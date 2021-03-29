from pokemon import Pokemon, Type, Stats
import pandas as pd
import numpy as np

STAT_COLS = range(8, 14)
WEAK_COLS = range(14, 32)
MAX_STAT = 720
MIN_STAT = 100
MAX_WEAK = 26
MIN_WEAK = 13


def no_to_idx(pokemon, team_no):
    """Converts NOs to indices."""

    pokemon = pokemon.reset_index(drop=True)
    unique_team = pokemon[pokemon["no"].isin(team_no)]
    team_idx = np.zeros((len(team_no),))
    for (i, no) in enumerate(team_no):
        team_idx[i] = unique_team[unique_team["no"] == no].index.item()

    return team_idx


def fitness(pokemon, team_no, weight=0.5):
    """Evaluates fitness for a team."""

    team_idx = no_to_idx(pokemon, team_no)

    team = pokemon.iloc[team_idx, :]

    stats = team.iloc[:, STAT_COLS].to_numpy(dtype=float)
    weaknesses = team.iloc[:, WEAK_COLS].to_numpy(dtype=float)

    n_team = team.shape[0]
    stat_score = np.mean(np.sum(stats, axis=0))
    weak_score = np.sum(np.sum(weaknesses, axis=0)) / n_team

    stat_score = (stat_score - MIN_STAT) / MAX_STAT
    weak_score = (weak_score - MIN_WEAK) / MAX_WEAK

    stat_score = np.minimum(stat_score, 1)
    weak_score = np.minimum(weak_score, 1)

    weak_score = 1 - weak_score

    fit = weight * stat_score + (1 - weight) * weak_score

    return fit


def get_types(pokemon):
    lookup = {}
    types = list(zip(pokemon["type_1"], pokemon["type_2"]))
    types = list(set(types))

    return types


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
    
    stage = frame["stage"]
    is_final = frame["is_final"]
    is_legendary = frame["is_legendary"]
    is_mythical = frame["is_mythical"]
    is_ultra = frame["is_ultra"]
    weaknesses = frame[15:].to_dict()
    
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
        is_ultra=is_ultra
    )

    return pokemon
