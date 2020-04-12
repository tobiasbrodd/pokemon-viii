from pokemon import Pokemon, Type, Stats
from getopt import getopt, GetoptError
import pandas as pd
import numpy as np
import asciify
import sys
import os


def load():
    pokemon = pd.read_csv("data/pokemon.csv", sep=",")
    pokemon.fillna("", inplace=True)

    rows = pokemon.shape[0]
    for row in range(rows):
        type_1 = pokemon.loc[row, "type_1"]
        type_2 = pokemon.loc[row, "type_2"]

        if len(type_2) > 0 and type_2 < type_1:
            pokemon.loc[row, "type_1"] = type_2
            pokemon.loc[row, "type_2"] = type_1

    return pokemon


def filter_pokemon(
    pokemon,
    stats,
    types=None,
    stage=None,
    only_final=False,
    allow_legendary=True,
    allow_mythical=True,
):
    pokemon = pokemon[pokemon["hp"] > stats[Stats.HP]]
    pokemon = pokemon[pokemon["attack"] > stats[Stats.ATTACK]]
    pokemon = pokemon[pokemon["defense"] > stats[Stats.DEFENSE]]
    pokemon = pokemon[pokemon["sp_attack"] > stats[Stats.SP_ATTACK]]
    pokemon = pokemon[pokemon["sp_defense"] > stats[Stats.SP_DEFENSE]]
    pokemon = pokemon[pokemon["speed"] > stats[Stats.SPEED]]
    pokemon = pokemon[
        pokemon["hp"]
        + pokemon["attack"]
        + pokemon["defense"]
        + pokemon["sp_attack"]
        + pokemon["sp_defense"]
        + pokemon["speed"]
        > stats[Stats.TOTAL]
    ]

    if types is not None:
        for t in types:
            fltr = np.logical_or(pokemon.type_1 == t.value, pokemon.type_2 == t.value)
            pokemon = pokemon[fltr]
    if stage is not None:
        pokemon = pokemon[pokemon["stage"] == stage]
    if only_final:
        pokemon = pokemon[pokemon["is_final"] == 1]
    if not allow_legendary:
        pokemon = pokemon[pokemon["is_legendary"] == 0]
    if not allow_mythical:
        pokemon = pokemon[pokemon["is_mythical"] == 0]

    return pokemon


def get_types(pokemon):
    lookup = {}
    types = list(zip(pokemon["type_1"], pokemon["type_2"]))
    types = list(set(types))

    return types


def get_team_types(pokemon, team_no):
    team_types = []
    for no in team_no:
        pkmn = pokemon[pokemon["no"] == no]
        if pkmn.empty:
            continue
        pkmn = pkmn.head(1)
        team_types.append(*zip(pkmn["type_1"], pkmn["type_2"]))

    return team_types


def generate_weakness_chart(pokemon):
    types = get_types(pokemon)
    indices = {}
    weaknesses = []
    for (i, t) in enumerate(types):
        type_1 = t[0]
        type_2 = t[1]
        fltr = np.logical_and(pokemon["type_1"] == type_1, pokemon["type_2"] == type_2)
        pkmn = pokemon.loc[fltr].head(1).to_numpy()
        weaknesses.append(pkmn[:, 14:].reshape(-1,))
        indices[t] = i

    all_types = pokemon.columns[14:]
    weaknesses = np.asmatrix(weaknesses)
    multi_index = pd.MultiIndex.from_tuples(types)
    weaknesses = pd.DataFrame(weaknesses, index=multi_index, columns=all_types)

    return weaknesses, types


def generate_team_types(
    pokemon, weaknesses, types, size=6, team=[], unique=False, unique_team=False
):
    team_types = []
    weaknesses -= 1
    weaknesses *= 2
    chart = weaknesses
    split = len(team)

    for i in range(split):
        t = team[i]
        team_types.append(t)
        chart = update_chart(weaknesses, chart, t)

    for i in range(split, size):
        t = get_best_type(chart, types)
        chart = update_chart(weaknesses, chart, t)
        uteam_exists = unique_team_exists(pokemon, team_types, t)
        while (t in team_types and unique) or (not uteam_exists and unique_team):
            if chart.shape[0] <= len(team_types):
                t = None
                break
            t = get_best_type(chart, types)
            chart = update_chart(weaknesses, chart, t)
            uteam_exists = unique_team_exists(pokemon, team_types, t)
        if t is not None:
            team_types.append(t)

    return team_types


def get_best_type(chart, types):
    perf = np.sum(chart, axis=1)
    best = np.argmin(perf)

    return types[best]


def unique_team_exists(pokemon, team_types, t):
    n_team_type = len(list(filter(lambda tt: tt == t, team_types))) + 1
    fltr = np.logical_and(pokemon["type_1"] == t[0], pokemon["type_2"] == t[1])
    n_pokemon = pokemon.loc[fltr].shape[0]
    return n_pokemon >= n_team_type


def update_chart(weaknesses, chart, t):
    type_1 = t[0]
    type_2 = t[1]

    m, n = weaknesses.shape

    update = chart * 0

    type_weaknesses = weaknesses.loc[t, :]
    min_weakness = np.amin(type_weaknesses)
    weak_types = type_weaknesses[type_weaknesses == min_weakness]
    fltr = np.logical_and(weak_types.index != type_1, weak_types.index != type_2)
    update_types = weak_types.loc[fltr]
    update.loc[t, :][update_types.index] += 1

    type_weaknesses = weaknesses.loc[t, :]
    max_weaknesses = np.amax(type_weaknesses)
    strong_types = type_weaknesses[type_weaknesses == max_weaknesses].index
    effective = weaknesses[strong_types]
    update_indices = []
    update_types = []
    for row in range(m):
        weakness_types = effective.columns[(effective.iloc[row, :] < 0).values]
        e_type_1 = effective.index[row][0]
        e_type_2 = effective.index[row][1]
        not_in_strong_types = (e_type_1 not in strong_types) and (
            e_type_2 not in strong_types
        )
        if len(weakness_types) > 0 and not_in_strong_types:
            update_indices.append(row)
            update_types.append(weakness_types)

    for i in range(len(update_indices)):
        index = update_indices[i]
        weakness_types = update_types[i]
        update.iloc[index, :][weakness_types] -= 1

    chart = chart.add(update)

    return chart


def get_team(pokemon, team_types, weights=None, team_no=[], unique=False):
    team = []
    team_types = team_types[len(team_no) :]

    for no in team_no:
        pkmn = pokemon[pokemon["no"] == no].squeeze()
        if pkmn.empty:
            continue
        team.append(frame_to_pokemon(pkmn))

    if weights is None:
        stats = pokemon.columns[8:14]
        weights = pd.DataFrame(np.ones((1, 6)), columns=stats)

    for t in team_types:
        pkmn = get_pokemon(pokemon, team, weights, t, unique=unique)
        if pkmn is not None:
            team.append(frame_to_pokemon(pkmn))

    return team


def get_pokemon(pokemon, team, weights, t, unique=False):
    type_1 = t[0]
    type_2 = t[1]
    fltr = np.logical_and(pokemon["type_1"] == type_1, pokemon["type_2"] == type_2)
    pkmns = pokemon.loc[fltr]
    if unique:
        team_names = [p.name for p in team]
        pkmns = pkmns[~pkmns.loc[:, "name"].isin(team_names)]
    if pkmns.empty:
        return None
    stats = pkmns.iloc[:, 8:14]
    weighted_stats = stats.multiply(weights.to_numpy())
    index = weighted_stats.sum(axis=1).idxmax(axis=0)
    pkmn = pkmns.loc[index]

    return pkmn


def get_random_team(pokemon, size=6, team_no=[], unique=False):
    team = []

    for no in team_no:
        pkmn = pokemon[pokemon["no"] == no].squeeze()
        if pkmn.empty:
            continue
        team.append(frame_to_pokemon(pkmn))

    n = pokemon.shape[0]
    rdx = []
    if unique:
        rdx = np.random.choice(n, size - len(team))
    else:
        rdx = np.random.randint(0, n, size - len(team))
    pkmns = pokemon.iloc[rdx, :]
    rows = pkmns.shape[0]
    for row in range(rows):
        team.append(frame_to_pokemon(pkmns.iloc[row, :]))

    return team


def frame_to_pokemon(frame):
    if frame is None:
        return None

    no = frame["no"]
    name = frame["name"]
    type_1 = frame["type_1"]
    type_2 = frame["type_2"]
    types = [Type[type_1.upper()], None if len(type_2) <= 0 else Type[type_2.upper()]]
    stats = {
        Stats.HP: frame["hp"],
        Stats.ATTACK: frame["attack"],
        Stats.DEFENSE: frame["defense"],
        Stats.SP_ATTACK: frame["sp_attack"],
        Stats.SP_DEFENSE: frame["sp_defense"],
        Stats.SPEED: frame["speed"],
    }
    weaknesses = frame[14:]
    stage = frame["stage"]
    is_final = frame["is_final"]
    is_legendary = frame["is_legendary"]
    is_mythical = frame["is_mythical"]

    pokemon = Pokemon(
        no,
        name,
        types,
        stats,
        weaknesses,
        stage=stage,
        is_final=is_final,
        is_legendary=is_legendary,
        is_mythical=is_mythical,
    )

    return pokemon


def print_team(team, color=False):
    if len(team) <= 0:
        return

    team_images, cols = get_team_images(team, color=color)

    rows = len(team_images[0])
    images = len(team_images)
    output = []

    output.append("_" * cols * images + "_" * (len(team) + 1))
    team_output = ["|"]
    for pokemon in team:
        padding = cols - len(pokemon.name)
        left_padding = padding // 2
        right_padding = padding - left_padding
        title = " " * left_padding + pokemon.name + " " * right_padding + "|"
        team_output.append(title)
    output.append("".join(team_output))

    output.append("-" * cols * images + "-" * (len(team) + 1))
    for row in range(rows):
        row_output = []
        for image in range(images):
            if image == 0:
                row_output.append("|")
            row_output.extend(team_images[image][row])
            row_output.append("|")
        output.append("".join(row_output))
    output.append("-" * cols * images + "-" * (len(team) + 1))

    combined_team_image = "\n".join(output)
    print(combined_team_image)


def get_team_images(team, color=False):
    team_images = []
    for pokemon in team:
        no = str(pokemon.no)
        while len(no) < 3:
            no = "0" + no

        path = f"images/{no}.png"
        image = asciify.get_image(path)
        if image is None:
            continue

        width = os.get_terminal_size().columns // len(team) - 2
        ascii_image = asciify.convert(image, width=width, color=color)
        team_images.append(ascii_image)

    return team_images, width


def print_team_statistics(team):
    print("Statistics")
    print("----------")
    stats = np.zeros((len(team),))
    for (i, p) in enumerate(team):
        stats[i] = p.get_total_stat()
    print(f"Mean Total: {stats.mean():.2f}")


def main(argv):
    short_options = "h"
    long_options = [
        "help",
        "size=",
        "team=",
        "hp=",
        "attack=",
        "defense=",
        "spattack=",
        "spdefense=",
        "speed=",
        "total=",
        "weights=",
        "types=",
        "stage=",
        "final",
        "legendary",
        "mythical",
        "random",
        "utypes",
        "uteam",
        "color"
    ]
    help_message = """usage: run.py [options]
    options:
        -h, --help          Prints help message.
        --size s            Sets size of the team to 's'. Default: '6'.
        --team t            Sets team to 't'. Default: 'Empty'.
        --hp h              Sets minimum HP to 'h'. Default: '0'.
        --attack a          Sets minimum attack to 'a'. Default: '0'.
        --defense d         Sets minimum defense to 'd'. Default: '0'.
        --spattack s        Sets minimum sp. attack to 's'. Default: '0'.
        --spdefense s       Sets minimum sp. defense to 's'. Default: '0'.
        --speed s           Sets minimum speed to 's'. Default: '0'.
        --total t           Sets minimum total to 't'. Default: '0'.
        --weights w         Sets weights to 'w'. Default: '1,1,1,1,1,1'.
        --types t           Sets types to 't. Default: 'All'.
        --stage s           Sets stage to 'ws'. Default: 'None'.
        --final             Only allow final evolutions.
        --legendary         Don't allow legendary Pokemon.
        --mytical           Don't allow mythical Pokemon.
        --random            Randomize team generation.
        --utypes            Enables unique type generation (if not random).
        --uteam             Enables unique team generation.
        --color             Enables colored output."""

    try:
        opts, args = getopt(argv, shortopts=short_options, longopts=long_options)
    except GetoptError:
        print(help_message)
        return

    size = 6
    team_no = []
    min_hp = 0
    min_attack = 0
    min_defense = 0
    min_sp_attack = 0
    min_sp_defense = 0
    min_speed = 0
    min_total = 0
    weights = np.ones((1, 6))
    types = None
    stage = None
    only_final = False
    allow_legendary = True
    allow_mythical = True
    randomize = False
    utypes = False
    uteam = False
    color = False

    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print(help_message)
            return
        elif opt == "--size":
            size = int(arg)
        elif opt == "--team":
            team_no = [int(no) for no in arg.split(",")]
        elif opt == "--hp":
            min_hp = float(arg)
        elif opt == "--attack":
            min_attack = float(arg)
        elif opt == "--defense":
            min_defense = float(arg)
        elif opt == "--spattack":
            min_sp_attack = float(arg)
        elif opt == "--spdefense":
            min_sp_defense = float(arg)
        elif opt == "--speed":
            min_speed = float(arg)
        elif opt == "--total":
            min_total = float(arg)
        elif opt == "--weights":
            weights = np.asmatrix([float(w) for w in arg.split(",")])
        elif opt == "--types":
            types = [Type[t.strip().upper()] for t in arg.split(",")]
        elif opt == "--stage":
            stage = int(arg)
        elif opt == "--final":
            only_final = True
        elif opt == "--legendary":
            allow_legendary = False
        elif opt == "--mythical":
            allow_mythical = False
        elif opt == "--random":
            randomize = True
        elif opt == "--utypes":
            utypes = True
        elif opt == "--uteam":
            uteam = True
        elif opt == "--color":
            color = True

    if weights.shape[1] != 6:
        print(help_message)
        return
    elif stage is not None and (stage < 1 or stage > 3):
        print(help_message)
        return
    elif len(team_no) > size:
        print(help_message)
        return

    min_stats = {
        Stats.HP: min_hp,
        Stats.ATTACK: min_attack,
        Stats.DEFENSE: min_defense,
        Stats.SP_ATTACK: min_sp_attack,
        Stats.SP_DEFENSE: min_sp_defense,
        Stats.SPEED: min_speed,
        Stats.TOTAL: min_total,
    }

    pokemon = load()
    pokemon = filter_pokemon(
        pokemon,
        min_stats,
        types=types,
        stage=stage,
        only_final=only_final,
        allow_legendary=allow_legendary,
        allow_mythical=allow_mythical,
    )

    team = []
    if randomize:
        team = get_random_team(pokemon, size=size, team_no=team_no, unique=uteam)
    else:
        weaknesses, types = generate_weakness_chart(pokemon)
        team_types = get_team_types(pokemon, team_no)
        team_types = generate_team_types(
            pokemon,
            weaknesses,
            types,
            size=size,
            team=team_types,
            unique=utypes,
            unique_team=uteam,
        )
        stats = pokemon.columns[8:14]
        weights = pd.DataFrame(weights, columns=stats)
        team = get_team(
            pokemon, team_types, weights=weights, team_no=team_no, unique=uteam
        )

    print_team(team, color=color)
    print("")
    print_team_statistics(team)


if __name__ == "__main__":
    main(sys.argv[1:])
