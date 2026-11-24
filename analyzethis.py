from board import CaravanGenerator, GameNames, GameTypes, ordered_progs
from os import path, curdir
import matplotlib.pyplot as plt

ITERS = 2000
FIG_PATH = path.join(curdir, "analysis")

def plotit(counts: dict, figurename: str):
    fig, ax = plt.subplots()
    pcts = percents(counts)
    xlables = [f"{i}-{str(pcts[i])}%" for i in counts.keys()]
    ax.bar(xlables, counts.values(), color="tab:purple")

    for tick in ax.xaxis.get_major_ticks()[1::3]:
        tick.set_pad(15)
    for tick in ax.xaxis.get_major_ticks()[2::3]:
        tick.set_pad(25)

    ax.set_title(figurename)
    fig.tight_layout()

    plt.savefig(f"{path.join(FIG_PATH, figurename)}.png")


def generate(kwargs: dict):
    counts = {p:0 for p in ordered_progs[GameNames.Silksong]}
    for i in range(ITERS):
        # try:
            g = CaravanGenerator("categorized_v3.json", 6, **kwargs)
            progs = [g.get_goal_progression(n["name"]) for n in g.export()]
            for prog in progs:
                counts[prog] += 1
        # except:
        #     pass
    return counts


def percents(counts: dict):
    total = sum(counts.values())
    print(total)

    if total == 0:
        return {p: 0 for p in counts.keys()}

    return {p: round(counts[p]*100/total,1) for p in counts.keys()}

clawline_no_tags = ["faydown", "act3", "silksoar"]

clawline_l = generate({"no_tags": clawline_no_tags, "lockout": True})
plotit(clawline_l, "clawline-lockout prog forcing")

clawline_l_nf = generate({
    "no_tags": clawline_no_tags,
    "lockout": True,
    "game_type":GameTypes.NoForcing})

plotit(clawline_l_nf, "clawline-lockout no forcing")

clawline_nf = generate({
    "no_tags": clawline_no_tags,
    "game_type":GameTypes.NoForcing})

plotit(clawline_nf, "clawline no forcing")

clawline_f  = generate({"no_tags": clawline_no_tags})
plotit(clawline_f, "clawline prog forcing")

g = CaravanGenerator("categorized_v3.json", 6, no_tags=clawline_no_tags)

counts = {p:0 for p in ordered_progs[GameNames.Silksong]}
for goal in g.goal_set.goals:
    counts[goal.progression[0]] += 1

print(percents(counts))