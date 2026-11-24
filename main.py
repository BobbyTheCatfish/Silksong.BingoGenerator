import discord, os, json, network, random
from discord import Member, app_commands
from typing import Optional
from board import CaravanGenerator, ByngosinkGenerator, DraftoutGenerator
from datetime import datetime, timedelta

from constants import DEFAULT_PASSPHRASE, BoardSizes, GameNames, GameTypes, SSProgression, Tags, MioProgression, SilkProgOpts, MioProgOpts

CONFIG_PATH = os.path.join("config","settings.dat")

ERROR_MESSAGE_UNKNOWN_SIZE = "Unable to generate room. Unknown board size of '%i'"
PRESET_DESCRIPTION = "Max progression for goals on the board."
PASSWORD_DESCRIPTION = f"Password for the room. Defaults to '{DEFAULT_PASSPHRASE}'."
SIZE_DESCRIPTION = "The board size"

DEF_TAGLIMITS = {
    Tags.Craft : 3,
    Tags.Flea : 5,
    Tags.Expensive : 2
}

SILKSONG_MAIN = "categorized_v3.json"

def config():
    if not os.path.exists(os.path.dirname(CONFIG_PATH)):
        os.makedirs(os.path.dirname(CONFIG_PATH))

    if not os.path.exists(CONFIG_PATH):
        #generate default config
        config_dic = {
                "token" : "",
                "owners" : [
                    0000
                ],
                "command_servers" : [
                    0000
                ]
            }
        with open(CONFIG_PATH, "w") as config_file:
            json.dump(config_dic, config_file, indent=4)
            print("please fill in bot token and any bot admin discord ids to the new config.json file!")
            quit()
    else:
        with open(CONFIG_PATH) as config_file:
            return json.load(config_file)


class NewClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        

    async def setup_hook(self):
        for guild_id in config()["command_servers"]:
            try:
                guild = discord.Object(id=guild_id)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
            except:
                pass
        await self.tree.sync()


ints = discord.Intents.default()
ints.members = True
client = NewClient(intents = ints)

@client.event
async def on_ready():
    print(f"logged in as {client.user} to {len(client.guilds)} servers")


@client.tree.error
async def on_app_command_error(interaction, error):
    try:
        await interaction.response.send_message(str(error), ephemeral=True)
    except:
        await interaction.followup.send(str(error), ephemeral=True)
    raise error


def silk_prog_options() -> list[app_commands.Choice[str]]:
    return SilkProgOpts.get_options()


def mio_prog_options() -> list[app_commands.Choice[str]]:
    return MioProgOpts.get_options()


def size_options() -> list[app_commands.Choice[int]]:
    return [app_commands.Choice(name="Standard (5x5)", value=BoardSizes.Standard),
            app_commands.Choice(name="Caravan (6x6)", value=BoardSizes.Caravan)]


def ping_role_options() -> list[app_commands.Choice[str]]:
    return [app_commands.Choice(name="Boop for Bing", value="1494131607118811257"),
            app_commands.Choice(name="Ring for Rando", value="1538693410964381716")]


def board_type_options() -> list[app_commands.Choice[str]]:
    return [app_commands.Choice(name=GameTypes.Rando.value, value=GameTypes.Rando.value),
            app_commands.Choice(name=GameTypes.Pattern.value, value=GameTypes.Pattern.value)]
    # options = BoardTypes.get_options()
    # return [app_commands.Choice(name=opt, value=opt) for opt in options]


def silk_prog_string_to_tags(progression: app_commands.Choice[str] | None) -> list[str]:
    """
    Converts a progression input string to tags for Silksong
    """
    if progression is None or progression.value == SilkProgOpts.NoFaydown:
        no_tags = [SSProgression.Faydown,
                   SSProgression.Act3,
                   SSProgression.SilkSoar]
    elif progression.value == SilkProgOpts.Act1Only:
        no_tags = [SSProgression.Act2,
                   SSProgression.Clawline,
                   SSProgression.Faydown,
                   SSProgression.Act3,
                   SSProgression.SilkSoar]
    elif progression.value == SilkProgOpts.NoClawline:
        no_tags = [SSProgression.Clawline,
                   SSProgression.Faydown,
                   SSProgression.Act3,
                   SSProgression.SilkSoar]
    elif progression.value == SilkProgOpts.FullAct2:
        no_tags = [SSProgression.Act3,
                   SSProgression.SilkSoar]
    elif progression.value == SilkProgOpts.Act3:
        no_tags = [SSProgression.SilkSoar]
    elif progression.value == SilkProgOpts.FullAct3:
        no_tags = []
    elif progression.value == SilkProgOpts.Easy:
        no_tags = [Tags.Hard,
                   SSProgression.Faydown,
                   SSProgression.Act3,
                   SSProgression.SilkSoar]
    elif progression.value == SilkProgOpts.OnlyAct2:
        no_tags = [SSProgression.Early,
                   SSProgression.Dash,
                   SSProgression.Cloak,
                   SSProgression.ClingGrip,
                   SSProgression.Widow,
                   SSProgression.Act3,
                   SSProgression.SilkSoar]
    else:
        no_tags = []

    return no_tags


def mio_prog_string_to_tags(progression: app_commands.Choice[str] | None) -> list[str]:
    """
    Converts a progression input string to tags for Mio
    """
    if progression is None or progression.value == MioProgOpts.NoCrucible:
        no_tags = []
    elif progression.value == MioProgOpts.NoVaults:
        no_tags = [MioProgression.Endgame, MioProgression.Vaults]
    else:
        no_tags = []
    return no_tags


def silk_board_type_to_params(board_type: app_commands.Choice[str] | None) -> tuple[str, GameTypes]:
    """Returns (filename, GameTypes) tuple."""
    if board_type is None:
        return SILKSONG_MAIN, GameTypes.Bingo
    elif board_type.value.strip().lower() == GameTypes.Rando.value.lower():
        return "silksong_rando.json", GameTypes.Rando
    elif board_type.value.strip().lower() == GameTypes.Pattern.value.lower():
        return SILKSONG_MAIN, GameTypes.Pattern
    else:
        return SILKSONG_MAIN, GameTypes.Bingo


def get_board_size(size: Optional[app_commands.Choice[int]]):
    if size is None:
        return BoardSizes.Standard
    else:
        return size.value


@client.tree.command()
@app_commands.describe(preset=PRESET_DESCRIPTION)
@app_commands.describe(size=SIZE_DESCRIPTION)
@app_commands.choices(preset=silk_prog_options())
@app_commands.choices(size=size_options())
@app_commands.choices(type=board_type_options())
async def newboard(interaction: discord.Interaction, lockout: bool = False, 
                   preset: Optional[app_commands.Choice[str]] = None, 
                   size: Optional[app_commands.Choice[int]]=None,
                   type: Optional[app_commands.Choice[str]]=None):
    """Generates a new board JSON for bingo."""

    filename, game_type = silk_board_type_to_params(type)
    print(game_type)

    no_tags = silk_prog_string_to_tags(preset)
    board_size = get_board_size(size)
        
    this_board = CaravanGenerator(filename, board_size, no_tags=no_tags, game_type=game_type,
                                 tag_limits=DEF_TAGLIMITS.copy(), lockout=lockout).export()

    await interaction.response.send_message(json.dumps(this_board), ephemeral=True)

@client.tree.command()
@app_commands.describe(preset=PRESET_DESCRIPTION)
@app_commands.choices(preset=silk_prog_options())
async def otherside(interaction: discord.Interaction,
                    preset: Optional[app_commands.Choice[str]] = None,
                    players: int = 0):
    """Generates a new board for byngosink's Get to the Other Side mode. Needs 100 goals!"""
    await interaction.response.defer(thinking=True)

    no_tags = silk_prog_string_to_tags(preset)
    this_board = ByngosinkGenerator(SILKSONG_MAIN, 10, no_tags=no_tags,
                                   game_type=GameTypes.GetToTheOtherSide).export()

    session = network.ByngosinkClient()
    room_name, room_url = session.new_fixed_room(this_board, GameTypes.GetToTheOtherSide, game_name=GameNames.Silksong, players=players)

    await interaction.followup.send(f"Room: {room_name} created at {room_url}")

@client.tree.command()
@app_commands.describe(preset=PRESET_DESCRIPTION)
@app_commands.describe(size=SIZE_DESCRIPTION)
@app_commands.choices(preset=silk_prog_options())
@app_commands.choices(size=size_options())
# @app_commands.describe(size="The side length of the board. Default: 5")
async def rosingy(interaction: discord.Interaction, preset: Optional[app_commands.Choice[str]] = None, size: Optional[app_commands.Choice[int]]=None):
    """Generates a new rosingy board. EXPERIMENTAL."""
    no_tags = silk_prog_string_to_tags(preset)

    board_size = get_board_size(size)
    
    if board_size == BoardSizes.Standard:
        session = network.BingosyncClient()
    elif board_size == BoardSizes.Caravan:
        session = network.CaravanClient()
    else:
        await interaction.response.send_message(ERROR_MESSAGE_UNKNOWN_SIZE % board_size)
        return
    
    this_board = CaravanGenerator("rosingy.json", board_size, no_tags=no_tags, tag_limits=DEF_TAGLIMITS.copy()).export()
    name, room_link = session.new_room(json.dumps(this_board), lockout=False)

    await interaction.response.send_message(f"Room: {name} created at {room_link}")


@client.tree.command()
@app_commands.describe(preset=PRESET_DESCRIPTION)
@app_commands.describe(size=SIZE_DESCRIPTION)
@app_commands.choices(preset=silk_prog_options())
@app_commands.choices(size=size_options())
@app_commands.choices(type=board_type_options())
@app_commands.describe(players="Number of teams to create. Don't fill out to create your own teams.")
async def byngosink(interaction: discord.Interaction, type: Optional[app_commands.Choice[str]] = None, preset: Optional[app_commands.Choice[str]] = None, 
                  players: int = 0,  size: Optional[app_commands.Choice[int]] = None):
    """Generates a new board and creates a byngosink room."""
    await interaction.response.defer(thinking=True)

    filename, game_type = silk_board_type_to_params(type)

    board_size = get_board_size(size)
    no_tags = silk_prog_string_to_tags(preset)
    
    this_board = ByngosinkGenerator(filename, board_size, no_tags=no_tags,
                                   game_type=game_type, tag_limits=DEF_TAGLIMITS.copy()).export()
    
    session = network.ByngosinkClient()
    board_type = GameTypes.NonLockout if board_size == BoardSizes.Standard else GameTypes.Caravan

    n, room_link = session.new_fixed_room(this_board, board_type, game_name=GameNames.Silksong, players=players)
    await interaction.followup.send(f"Room: {n} created at {room_link}")


@client.tree.command()
@app_commands.describe(preset=PRESET_DESCRIPTION)
@app_commands.describe(password=PASSWORD_DESCRIPTION)
@app_commands.choices(preset=silk_prog_options())
@app_commands.choices(type=board_type_options())
async def bingosync(interaction: discord.Interaction, lockout: bool = False, type: Optional[app_commands.Choice[str]] = None,
                       preset: Optional[app_commands.Choice[str]] = None, password: str = "fast"):
    """Generates a new 5x5 board and creates a bingosync room with "fast" as the default password."""
    await interaction.response.defer(thinking=True)

    filename, game_type = silk_board_type_to_params(type)

    no_tags = silk_prog_string_to_tags(preset)

    this_board = CaravanGenerator(filename, BoardSizes.Standard, no_tags=no_tags, tag_limits=DEF_TAGLIMITS.copy(),
                                 game_type=game_type, lockout=lockout).export()
    bs_session = network.BingosyncClient()
    room_name, room_link = bs_session.new_room(json.dumps(this_board), lockout=lockout, passphrase=password)
    bs_session.close()
    await interaction.followup.send(f"Room: {room_name} created at {room_link}")


@client.tree.command()
@app_commands.describe(preset=PRESET_DESCRIPTION)
@app_commands.describe(password=PASSWORD_DESCRIPTION)
@app_commands.choices(preset=silk_prog_options())
@app_commands.choices(type=board_type_options())
async def caravan(interaction: discord.Interaction, lockout: bool = False, type: Optional[app_commands.Choice[str]] = None, 
                     preset: Optional[app_commands.Choice[str]] = None, password: str = DEFAULT_PASSPHRASE):
    """Generates a new 6x6 board and creates a caravan room with "fast" as the default password."""
    await interaction.response.defer(thinking=True)

    filename, game_type = silk_board_type_to_params(type)

    no_tags = silk_prog_string_to_tags(preset)

    this_board = CaravanGenerator(filename, BoardSizes.Caravan, no_tags=no_tags, tag_limits=DEF_TAGLIMITS.copy(),
                                 game_type=game_type, lockout=lockout).export()
    bs_session = network.CaravanClient()
    room_name, room_link = bs_session.new_room(json.dumps(this_board), lockout=lockout, passphrase=password)
    bs_session.close()
    await interaction.followup.send(f"Room: {room_name} created at {room_link}")


@client.tree.command()
@app_commands.describe(size=SIZE_DESCRIPTION)
@app_commands.choices(size=size_options())
async def doublingy(interaction: discord.Interaction, size: Optional[app_commands.Choice[int]]=None):
    """Generates a pair of doublingy rooms."""
    await interaction.response.defer(thinking=True)

    # Determine the board size
    board_size = get_board_size(size)

    # Grab the correct session for the board size
    if board_size == BoardSizes.Standard:
        session = network.BingosyncClient()
    elif board_size == BoardSizes.Caravan:
        session = network.CaravanClient()
    else:
        await interaction.followup.send(ERROR_MESSAGE_UNKNOWN_SIZE % board_size)
        return

    # Create two boards, one for act 1 only, and one for act 2 only
    act1_tags = [SSProgression.Act2,
                 SSProgression.Clawline,
                 SSProgression.Faydown,
                 SSProgression.Act3,
                 SSProgression.SilkSoar]

    act2_tags = [SSProgression.Early,
                 SSProgression.Dash,
                 SSProgression.Cloak,
                 SSProgression.ClingGrip,
                 SSProgression.Widow,
                 SSProgression.Act3,
                 SSProgression.SilkSoar]

    act1_generator = CaravanGenerator(SILKSONG_MAIN, board_size, no_tags=act1_tags, tag_limits=DEF_TAGLIMITS.copy())
    act1_board = act1_generator.export()

    act2_generator = CaravanGenerator(SILKSONG_MAIN, board_size, no_tags=act2_tags, tag_limits=DEF_TAGLIMITS.copy())
    act2_generator.link_boards(act1_generator.goal_set.goals)
    act2_board = act2_generator.export()

    # Create the rooms
    room1_name, room1_link = session.new_room(json.dumps(act1_board), lockout=False)
    room2_name, room2_link = session.new_room(json.dumps(act2_board), lockout=False)
    session.close()

    await interaction.followup.send(f"Act 1 room: {room1_name} at {room1_link}\nAct 2 room: {room2_name} at {room2_link}")

    
@client.tree.command()
@app_commands.describe(size=SIZE_DESCRIPTION)
@app_commands.choices(size=size_options())
async def triplingy(interaction: discord.Interaction, size: Optional[app_commands.Choice[int]]=None):
    """Generates a set of triplingy rooms."""
    await interaction.response.defer(thinking=True)

    board_size = get_board_size(size)

    if board_size == BoardSizes.Standard:
        session = network.BingosyncClient()
    elif board_size == BoardSizes.Caravan:
        session = network.CaravanClient()
    else:
        await interaction.followup.send(ERROR_MESSAGE_UNKNOWN_SIZE % board_size)
        return

    # Create three boards, one for each act
    act1_tags = [SSProgression.Act2,
                 SSProgression.Clawline,
                 SSProgression.Faydown,
                 SSProgression.Act3,
                 SSProgression.SilkSoar]

    act2_tags = [SSProgression.Early,
                 SSProgression.Dash,
                 SSProgression.Cloak,
                 SSProgression.ClingGrip,
                 SSProgression.Widow,
                 SSProgression.Act3,
                 SSProgression.SilkSoar]

    act3_tags = [SSProgression.Early,
                 SSProgression.Dash,
                 SSProgression.Cloak,
                 SSProgression.ClingGrip,
                 SSProgression.Widow,
                 SSProgression.Act2,
                 SSProgression.Clawline,
                 SSProgression.Faydown]

    act1_board = CaravanGenerator(SILKSONG_MAIN, board_size, no_tags=act1_tags, tag_limits=DEF_TAGLIMITS.copy())
    act2_generator = CaravanGenerator(SILKSONG_MAIN, board_size, no_tags=act2_tags, tag_limits=DEF_TAGLIMITS.copy())
    act2_generator.link_boards(act1_board.goal_set.goals)
    act2_board   = act2_generator.export()
    act3_generator = CaravanGenerator(SILKSONG_MAIN, BoardSizes.Standard, no_tags=act3_tags, tag_limits=DEF_TAGLIMITS.copy())
    act3_generator.link_boards(act1_board.goal_set.goals)
    act3_generator.link_boards(act2_generator.goal_set.goals)
    act3_board = act3_generator.export()

    n1, room1_link = session.new_room(json.dumps(act1_board.export()), lockout=False)
    n2, room2_link = session.new_room(json.dumps(act2_board), lockout=False)

    if board_size == BoardSizes.Caravan: #swap back to bingosync # note: why? we gonna explain this?
        session.close()
        session = network.BingosyncClient()
    n3, room3_link = session.new_room(json.dumps(act3_board), lockout=False)

    session.close()
    await interaction.followup.send(f"Act 1 room: {n1} at {room1_link}\nAct 2 room: {n2} at {room2_link}\nAct 3 room: {n3} at {room3_link}")


@client.tree.command()
@app_commands.describe(preset=PRESET_DESCRIPTION)
@app_commands.describe(size=SIZE_DESCRIPTION)
@app_commands.choices(size=size_options())
@app_commands.choices(preset=mio_prog_options())
async def miobingo(interaction: discord.Interaction, preset: Optional[app_commands.Choice[str]]=None, size: Optional[app_commands.Choice[int]]=None):
    """All-in-one command for Mio Bingo. Password is 'fast'."""
    await interaction.response.defer(thinking=True)

    board_size = get_board_size(size)

    if board_size == BoardSizes.Standard:
        session = network.BingosyncClient()
    elif board_size == BoardSizes.Caravan:
        session = network.CaravanClient()
    else:
        await interaction.followup.send(ERROR_MESSAGE_UNKNOWN_SIZE % board_size)
        return False

    no_tags = mio_prog_string_to_tags(preset)

    this_board = CaravanGenerator("mio.json", board_size, no_tags=no_tags, game_name=GameNames.Mio).export()
    room_name, room_link = session.new_room(json.dumps(this_board), game=GameNames.Mio)
    session.close()

    await interaction.followup.send(f"Room: {room_name} created at {room_link} with password 'fast'.")
    return True


@client.tree.command()
@app_commands.describe(start_time="The starting time, following the format of HH:MM:SS")
@app_commands.describe(end_time="The ending time, following the format of HH:MM:SS")
async def time(interaction: discord.Interaction, start_time: str, end_time: str):
    """Calculates the run time for a bingo session"""

    # Parse the time to a datetime
    try:
        time_format = "%H:%M:%S"
        parsed_start = datetime.strptime(start_time, time_format)
        parsed_end = datetime.strptime(end_time, time_format)
    except ValueError as err:
        print(err)
        await interaction.response.send_message("Times must be in the format of HH:MM:SS", ephemeral=True)
        return

    # The start time must always be before the end time.
    # If it's not, then the end time is on the next day
    if parsed_end < parsed_start:
        parsed_end += timedelta(days=1)

    time_difference_seconds = (parsed_end - parsed_start).seconds

    # Calculate h:m:s format from the seconds
    hours, remainder = divmod(time_difference_seconds, 60 * 60)
    minutes, seconds = divmod(remainder, 60)

    final_time_str = f"{hours}h {minutes}m {seconds}s"
    await interaction.response.send_message(f"The calculated time is: `{final_time_str}`", ephemeral=True)

class DrafoutUI(discord.ui.View):
    def __init__(self, no_tags, size: int, player1: discord.User, player2: discord.User, parent_interaction: discord.Interaction):
        super().__init__(timeout=1800) #30 minutes
        self.generator = DraftoutGenerator(no_tags, size)
        self.p1 = player1
        self.p2 = player2
        self.totalSize = size**2
        self.active = self.p1
        self.color = int(discord.Colour.from_str(random.choice(network.TEAM_COLORS)))
        self.name = random.choice(network.ROOM_NAMES)
        self.currentOptions = self.generator.show_goals()
        self.parentInteract = parent_interaction
        self.init = False
        self.message = None

    def swapPlayer(self):
        if self.active == self.p1:
            self.active = self.p2
        else:
            self.active = self.p1

    @discord.ui.button(style=discord.ButtonStyle.blurple, label="Option 1")
    async def button1(self, interact : discord.Interaction, button: discord.ui.Button):
        if interact.user.id != self.active.id:
            await interact.response.send_message("It's not your turn!", ephemeral=True)
            return 

        if not self.init:
            self.init = True
            await interact.response.defer(ephemeral=True)
            await self.rebuildMessage()
            return
        
        await interact.response.defer(ephemeral=True)
        if self.generator.add_goal(self.currentOptions[0]): #nonzero until all goals picked YAY PYTHON
            self.currentOptions = self.generator.show_goals()
            self.swapPlayer()
            await self.rebuildMessage()
        else:
            await interact.followup.send("All goals picked! Please wait while I make a room.")
            await self.postRoom()

    @discord.ui.button(style=discord.ButtonStyle.blurple, label="Option 2")
    async def button2(self, interact : discord.Interaction, button : discord.ui.Button):
        if interact.user.id != self.active.id:
            await interact.response.send_message("It's not your turn!", ephemeral=True)
            return

        if not self.init:
            self.init = True
            await interact.response.defer(ephemeral=True)
            await self.rebuildMessage()
            return
        
        await interact.response.defer(ephemeral=True)
        if self.generator.add_goal(self.currentOptions[1]): #nonzero until all goals picked YAY PYTHON
            self.currentOptions = self.generator.show_goals()
            self.swapPlayer()
            await self.rebuildMessage()
        else:
            await interact.followup.send("All goals picked! Please wait while I make a room.")
            await self.postRoom()

    @discord.ui.button(style=discord.ButtonStyle.blurple, label="Option 3")
    async def button3(self, interact : discord.Interaction, button: discord.ui.Button):
        if interact.user.id != self.active.id:
            await interact.response.send_message("It's not your turn!", ephemeral=True)
            return 

        if not self.init:
            self.init = True
            await interact.response.defer(ephemeral=True)
            await self.rebuildMessage()
            return
        
        await interact.response.defer(ephemeral=True)
        if self.generator.add_goal(self.currentOptions[2]): #nonzero until all goals picked YAY PYTHON
            self.currentOptions = self.generator.show_goals()
            self.swapPlayer()
            await self.rebuildMessage()
        else:
            await interact.followup.send("All goals picked! Please wait while I make a room.")
            await self.postRoom()

    async def rebuildMessage(self):
        if self.message is None:
            temp = await self.parentInteract.original_response()
            self.message = await temp.fetch()

        goal_string = ""
        for goal in self.generator.getList():
            goal_string += goal["name"]+"\n"

        embed_dict = {
            "title" : self.name,
            "color" : self.color,
            "fields" : [
                    {
                        "name" : "Current goals:",
                        "value" : goal_string,
                        "inline" : False
                        },
                    {
                        "name" : "**Currently picking:**",
                        "value" : self.active.display_name,
                        "inline" : False
                    },
                    {
                        "name" : "Option 1",
                        "value" : self.currentOptions[0]["name"]
                    },
                    {
                        "name" : "Option 2",
                        "value" : self.currentOptions[1]["name"]
                    },
                    {
                        "name" : "Option 3",
                        "value" : self.currentOptions[2]["name"]
                    }
                ]
        }

        await self.message.edit(embed=discord.Embed.from_dict(embed_dict))

    async def postRoom(self):
        if self.totalSize == BoardSizes.Standard ** 2:
            session = network.BingosyncClient()
        elif self.totalSize == BoardSizes.Caravan ** 2:
            session = network.CaravanClient()
        else:
            await self.parentInteract.followup.send(ERROR_MESSAGE_UNKNOWN_SIZE % self.totalSize)
            return
        
        formatted_board = []
        for g in self.generator.getList():
            formatted_board.append({"name": g["name"]})
        random.shuffle(formatted_board)
        n, room_link = session.new_room(json.dumps(formatted_board), room_name=self.name)
        session.close()
        await self.parentInteract.followup.send(f"Room: {n} created at {room_link}")


@client.tree.command()
@app_commands.describe(preset=PRESET_DESCRIPTION)
@app_commands.describe(opponent="Ping your opponent here!")
@app_commands.choices(preset=silk_prog_options())
@app_commands.choices(size=size_options())
async def draftout(interaction: discord.Interaction, opponent:str, preset: Optional[app_commands.Choice[str]] = None, size: Optional[app_commands.Choice[int]]=None):
    """
    Draft goals into a lockout board.
    """
    opp = client.get_user(int(opponent.strip()[2:-1]))
    no_tags = silk_prog_string_to_tags(preset)

    board_size = get_board_size(size)
    await interaction.response.send_message("Click any button to start!", view=DrafoutUI(no_tags, board_size, interaction.user, opp, interaction))


@client.tree.command()
@app_commands.describe(hands="Comma-seperated list of names.")
@app_commands.describe(brains="Comma-seperated list of names.")
async def handbrainteams(interaction: discord.Interaction, hands: str, brains: str):
    """Splits hands and brains into teams."""
    hands_list = hands.split(",")
    random.shuffle(hands_list)

    brains_list = brains.split(",")
    random.shuffle(brains_list)

    teams = zip(hands_list, brains_list)
    out = "The teams are:\n"
    for hand, brain in teams:
        out += f"{hand.strip()}, {brain.strip()}\n"
    await interaction.response.send_message(out)

@client.tree.command()
@app_commands.describe(hands="Comma-seperated list of names.")
@app_commands.describe(artists="Comma-seperated list of names.")
@app_commands.describe(interpreters="Comma-seperated list of names.")
async def pictionaryteams(interaction: discord.Interaction, hands: str, artists: str, interpreters: str):
    """Splits the players into pictionary teams."""
    hands_list = hands.split(",")
    random.shuffle(hands_list)

    brains_list = interpreters.split(",")
    random.shuffle(brains_list)

    art_list = artists.split(",")
    random.shuffle(art_list)

    teams = zip(hands_list, brains_list, art_list)
    out = "The teams are:\n"
    for hand, brain, art in teams:
        out += f"{hand.strip()}, {brain.strip()}, {art.strip()}\n"
    await interaction.response.send_message(out)

@client.tree.command()
@app_commands.describe(players="Comma-seperated list of names.")
@app_commands.describe(teamsize="Players per team")
async def teams(interaction: discord.Interaction, players: str, teamsize: int):
    """Splits players into teams."""
    player_list = players.split(",")
    random.shuffle(player_list)
    #check for sanity
    if len(player_list) % teamsize != 0:
        await interaction.response.send_message("That many players cannot be divided into teams of that size.", ephemeral=True)

    out = "The teams are:\n"
    for i in range(0, len(player_list), teamsize):
        team = player_list[i:i+teamsize]
        out += f"{team}\n"
    await interaction.response.send_message(out)

@client.tree.command()
@app_commands.choices(roleid=ping_role_options())
async def togglerole(interaction: discord.Interaction, roleid: app_commands.Choice[str]):
    """Adds (or removes) the Boop for Bing role."""
    try:
        if interaction.guild is None:
            await interaction.response.send_message("You need to run this command on the Silksong Bingo server.", ephemeral=True)
            return

        user: Member = interaction.user
        boop_roleid = int(roleid.value)
        boop_role = interaction.guild.get_role(boop_roleid)
        if boop_role not in user.roles:
            await user.add_roles(boop_role)
            await interaction.response.send_message("Role added!", ephemeral=True)
        else:
            await user.remove_roles(boop_role)
            await interaction.response.send_message("Role removed!", ephemeral=True)
    except:
        await interaction.response.send_message("You need to run this command on the Silksong Bingo server. If you did, then it broke.", ephemeral=True)


if __name__ == "__main__":
    client.run(config()["token"])