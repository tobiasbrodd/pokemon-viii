from getopt import getopt, GetoptError
from scraper import PokemonScraper, Dex, Game
import pandas as pd
import tools
import sys

HEADER = [
    "no",
    "name",
    "type_1",
    "type_2",
    "stage",
    "is_final",
    "is_legendary",
    "is_mythical",
    "is_ultra",
    "hp",
    "attack",
    "defense",
    "sp_attack",
    "sp_defense",
    "speed",
    "normal",
    "fire",
    "water",
    "electric",
    "grass",
    "ice",
    "fighting",
    "poison",
    "ground",
    "flying",
    "psychic",
    "bug",
    "rock",
    "ghost",
    "dragon",
    "dark",
    "steel",
    "fairy",
]


def save(pokemon, game=Game.SWSH, dex=Dex.GALAR):
    file_name = f"pokemon/{game.value}/{dex.value}.csv"
    with open(file_name, "w") as f:
        f.write(",".join(HEADER) + "\n")
        for p in pokemon:
            f.write(str(p) + "\n")


def load(game=Game.SWSH, dex=Dex.GALAR):
    pokemon = []
    lines = []
    file_name = f"pokemon/{game.value}/{dex.value}.csv"
    with open(file_name, "r") as f:
        lines = f.readlines()
    header = lines[0].replace("\n", "").split(",")
    for line in lines[1:]:
        line = line.replace("\n", "")
        values = line.split(",")
        frame = pd.Series(values, index=header)
        p = tools.frame_to_pokemon(frame)
        pokemon.append(p)

    return pokemon


def main(argv):
    short_options = "h"
    long_options = ["help", "game=", "dex=", "workers="]
    help_message = """usage: download.py [options]
    options:
        -h, --help          Prints help message.
        --game g            Downloads game 'g'. Default: 'SWSH'.
        --dex d             Downloads dex 'd'. Default: 'GALAR'.
        --workers w         Uses 'w' workers. Default: None (cpu_count)."""

    try:
        opts, args = getopt(argv, shortopts=short_options, longopts=long_options)
    except GetoptError:
        print(help_message)
        return

    game = Game.SWSH
    dex = Dex.GALAR
    workers = None

    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print(help_message)
            return
        elif opt == "--game":
            game = Game[arg.upper()]
        elif opt == "--dex":
            dex = Dex[arg.upper()]
        elif opt == "--workers":
            workers = int(arg)

    scraper = PokemonScraper()
    urls = scraper.get_urls(game=game, dex=dex)
    pokemon, failed = scraper.get_pokemon(urls, workers=workers)

    if len(failed) > 0:
        print("Failed:")
        print(failed.keys())

    if len(pokemon) > 0:
        print("Scraped:")
        print([p.name for p in pokemon])

    # pokemon = load(dex=dex)
    save(pokemon, game=game, dex=dex)


if __name__ == "__main__":
    main(sys.argv[1:])
