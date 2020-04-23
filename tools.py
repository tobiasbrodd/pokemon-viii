from pokemon import Pokemon, Type, Stats
import pandas as pd
import numpy as np

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
