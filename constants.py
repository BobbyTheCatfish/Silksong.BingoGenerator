#file paths and names
from discord.app_commands import Choice
from enum import Enum


ASSETS_PATH = "assets"
COMPUTED_SUBDIR = "generated"
GOALS_FILENAME = "silksong-v6.json"
CAT_FILENAME = "categorized_v3.json"
GOALSET_VER = "3.0"
DEFAULT_PASSPHRASE = "fast"

ROOM_NAMES = [
    "Abyssopelagic Zone",
    "Rose Garden",
    "Not a Human Hand",
    "Almost a Tundra",
    "Sentient Blobs",
    "Bing of the Hill with Multiverse Time Travel",
    "Skongin It",
    "Fa Ri Du La Ci Ma Ne",
    "POSHANKA",
    "Savage Beastfly",
    "Choral Chambers",
    "Wispfire Lantern",
    "OOSHKA NEEPLY",
    "Neepless",
    "Flea Route",
    "Cloakless",
    "Double Shanka",
    "Quad Shanka",
    "Looks to the Moon",
    "Silkshot Weaver",
    "Weavenest Absolom",
    "Yuri Stay Winning",
    "Daves Shard",
    "Start on Bind",
    "Bilewater Hidden Bench",
    "Running for Rosaries",
    "Fourth Chorus Skip Skip",
    "Hoker RNG",
    "Crustnut Powder",
    "Shaw and Other Things to Yell at Your Enemies",
    "Silk and Possibly Song",
    "Lacenet",
    "Architect Crest",
    "Bingy Bingus Bongus Blafoingus",
    "Beast Boost Uppie Strike",
    "Silkeater Noclip",
    "Archies Mossberry",
    "Key Route",
    "Silver Bells Loop",
    "Shawtoof",
    "Hang_08",
    "Lets Go Gambling",
    "Cog_08",
    "Dust_Maze_07",
    "Failure",
    "Triple GMS",
    "Early Second Skarrguard",
    "Proper Substance Use",
    "Mrs Streamer",
    "I Suggest Forcefem",
    "Toxic Yuri Wins Again",
    "Zango Becomes Blueful",
    "Forcefemmed",
    "Sometimes Its Not Our Turn to Talk",
    "Fourth Chorus Skip Skip Skip",
    "Fourth Chorus Skip Skip Skip Skip",
    "Nyaaaaaa",
    "Pimpogos",
    "Save Me From Act 1",
    "Moss Grotto Reset",
    "I Need Shards For My Compass",
    "Debug Hotkey Check",
    "Hornt",
    "1999",
    "Krattball",
    "Webbed Bouce",
    "Skimaaaanama",
    "Heavy Brosary Necklace",
    "Lunaberry",
    "Cogwork Canyon",
    "15 Minutes and a Coffee",
    "Hornts in Boards",
    "BS2 is BS",
    "Canonically Plural Hornet",
    "V bbbbbbbbbbbbb      vv v    b bb",
    "Spill Issue"
]

MIO_ROOM_NAMES = [
    #"Abyssopelagic Zone",
    #"Misty Morning",
    #"Almost a Tundra",
    #"Sentient Blobs",
    #"Bing of the Hill with Multiverse Time Travel",
    #"Gliese Catalog",
    #"Looks to the Moon",
    #"Silkshot Weaver",
    #"Weavenest Absolom",
    #"Yuri Stay Winning",
    #"Bingy Bingus Bongus Blafoingus",
    #"Lets Go Gambling",
    #"Failure",
    #"Proper Substance Use",
    #"Mrs Streamer",
    #"I Suggest Forcefem",
    #"Toxic Yuri Wins Again",
    #"Forcefemmed",
    #"Sometimes Its Not Our Turn to Talk",
    #"Nyaaaaaa",
    #"Debug Hotkey Check",
    #"1999",
    #"Webbed Bouce",
    #"Lunaberry",
    #"Cogwork Canyon",
    #"15 Minutes and a Coffee",
    "V bbbbbbbbbbbbb      vv v    b bb",
    "Flower Warp",
    "Washing Machine",
    "Defective Core",
    "Stargazing",
    "Crash the Vessel",
    "Mel is the Hand's Keeper",
    "Samsk is the Hand's Keeper",
    "Rad is the Hand's Keeper",
    "Skitter Like a Buge",
    "Finding Samsk",
    "Toumtoum",
    "Above the Suns",
    "FRIENDS :)",
    "Sixth Tremor",
    "Coating Components",
    "Wildcat",
    "Halyn's Experiment #67",
    "Spill Issue",
    "Very Dangerous Red Plants",
    "Where You Come to Die",
    "Shairpin Crits",
    "Ember's Lost Boot",
    "Target Practice Plushie",
    "Nacre Drought",
    "The Eye's Favorite",
    "<REDACTED>",
    "Weave, Thread, Cut",
    "Bulnosaur",
    "A Rat in the Vessel",
    "The Wheel",
    "For Each Voice, a Keeper",
    "For Each Keeper, a Voice",
    "You Know She Ate a Cheese",
    "Save the Heart",
    "Black Egg Library",
    "Two Betrayals",
    "You're Forgiven Now",
    "Little Sapling",
    "The Other Side",
    "Strider Dash",
    "Orbular Ati",
    "Mio Upskirt View",
    "Tomo's Office"
]

TEAM_NAMES = [
    "Red Tools",
    "Blue Tools",
    "Yellow Tools",
    "Atla",
    "Cindril",
    "Karn",
    "Murglin",
    "Absolom",
    "Karmelita",
    "Clover",
    "Nyleth",
    "Pebb",
    "Forge Daughter",
    "Jubilana",
    "Twelfth Architect",
    "Silkspear",
    "Threadstorm",
    "Sharpdart",
    "Crosstitch",
    "Rune Rage",
    "Pale Nails",
    "Beastlings",
    "plasmium", #caravan teams
    "sherma",
    "gilly",
    "vespa",
    "magnetite",
    "huntress",
    "scrounge",
    "beastling",
    "Hornt", #silly starts
    "Soul",
    "Silk",
    "Darkness",
    "Yuri",
    "Yaoi"
]


class SSProgression:
    Early = "early"
    Dash = "dash"
    Cloak = "cloak"
    ClingGrip = "walljump"
    Widow = "widow"
    Act2 = "act2"
    Clawline = "clawline"
    Faydown = "faydown"
    Act3 = "act3"
    SilkSoar = "silksoar"


class MioProgression:
    Early = "early"
    Hairpin = "hairpin"
    OneSkill = "1skill"
    Vaults = "vaults"
    Endgame = "endgame"


class Tags:
    Blocking = "blocking"
    NoLockout = "nolockout"
    Lockout = "lockout"
    Silly = "silly"
    ItemSync = "itemsync"
    Hard = "hard"
    Craft = "craft"
    Flea = "flea"
    Expensive = "expensive"
    NoForcing = "noforcing"
    Missable = "missable"
    HardSave = "hardsave"
    Melody = "melody"
    Key = "key"
    Tool = "tool"
    Quest = "quest"
    Locket = "locket"
    Upgrade = "upgrade"
    Fight = "fight"
    NPC = "npc"
    Location = "location"
    Collection = "collection"
    Relic = "relic"


class Skips:
    ToolPogo = "toolpogo"
    BeastBoost = "beastboost"
    AirStall = "airstall"
    EnemyPogo = "enemypogo"
    


def attributes_to_choices_list(options: type) -> list[Choice[str]]:
    choices: list[Choice[str]] = []

    for key, option in options.__dict__.items():
        if isinstance(option, str) and not key.startswith("__"):
            choices.append(Choice(name=option, value=option))

    return choices


class BoardSizes:
    Standard = 5
    Caravan = 6


class GameNames(Enum):
    Silksong = "silksong"
    Mio = "mio"


class SilkProgOpts:
    Act1Only = "Act 1 Only"
    NoClawline = "No Clawline"
    NoFaydown = "No Faydown (Default)"
    FullAct2 = "Full Act 2"
    Act3 = "Act 3 No Silk Soar"
    FullAct3 = "Full Act 3"
    Easy = "Easier Mode"
    OnlyAct2 = "Act 2 Only"

    @classmethod
    def get_options(cls) -> list[Choice[str]]:
        return attributes_to_choices_list(cls)

    
class MioProgOpts:
    NoCrucible = "No Crucible (Default)"
    NoVaults = "No Vaults"

    @classmethod
    def get_options(cls) -> list[Choice[str]]:
        return attributes_to_choices_list(cls)


class GameTypes(Enum):
    # Values used in API calls
    GetToTheOtherSide = "GTTOS10"
    Caravan = "Bingo6"
    NonLockout = "Non-Lockout"

    # Used for board type options
    Rando = "Rando"
    Pattern = "Pattern"

    Bingo = "Bingo"
    NoForcing = "NoForcing"