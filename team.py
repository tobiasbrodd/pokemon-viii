from generators.genetic_generator import GeneticGenerator
from generators.random_generator import RandomGenerator
from generators.naive_generator import NaiveGenerator
from generators.generator import GeneratorType
from pokemon import Type, Stats
from scraper import Dex
from getopt import getopt, GetoptError
import pandas as pd
import numpy as np
import asciify
import tools
import sys
import os


def load(dex=Dex.ALL):
    if dex == Dex.ALL:
        galar_dex = load_dex(dex=Dex.GALAR)
        armor_dex = load_dex(dex=Dex.ARMOR)
        crown_dex = load_dex(dex=Dex.CROWN)
        other_dex = load_dex(dex=Dex.OTHER)
        dex = pd.concat([galar_dex, armor_dex, crown_dex, other_dex])
        return dex.drop_duplicates()
    else:
        return load_dex(dex=dex)


def load_dex(dex):
    file_name = f"data/pokemon_{dex.value}.csv"
    pokemon = pd.read_csv(file_name, sep=",")
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
    skip_no=[],
    only_final=False,
    allow_legendary=True,
    allow_mythical=True,
    allow_ultra=True,
):
    pokemon = pokemon[~pokemon["no"].isin(skip_no)]
    pokemon = pokemon[pokemon["hp"] >= stats[Stats.HP]]
    pokemon = pokemon[pokemon["attack"] >= stats[Stats.ATTACK]]
    pokemon = pokemon[pokemon["defense"] >= stats[Stats.DEFENSE]]
    pokemon = pokemon[pokemon["sp_attack"] >= stats[Stats.SP_ATTACK]]
    pokemon = pokemon[pokemon["sp_defense"] >= stats[Stats.SP_DEFENSE]]
    pokemon = pokemon[pokemon["speed"] >= stats[Stats.SPEED]]
    pokemon = pokemon[
        pokemon["hp"]
        + pokemon["attack"]
        + pokemon["defense"]
        + pokemon["sp_attack"]
        + pokemon["sp_defense"]
        + pokemon["speed"]
        >= stats[Stats.TOTAL]
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
    if not allow_ultra:
        pokemon = pokemon[pokemon["is_ultra"] == 0]

    return pokemon


def print_team(team, color=False):
    if len(team) <= 0:
        return

    team_images, cols = get_team_images(team, color=color)

    images = len(team_images)
    upper_border = "_" * cols * images + "_" * (len(team) + 1)
    middle_border = "-" * cols * images + "-" * (len(team) + 1)

    output = []

    output.append(upper_border)
    output = get_team_title(output, team, cols)
    output.append(middle_border)
    output = get_combined_team_images(output, team_images)
    output.append(middle_border)
    output = get_team_info(output, team, cols)
    output.append(middle_border)

    print("\n".join(output))


def get_team_title(output, team, cols):
    team_output = ["|"]
    for pokemon in team:
        title = f"{pokemon.name} ({pokemon.no})"
        padding = cols - len(title)
        left_padding = padding // 2
        right_padding = padding - left_padding
        title = " " * left_padding + title + " " * right_padding + "|"
        team_output.append(title)
    output.append("".join(team_output))

    return output


def get_team_info(output, team, cols):
    info_output = ["|"]
    for pokemon in team:
        info = pokemon.type_1.name
        if pokemon.type_2 is not None:
            info = f"{info}/{pokemon.type_2.name}"
        padding = cols - len(info)
        left_padding = padding // 2
        right_padding = padding - left_padding
        line = " " * left_padding + info + " " * right_padding + "|"
        info_output.append(line)
    output.append("".join(info_output))

    return output


def get_combined_team_images(output, team_images):
    rows = len(team_images[0])
    images = len(team_images)

    for row in range(rows):
        row_output = []
        for image in range(images):
            if image == 0:
                row_output.append("|")
            row_output.extend(team_images[image][row])
            row_output.append("|")
        output.append("".join(row_output))

    return output


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


def print_team_statistics(pokemon, team, weight):
    print("--------------")
    print("| Statistics |")
    print("--------------")
    nos = np.zeros((len(team),))
    total = np.zeros((len(team),))
    hp = np.zeros((len(team),))
    attack = np.zeros((len(team),))
    defense = np.zeros((len(team),))
    sp_attack = np.zeros((len(team),))
    sp_defense = np.zeros((len(team),))
    speed = np.zeros((len(team),))
    for (i, p) in enumerate(team):
        nos[i] = p.no
        total[i] = p.get_total_stat()
        hp[i] = p.hp
        attack[i] = p.attack
        defense[i] = p.defense
        sp_attack[i] = p.sp_attack
        sp_defense[i] = p.sp_defense
        speed[i] = p.speed
    print(f"Mean Total: {total.mean():.2f}")
    print(f"Mean HP: {hp.mean():.2f}")
    print(f"Mean Attack: {attack.mean():.2f}")
    print(f"Mean Defense: {defense.mean():.2f}")
    print(f"Mean Sp. Attack: {sp_attack.mean():.2f}")
    print(f"Mean Sp. Defense: {sp_defense.mean():.2f}")
    print(f"Mean Speed: {speed.mean():.2f}")
    print(f"Team Score: {tools.fitness(pokemon, nos, weight=weight):.2f}")


def main(argv):
    short_options = "h"
    long_options = [
        "help",
        "seed=",
        "dex=",
        "size=",
        "team=",
        "skip=",
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
        "gen=",
        "weight=",
        "gens=",
        "prop=",
        "teams=",
        "cross=",
        "mut=",
        "final",
        "legendary",
        "mythical",
        "ultra",
        "utypes",
        "uteam",
        "color",
    ]
    help_message = """usage: run.py [options]
    options:
        -h, --help          Prints help message.
        --seed s            Sets random seed to 's'. Default: '123'.
        --dex d             Sets dex to 'd'. Default: 'ALL'.
        --size s            Sets size of the team to 's'. Default: '6'.
        --team t            Sets team to 't'. Default: 'Empty'.
        --skip s            Sets pokemon to skip to 's'. Default: 'Empty'.
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
        --gen g             Sets team generator to 'g'. Default: 'NAIVE'.
        --weight w          Sets weight to 'w'. Default: '0.5'.
        --gens g            Sets genetic generations to 'g'. Default: '10'.
        --prop p            Sets genetic proportion to 'p'. Default: '0.8'.
        --teams t           Sets genetic teams to 't'. Default: '100'.
        --cross c           Sets genetic crossing to 'c'. Default: '2'.
        --mut m             Sets genetic mutations to 'm'. Default: '3'.
        --final             Only allow final evolutions.
        --legendary         Don't allow legendary Pokemon.
        --mytical           Don't allow mythical Pokemon.
        --ultra             Don't allow ultra beast Pokemon.
        --utypes            Enables unique type generation (only for NAIVE).
        --uteam             Enables unique team generation (only for NAIVE/RANDOM).
        --color             Enables colored output."""

    try:
        opts, args = getopt(argv, shortopts=short_options, longopts=long_options)
    except GetoptError:
        print(help_message)
        return

    seed = 123
    dex = Dex.ALL
    size = 6
    team_no = []
    skip_no = []
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
    allow_ultra = True
    gen_type = GeneratorType.NAIVE
    weight = 0.5
    gens = 10
    prop = 0.8
    teams = 100
    cross = 2
    mut = 3
    utypes = False
    uteam = False
    color = False

    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print(help_message)
            return
        elif opt == "--seed":
            seed = int(arg)
        elif opt == "--dex":
            dex = Dex[arg.upper()]
        elif opt == "--size":
            size = int(arg)
        elif opt == "--team":
            team_no = [int(no) for no in arg.split(",")]
        elif opt == "--skip":
            skip_no = [int(no) for no in arg.split(",")]
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
        elif opt == "--weight":
            weight = float(arg)
        elif opt == "--types":
            types = [Type[t.strip().upper()] for t in arg.split(",")]
        elif opt == "--stage":
            stage = int(arg)
        elif opt == "--gen":
            gen_type = GeneratorType[arg.upper()]
        elif opt == "--gens":
            gens = int(arg)
        elif opt == "--final":
            only_final = True
        elif opt == "--legendary":
            allow_legendary = False
        elif opt == "--mythical":
            allow_mythical = False
        elif opt == "--ultra":
            allow_ultra = False
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

    pokemon = load(dex=dex)
    pokemon = filter_pokemon(
        pokemon,
        min_stats,
        types=types,
        stage=stage,
        skip_no=skip_no,
        only_final=only_final,
        allow_legendary=allow_legendary,
        allow_mythical=allow_mythical,
        allow_ultra=allow_ultra,
    )

    generator = None
    if gen_type == GeneratorType.RANDOM:
        generator = RandomGenerator(
            pokemon, team_no=team_no, size=size, uteam=uteam, seed=seed
        )
    elif gen_type == GeneratorType.GENETIC:
        generator = GeneticGenerator(
            pokemon,
            team_no=team_no,
            size=size,
            uteam=uteam,
            weight=weight,
            gens=gens,
            prop=prop,
            teams=teams,
            cross=cross,
            mut=mut,
            seed=seed,
        )
    else:
        generator = NaiveGenerator(
            pokemon,
            team_no=team_no,
            size=size,
            weights=weights,
            utypes=utypes,
            uteam=uteam,
        )

    team = generator.generate()

    print_team(team, color=color)
    print("")
    print_team_statistics(pokemon, team, weight)


if __name__ == "__main__":
    main(sys.argv[1:])
