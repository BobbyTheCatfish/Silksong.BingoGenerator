import requests, random
from time import sleep
from websockets.sync.client import connect
import json

from constants import DEFAULT_PASSPHRASE, ROOM_NAMES, MIO_ROOM_NAMES, TEAM_NAMES, GameNames, GameTypes

TEAM_COLORS = [
    "#237e3d",
    "#c32a45",
    "#0d48b5",
    "#ddc700",
    "#cd560b",
    "#f5c06c",
    "#80c786",
    "#75b4d8",
    "#481572"
]

STANDARD_PAYLOAD = {
    "game_type": 18, #custom game
    "variant_type": 18, #custom game, both are required
    #The following can be adjusted on a case-by-case basis
    "seed": "",
    "hide_card" : 1,
    "custom_json" : None,
    "lockout_mode" : 1 #1 is no lockout
}

NEW_CARD_PAYLOAD = STANDARD_PAYLOAD.copy()
NEW_CARD_PAYLOAD.update({
    "nickname" : "Bingyflea",
    #update pretty much all of these
    "room_name" : "",
    "passphrase" : "fast"
})

def get_room_name(game: GameNames) -> str:
    """
    Gets a room name for a game
    """
    if game == GameNames.Mio:
        return random.choice(MIO_ROOM_NAMES)
    else:
        return random.choice(ROOM_NAMES)


class BingosyncClient:
    """
    Opens a bingosync session with the correct csrf cookies!! Very exciting.
    Implements api methods for bingosync as well probably.
    """
    bingosync = True
    roomId = None
    _base_url = "https://bingosync.com"
    _hostname = "bingosync.com"

    def __init__(self):
        self.bingosync = True
        self.session = requests.Session()

        #Using a session automatically persists cookies!
        #set user-agent header:
        self.session.headers.update({
            "User-Agent" : "Silksong.Bingogenerator/0.1",
            "Origin": self._base_url + "/",
            "Host": self._hostname,
        })

        #Make a request to get them cookies
        r = self.session.get(self._base_url)
        if r.status_code > 499: #server error
            if self.bingosync:
                raise ConnectionError("Bingosync server error. Try Caravan (6x6) or byngosink (5x5, 6x6).")
            else:
                raise ConnectionError("Caravan server error. Try Bingosync (5x5) or byngosink (5x5, 6x6).")

        self.csrf_token = self.session.cookies["csrftoken"]


    def new_room(self, board_json: str,
                 hide_card=True, lockout=False, room_name=None,
                 passphrase=DEFAULT_PASSPHRASE, seed ="", game=GameNames.Silksong):
        """
        Opens a new room and sets the instance roomId.
        """
        form_data = NEW_CARD_PAYLOAD.copy()

        # Update the room settings
        form_data.update({
            "hide_card" : 1 if hide_card else 0,
            "lockout_mode" : 2 if lockout else 1,
            "custom_json" : board_json,
            "passphrase" : passphrase,
            "seed": seed
        })

        # Get a name for the room
        if room_name is None:
            room_name = get_room_name(game)

        form_data["room_name"] = room_name
        form_data["csrfmiddlewaretoken"] = [self.csrf_token, self.csrf_token]

        # Send the request
        response = self.session.post(self._base_url, data=form_data, allow_redirects=False)
        if response.status_code == 302: #expected
            #save the room ID and then disconnect from it
            self.roomId = response.headers["location"].split("/")[2]
            self.session.get(f"{self._base_url}/room/{self.roomId}/disconnect")
            self.session.get(f"{self._base_url}")

        return form_data["room_name"], f"{self._base_url}/room/{self.roomId}"


    def update_card(self, room_id: str, board_json: str,
                    hide_card=True, lockout = False, seed =""):
        """
        Updates a room's card with a new board.
        """
        form_data = STANDARD_PAYLOAD.copy()

        #need to update the following
        form_data.update({
            "room": room_id,
            "hide_card" : 1 if hide_card else 0,
            "lockout_mode" : 2 if lockout else 1,
            "custom_json" : board_json,
            "seed": seed
        })

        form_data["csrfmiddlewaretoken"] = [self.csrf_token, self.csrf_token]
        response = self.session.post(f"{self._base_url}/api/new-card", data=form_data)
        return response


    def close(self):
        """
        Closes the session.
        """
        self.session.close()


class CaravanClient(BingosyncClient):
    bingosync = False
    _base_url = "https://caravan.kobold60.com"
    _hostname = "caravan.kobold60.com"


class ByngosinkClient: #completely different format.
    def __init__(self) -> None:
        self.socketAddress = "wss://byngosink-ws.manicjamie.com:555/"
        #self.socketAddress = "ws://localhost:555/"
        self.baseURL = "https://byngosink.manicjamie.com/board.html?id="

    def new_fixed_room(self, board_list: list, game_type: GameTypes, room_name: str | None=None,
                       game_name=GameNames.Silksong, players=0):
        """
        Opens a new room with fixed board and sets the instance roomId.
        """ 
        if room_name is None:
            room_name = get_room_name(game_name)

        payload = {
            "verb":"OPEN_FIXED",
            "roomName": room_name,
            "game": game_name,
            "generator": "Fixed",
            "board": game_type.value,
            "goals": board_list
        }

        with connect(self.socketAddress) as socket:
            socket.send(json.dumps(payload))
            response = json.loads(socket.recv(10))
            room_id = response["roomId"]
            room_url = self.baseURL+room_id

            if players > 0:
                #join bingyflea to make teams and then leave
                socket.send(json.dumps({"verb": "JOIN",
                                        "roomId": room_id,
                                        "username": "Bingyflea"}))

                r2 = json.loads(socket.recv(10))
                user_id = r2["userId"]

                names, colors = (random.sample(TEAM_NAMES, k=players), random.sample(TEAM_COLORS, k=players))
                for i in range(players):
                    socket.send(json.dumps({"verb": "CREATE_TEAM",
                                            "roomId": room_id,
                                            "name": names[i],
                                            "colour": colors[i]}))
                    _ = socket.recv(10)
                    sleep(0.2)

                socket.send(json.dumps({"verb": "LEAVE_TEAM",
                                        "roomId": room_id}))
                _ = socket.recv(10) 
                sleep(0.2)
                socket.send(json.dumps({"verb": "EXIT",
                                        "userId": user_id,
                                        "roomId": room_id}))
                _ = socket.recv(10)
                sleep(0.2)

        return room_name, room_url


if __name__ == "__main__":
    c = ByngosinkClient()
    board = ["Beast's Crest", "Vintage Nectar", "Cogwork Core Mask Shard", "Deep Docks Fleas [3]", "Blasted Steps Mask Shard", "Slab Mask Shard", "5 Red Tools", "3 Gather Quests", "Talk to Loam", "Crustnut", "Talk to Shakra in Bilewater", "High Halls Spool Fragment", "1 Crafting Kit", "Obtain 3 Beast Shards", "Meet Caravan at the Grand Gate [12]", "Obtain 5 Craftmetal", "Apostate Key", "Pimpillo & Voltvessels", "Skull Tyrant", "2 Wayfarer Quests", "Conductor's Melody", "Rosary Cannon", "Voltvyrm", "Buy From Grindle (No String)", "Moorwing", "Flintslate", "Witch Crest", "Sands of Karak Flea [1]", "2 Extra Masks", "Mt. Fay Mask Shard", "Defeat a Covetous Pilgrim", "Obtain 5 Memory Lockets", "Deep Docks Spool Fragments (2)", "Disgraced Chef Lugoli", "Pale Lake Craftmetal", "Talk to Styx & Huntress"]
    _, rId = c.new_fixed_room(board, game_type=GameTypes.Caravan, players=5)
    print(rId)
