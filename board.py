from dataclasses import dataclass, field
import os, json, random

from constants import GameNames, GameTypes, SSProgression, MioProgression, Tags

#file paths and names
ASSETS_PATH = "assets"
COMPUTED_SUBDIR = "generated"
GOALS_FILENAME = "silksong-v6.json"
CAT_FILENAME = "categorized_v3.json"
GOALSET_VER = "3.0"

#Lockout.live formatting
BOARD_TYPES = [
    SSProgression.Cloak,
    SSProgression.ClingGrip,
    SSProgression.Act2,
    SSProgression.Dash,
    SSProgression.Early,
    SSProgression.Clawline,

    SSProgression.Faydown,
    Tags.Craft,
    Tags.HardSave,
    Tags.Melody,
    Tags.Flea,
    Tags.Key,
    Tags.Tool,
    Tags.Expensive,
    SSProgression.Act3,
    SSProgression.SilkSoar
]

LL_PROGRESSION = {
    SSProgression.Early: "e",
    SSProgression.Dash: "e",
    SSProgression.Cloak: "e",
    SSProgression.ClingGrip : "m",
    SSProgression.Widow : "m",
    SSProgression.Act2 : "l",
    SSProgression.Clawline : "l",
    SSProgression.Faydown : "n"
}

LL_EXCLUDE = [SSProgression.Act3, SSProgression.SilkSoar, Tags.Silly, Tags.Missable, Tags.ItemSync]

LL_LIMITS = {
            "board" : {
                SSProgression.Early : 20,
                SSProgression.Dash  : 20,
                SSProgression.Cloak : 30,
                SSProgression.ClingGrip : 30,
                SSProgression.Act2 : 30,
                SSProgression.Clawline : 40,
                SSProgression.Faydown : 50,
                Tags.HardSave : 20,
                Tags.Craft : 40,
                Tags.Flea : 25,
                Tags.Key : 20,
                Tags.Tool : 30,
                Tags.Melody : 20,
                Tags.Expensive : 10
            },
            "line" : {
                Tags.Quest : 60,
                Tags.Locket : 60,
                Tags.Upgrade : 80,
                Tags.Fight : 60,
                Tags.NPC : 40,
                Tags.Location : 60,
                Tags.Collection : 60,
                Tags.Relic : 60
            }
        }

#Default excluded tags
DEF_NOTAGS = [Tags.Silly, Tags.ItemSync]

FOW_TYPES = [GameTypes.GetToTheOtherSide]

ordered_progs: dict[GameNames, list[str]] = {
    GameNames.Silksong: [
        SSProgression.Early,
        SSProgression.Dash,
        SSProgression.Cloak,
        SSProgression.ClingGrip,
        SSProgression.Widow,
        SSProgression.Act2,
        SSProgression.Clawline,
        SSProgression.Faydown,
        SSProgression.Act3,
        SSProgression.SilkSoar
    ],
    GameNames.Mio : [
        MioProgression.Early,
        MioProgression.Hairpin,
        MioProgression.OneSkill,
        MioProgression.Vaults
    ]
}


@dataclass
class Goal:
    name: str
    progression: list[str]
    types: list[str]
    weight: float = 1
    fow: str = ""
    rando: str = ""
    range: list[int] = field(default_factory=lambda: [])
    skip: dict[str, str] = field(default_factory=lambda: {})

    @property
    def fow_name(self) -> str:
        """
        The goal name for Fog of War boards
        """
        if self.fow != "":
            return self.fow

        return self.name

    @property
    def rando_name(self) -> str:
        """
        The goal name for randomizer boards
        """
        if self.rando == "":
            return self.name

        return random.choice([self.name, self.rando])

    @property
    def range_names(self) -> list[str]:
        """
        All goal names for ranges of items
        """
        return [self.name.replace("{{X}}", str(num)) for num in self.range]


@dataclass
class Exclusion:
    unique: list[str]
    limit: int | None = None
    pattern: bool = False


class GoalSet:
    goals: list[Goal]
    exclusions: list[Exclusion]

    def __init__(self, goals_filename: str):
        self.goals = []
        self.exclusions = []
        self.filename = goals_filename

        with open(os.path.join(ASSETS_PATH, goals_filename)) as f:
            goals_dict = json.load(f)

            unique_keys = set()
            def get_keys(d: dict, r = ""):
                for key, value in d.items():
                    fk = r + key
                    if fk not in unique_keys:
                        unique_keys.add(fk)

                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                get_keys(item, r + key + ".")
                    elif isinstance(value, dict):
                        get_keys(value, r + key + ".")

            get_keys(goals_dict)
            print("\n".join(unique_keys))


            for goal in goals_dict["goals"]:
                self.goals.append(Goal(**goal))

            for exclusion in goals_dict["exclusions"]:
                self.exclusions.append(Exclusion(**exclusion))

    def copy(self):
        return GoalSet(self.filename)

    def remove_goal(self, goal: Goal):
        if goal in self.goals:
            self.goals.remove(goal)

    def get_random_goal(self) -> Goal:
        return random.choices(self.goals, weights=[g.weight for g in self.goals])[0]


class Generator:
    """Base class for generators."""
    def __init__(
            self,
            goal_filename: str,
            size: int,
            no_tags: list[str] | None = None,
            tag_limits: dict[str, int] | None = None,
            game_name = GameNames.Silksong,
            game_type = GameTypes.Bingo,
            lockout = False):
        self.size = size
        self.no_tags = (no_tags or []).copy()

        self.no_tags += DEF_NOTAGS
        self.tag_limits = tag_limits

        if self.tag_limits is None:
            self.base_tag_limits = None
        else:
            self.tag_limits = self.tag_limits.copy()
            self.base_tag_limits = self.tag_limits.copy()

        if game_type is GameTypes.Pattern:
            self.no_tags.append(Tags.Blocking)

        self.game_name = game_name
        self.game_type = game_type
        self.lockout = lockout

        if self.lockout:
            self.no_tags.append(Tags.NoLockout)
        else:
            self.no_tags.append(Tags.Lockout)

        self.goal_set = GoalSet(goal_filename)
        self.filter_goals()

        self.base_set = self.goal_set.copy()


    def total_count(self):
        return self.size ** 2


    def force_indices(self):
        """
        Pick locations for goals which force max progression.
        Returns a list of indices.
        """
        m_size = self.size - 1

        # first pick two (zero indexed) squares on the diagonals. row, col
        diag_1 = random.randrange(self.size)
        diag_2 = random.randrange(self.size)

        # enforce different rows and columns
        while diag_2 == diag_1 or abs(diag_2 - m_size) == diag_1:
            diag_2 = random.randrange(self.size)

        # Create an ordered list of rows excluding the diagonals,
        # which are appended after generation
        rows = [row for row in range(self.size) if row not in [diag_1, diag_2]]
        rows.append(diag_1)
        rows.append(diag_2)

        # Create a randomized list of columns excluding the diagonals,
        # which are appended after shuffling
        diag_2 = abs(diag_2 - m_size)
        cols = [col for col in range(self.size) if col not in [diag_1, diag_2]]
        random.shuffle(cols)
        cols.append(diag_1)
        cols.append(diag_2)



        locations = zip(rows, cols)
        tiles = sorted([col + (row * self.size) for row, col in locations])

        return tiles


    def link_boards(self, goal_list: list[Goal]):
        """Apply exclusions from a previously generated list of (bingosync formatted) goal names."""
        for goal in goal_list:
            goals_to_exclude = self.find_exclusions(goal.name)
            if goals_to_exclude: #false if limit > 1 or no exclusions found
                for excluded_goal in goals_to_exclude:
                    self.remove_goal_by_name(excluded_goal)


    def filter_goals(self):
        """
        Splits the dictionary passed into Goals and Exclusions and returns the parts. Filters based on the Generator's attributes.
        Returns list of Goal dictionaries and list of Exclusive lists.
        """
        #can't modify list during iteration so keep track of removables here
        goals_to_remove: list[Goal] = []

        for goal in self.goal_set.goals:
            if self.game_type is GameTypes.Rando: #remove progression field since it doesn't matter
                goal_tags = goal.types
            else:
                #check if we should exclude the goal based on options passed
                goal_tags = goal.types + goal.progression
            for tag in goal_tags:
                if tag in self.no_tags:
                    goals_to_remove.append(goal)
                    break

        # remove the goals
        for goal in goals_to_remove:
            self.goal_set.remove_goal(goal)


    def find_exclusions(self, goal_name: str):
        """
        Given a goal name, returns the exclusions relevant to this goal or False if none.
        """
        exclusions: list[str] = []
        for exclusion_group in self.goal_set.exclusions:
            # Skip pattern-specific groups if not playing a pattern group
            if self.game_type is not GameTypes.Pattern and exclusion_group.pattern:
                continue

            if goal_name in exclusion_group.unique:
                if exclusion_group.limit is None or exclusion_group.limit == 1: #no limit or limit reached
                    exclusions += exclusion_group.unique
                else:
                    exclusion_group.limit -= 1

        return exclusions if exclusions != [] else False


    def remove_goal_by_name(self, goal_name: str):
        #can't modify list during iteration so keep track of goal here
        goal_to_remove: Goal | None = None

        for goal in self.goal_set.goals:
            if goal.name == goal_name:
                goal_to_remove = goal
                break

        if goal_to_remove is not None:
            self.goal_set.remove_goal(goal_to_remove)

    def get_goal_progression(self, goal_name: str) -> str:
        """Get progression level of a goal from its name."""
        for goal in self.base_set.goals:
            if goal.name == goal_name or goal.fow == goal_name:
                return goal.progression[0]

        # TODO: What's the actual default value?
        return SSProgression.Early

    def board(self):
        """
        Generates a list of goals from the Generator's goalSet. Goals will have a name and optionally exclusions.
        Returns a list of goal names. Modifies the Generator's goalSet.
        """
        goals: list[str] = []

        ordered_prog = ordered_progs[self.game_name]
        indices = self.force_indices()
        forced_goals = []

        # Determine number of random goals to get
        if self.game_type in [GameTypes.Rando, GameTypes.NoForcing]:
            force_count = 0
        else:
            force_count = len(indices)

        goals_needed = self.total_count() - force_count

        # Determine max progression
        max_prog = SSProgression.Early
        for prog in ordered_prog:
            if prog not in self.no_tags:
                max_prog = prog

        while goals_needed > 0:
            if len(self.goal_set.goals) == 0: #critical failure
                raise EOFError("Out of goals! Try again.")

            new_goal = self.goal_set.get_random_goal()
            goal_tags = new_goal.types + new_goal.progression

            #process generator limits and forcing requirements
            skip = False

            print(goals_needed, force_count, len(forced_goals),
                  goals_needed <= force_count - len(forced_goals),
                  len(forced_goals) < force_count,
                  new_goal.progression[0] != max_prog,
                  Tags.NoForcing not in goal_tags)

            if self.tag_limits is not None: #tag limit handling
                for tag in goal_tags:
                    if tag in self.tag_limits.keys(): #tag has a limit
                        if self.tag_limits[tag] == 0: #limit has been reached
                            self.goal_set.remove_goal(new_goal)
                            skip = True #remove goal from list and redraw

            can_force_prog = len(forced_goals) < force_count and new_goal.progression[0] == max_prog and Tags.NoForcing not in goal_tags
            if not skip and goals_needed <= force_count - len(forced_goals) and not can_force_prog:
                #need more max prog goals; unlikely to hit this code path but just in case.
                skip = True

            if skip:
                continue

            ### GOAL IS LOCKED IN AT THIS POINT. DO NOT REDRAW

            # Determine the goal name
            if self.game_type in FOW_TYPES:
                goal_name = new_goal.fow_name
            elif self.game_type is GameTypes.Rando:
                goal_name = new_goal.rando_name
            else:
                goal_name = new_goal.name

            #put it in the right bin
            if can_force_prog:
                forced_goals.append(goal_name)
            else:
                goals.append(goal_name)
                goals_needed -= 1

            #process set exclusions
            exclusions = self.find_exclusions(new_goal.name)
            if exclusions: #exclusions is false if no exclusions found
                for excluded_goal in exclusions:
                    self.remove_goal_by_name(excluded_goal)

            #decrement tag limits
            if self.tag_limits is not None:
                for tag in goal_tags:
                    if tag in self.tag_limits.keys(): #tag has a limit
                        self.tag_limits[tag] = self.tag_limits[tag] - 1 #decrement tag limit

            #remove goal from list to not get chosen twice
            try:
                self.goal_set.remove_goal(new_goal)
            except ValueError: #what
                pass

        total_goals = len(goals) + len(forced_goals)
        if total_goals < self.total_count():
            # print(self.no_tags)
            raise RuntimeError(f"Needed {self.total_count()} goals, only found {total_goals}.")

        if self.game_type is GameTypes.GetToTheOtherSide: #otherside formatting
            goals += forced_goals #combine them
            goals.sort(key=lambda g: ordered_prog.index(self.get_goal_progression(g))) #sort by progression order

            arranged_board = ["placeholder"] * self.total_count() #r1c1 is 0, r3c7 is 26, r10c10 is 99
            for setIndex in range(self.size):
                current_set = goals[(setIndex*self.size) : (setIndex*self.size)+self.size]
                order = random.sample(range(self.size), k=self.size)
                for i, goal in enumerate(current_set):
                    arranged_board[(order[i]*self.size)+setIndex] = goal

            assert "placeholder" not in arranged_board
            return arranged_board

        else: #default setting
            try:
                random.shuffle(goals) #mix em all up when we're done
                if len(forced_goals) > 0: #if this was used
                    for i, index in enumerate(indices):
                        goals.insert(index, forced_goals[i])

                return goals
            except IndexError:
                if self.base_tag_limits is not None:
                    self.tag_limits = self.base_tag_limits.copy()

                self.goal_set = self.base_set.copy()
                return self.board()


class ByngosinkGenerator(Generator):
    """Formats a generated board for Byngosink upload."""
    def export(self):
        return self.board()


class CaravanGenerator(Generator):
    """Formats a generated board for Caravan/Bingosync upload."""
    def export(self):
        return [{"name" : g} for g in self.board()]


class LockoutGenerator(Generator):
    def export(self):
        return json.dumps({
            "schema_version": 3,
            "schema_mode": "relaxed",
            # "capped_schema_settings": {
            #     "max_size": "square8"
            # },
            # "dedicated_schema_settings": {
            #     "game_mode": "bingo",
            #     "game_size": "square8"
            # },
            "game_name": "Silksong",
            "set_name": "Full Act 2",
            "tag_names": [],
            "objectives": [
                {
                    "goal": b,
                    "range": [],
                    "progression": ["e", "m", "l", "n"],
                    "board_categories": [],
                    "line_categories": [],
                    "icons": [],
                    "forced_positions": [i + 1]
                } for (i, b) in enumerate(self.board())
            ],
            "limits": {
                "board": {},
                "line": {}
            }
        })
    

class GeneratorFormatter(Generator):
    """Class with functions to export files. Don't use to generate boards."""
    def __init__(self, goal_filename, game_name=GameNames.Silksong):
        super().__init__(goal_filename, size=5, no_tags=[], tag_limits={},
                         game_name=game_name, game_type=GameTypes.Bingo)

    def board(self):
        raise NotImplementedError

    def bingosync_format(self):
        """
        Outputs a list of goals formatted for bingosync.
        """
        goals_list: list[dict[str, str]] = []

        for goal in self.goal_set.goals:
            if len(goal.range) > 0:
                for name in goal.range_names:
                    goals_list.append({"name": name})
            else:
                goals_list.append({"name": goal.name})

        return goals_list


    def readable_format(self):
        """
        Outputs a list of goals in nice, readable formatting.
        """
        if self.game_name == GameNames.Silksong:
            lines_list = [f"# Goalset Version: {GOALSET_VER}\n\n\n"]
        else:
            lines_list = []

        for goal in self.goal_set.goals:
            if len(goal.range) > 0:
                for name in goal.range_names:
                    bold_name = f"**{name}**"
                    progression = goal.progression
                    types = goal.types
                    lines_list.append(f"{bold_name} | Progression level: {progression} | Other tags: {types}\n\n")
            else:
                bold_name = f"**{goal.name}**"
                progression = goal.progression
                types = goal.types
                lines_list.append(f"{bold_name} | Progression level: {progression} | Other tags: {types}\n\n")

        return lines_list


    def lockout_format(self):
        """
        Outputs a list of goals formatted for Lockout.Live.
        """
        out = {
            "game_name" : "Hollow Knight: Silksong",
            "schema_version" : 3,
            "schema_mode" : "strict",
            "set_name" : "Default Silksong Set",
            "tag_names" : [],
            "limits" : LL_LIMITS
        }

        goals_list = []
        for goal in self.goal_set.goals:
            all_types = goal.progression + goal.types

            skip = False
            for goal_type in all_types: #yeah we iterate over this twice, whatever
                if goal_type in LL_EXCLUDE:
                    skip = True
                    break
            if skip:
                continue #if goal should be excluded, exclude it

            b_types = []
            l_types = []
            for goal_type in all_types:
                if goal_type == SSProgression.Widow:    #the difference between widow and walljump progression was causing balance issues
                    goal_type = SSProgression.ClingGrip  #get outta here

                if goal_type not in out["limits"]["board"].keys() and goal_type not in out["limits"]["line"].keys():
                    out["limits"]["line"][goal_type] = 100
                if goal_type in BOARD_TYPES:
                    b_types.append(goal_type)
                else:
                    l_types.append(goal_type)

            new_dic = {
                "goal" : goal.fow_name,
                "progression" : [LL_PROGRESSION[goal.progression[0]]],
                "range": goal.range,
                "individual_limit": 1,
                "board_categories": b_types,
                "line_categories" : l_types,
                "tooltip": "",
                "icons" : [],
            }

            goals_list.append(new_dic)

        out["objectives"] = goals_list
        return out


class DraftoutGenerator(Generator):
    def __init__(self, no_tags, size, goalset_path=CAT_FILENAME, **kwargs):
        super().__init__(goalset_path, size, no_tags)
        self.goals = []
        self.goalsRemaining = size**2
        self.present_progs = [tag for tag in ordered_progs[GameNames.Silksong] if tag not in no_tags] #ordered tags that arent excluded
        
    def show_goals(self, count=3):
        """Present 3 goals."""
        selected_prog = random.choice(self.present_progs)
        while len([g for g in self.goal_set.goals if g.progression[0] == selected_prog]) < 3:
            self.present_progs.remove(selected_prog)
            selected_prog = random.choice(self.present_progs)
        out = []
        while len(out) < count:
            new_goal = self.goal_set.get_random_goal() #list comprehension to extract weights
            while new_goal.progression[0] != selected_prog or new_goal in out:
                new_goal = self.goal_set.get_random_goal()

            out.append(new_goal)
        return out
    
    def add_goal(self, goal):
        """Adds goal to list and returns number of goals remaining."""
        self.goals.append(goal)
        self.goalsRemaining -= 1
        exclusions = self.find_exclusions(goal.name)
        if exclusions: #exclusions is false if no exclusions found
            for excludedGoal in exclusions:
                self.remove_goal_by_name(excludedGoal)
        self.goal_set.remove_goal(goal.name)
        return self.goalsRemaining
    
    def getList(self):
        return self.goals

if __name__ == "__main__":
    # a = LockoutGenerator(
    #         goal_filename="categorized_v3.json",
    #         size=5,
    #         no_tags=['act3', 'silksoar'],
    #         game_type=GameTypes.Bingo,
    #         tag_limits={"craft" : 3, "flea" : 5, "expensive" : 2},
    #         lockout=False)

    # # print(a.force_indices())

    # board = a.export()
    # print(board)
    # pyperclip.copy(board)

    ####dump the current format for lockout.live
    with open(os.path.join(ASSETS_PATH,COMPUTED_SUBDIR,"silksong_lockoutlive.json"), "w") as f:
        json.dump(GeneratorFormatter("categorized_v3.json").lockout_format(), f, indent=4)

    ####dump the current format for bingosync
    with open(os.path.join(ASSETS_PATH,COMPUTED_SUBDIR,"silksong_bingosync.json"), "w") as f:
        json.dump(GeneratorFormatter("categorized_v3.json").bingosync_format(), f, indent=4)
    #print("File dumped.")

    ####Generate sophont-readable list of goals
    with open(os.path.join(ASSETS_PATH,COMPUTED_SUBDIR,"silksong_readable.md"), "w") as f:
        f.writelines(GeneratorFormatter("categorized_v3.json").readable_format())

    with open(os.path.join(ASSETS_PATH,COMPUTED_SUBDIR,"mio_readable.md"), "w") as f:
        f.writelines(GeneratorFormatter("mio.json", game_name=GameNames.Mio).readable_format())

    with open(os.path.join(ASSETS_PATH,COMPUTED_SUBDIR,"silksong_rando_readable.md"), "w") as f:
        f.writelines(GeneratorFormatter("silksong_rando.json").readable_format())

    #bug tracking
    for i in range(50):
        CaravanGenerator(
            "categorized_v3.json",
            5,
            no_tags=[Tags.Hard, SSProgression.Faydown, SSProgression.Act3, SSProgression.SilkSoar], 
            tag_limits={
                Tags.Craft : 3,
                Tags.Flea : 5,
                Tags.Expensive : 2
            },
            game_type=GameTypes.Bingo,
            lockout=False).export()


        