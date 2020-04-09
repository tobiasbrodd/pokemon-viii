from getopt import getopt, GetoptError
import pandas as pd
import numpy as np
import sys


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


def get_types(pokemon):
    lookup = {}
    types = list(zip(pokemon.type_1, pokemon.type_2))
    types = list(set(types))

    return types


def generate_weakness_chart(pokemon):
    types = get_types(pokemon)
    indices = {}
    weaknesses = []
    for (i, t) in enumerate(types):
        type_1 = t[0]
        type_2 = t[1]
        fltr = np.logical_and(pokemon.type_1 == type_1, pokemon.type_2 == type_2)
        pkmn = pokemon.loc[fltr].head(1).to_numpy()
        weaknesses.append(pkmn[:, 14:].reshape(-1,))
        indices[t] = i

    all_types = pokemon.columns[14:]
    weaknesses = np.asmatrix(weaknesses)
    weaknesses = pd.DataFrame(weaknesses, index=types, columns=all_types)

    return weaknesses, types


def generate_team_types(weaknesses, types, n=6):
    team_types = []
    weaknesses -= 1
    chart = weaknesses

    for i in range(n):
        perf = np.sum(chart, axis=1)
        best = np.argmin(perf)
        t = types[best]
        team_types.append(t)
        chart = update_chart(weaknesses, chart, t, best)

    return team_types


def update_chart(weaknesses, chart, t, best):
    type_1 = t[0]
    type_2 = t[1]

    m, n = weaknesses.shape

    update = chart * 0

    type_weaknesses = weaknesses.iloc[best, :]
    min_weakness = np.amin(type_weaknesses)
    weak_types = type_weaknesses[type_weaknesses == min_weakness]
    fltr = np.logical_and(weak_types.index != type_1, weak_types.index != type_2)
    update_types = weak_types.loc[fltr]
    update.iloc[best, :][update_types.index] += 2

    type_weaknesses = weaknesses.iloc[best, :]
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


def get_team(pokemon, team_types, weights=None):
    team = []

    if weights is None:
        stats = pokemon.columns[8:14]
        weights = pd.DataFrame(np.ones((1, 6)), columns=stats)

    for t in team_types:
        type_1 = t[0]
        type_2 = t[1]
        fltr = np.logical_and(pokemon.type_1 == type_1, pokemon.type_2 == type_2)
        pkmns = pokemon.loc[fltr]
        stats = pkmns.iloc[:, 8:14]
        weighted_stats = stats.multiply(weights.to_numpy())
        index = weighted_stats.sum(axis=1).idxmax(axis=0)
        pkmn = pkmns.loc[index]
        team.append(pkmn["name"])

    return team


def main(argv):
    short_options = "h"
    long_options = [
        "help",
    ]
    help_message = """usage: run.py [options]
    options:
        -h, --help          Prints help message."""

    try:
        opts, args = getopt(argv, shortopts=short_options, longopts=long_options)
    except GetoptError:
        print(help_message)
        return

    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print(help_message)
            return

    pokemon = load()
    weaknesses, types = generate_weakness_chart(pokemon)
    team_types = generate_team_types(weaknesses, types)

    # stats = pokemon.columns[8:14]
    # weights = pd.DataFrame(np.zeros((1, 6)), columns=stats)
    # weights["speed"] = 1
    team = get_team(pokemon, team_types)
    print(f"Team: {team}")


if __name__ == "__main__":
    main(sys.argv[1:])
