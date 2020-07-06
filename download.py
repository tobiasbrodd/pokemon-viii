from getopt import getopt, GetoptError
from scraper import PokemonScraper, Dex
import sys


def save(pokemon, dex=Dex.GALAR):
    file_name = f"data/pokemon_{dex.value}.csv"
    with open(file_name, "w") as f:
        header = [
            "no",
            "name",
            "type_1",
            "type_2",
            "stage",
            "is_final",
            "is_legendary",
            "is_mythical",
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
        f.write(",".join(header) + "\n")
        for p in pokemon:
            f.write(str(p) + "\n")


def main(argv):
    short_options = "h"
    long_options = ["help", "dex="]
    help_message = """usage: download.py [options]
    options:
        -h, --help          Prints help message.
        --dex d             Downloads dex 'd'. Default: 'GALAR'."""

    try:
        opts, args = getopt(argv, shortopts=short_options, longopts=long_options)
    except GetoptError:
        print(help_message)
        return

    dex = Dex.GALAR

    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print(help_message)
            return
        elif opt == "--dex":
            dex = Dex[arg.upper()]

    scraper = PokemonScraper()
    urls = scraper.get_urls(dex=dex)
    pokemon, failed = scraper.get_pokemon(urls)

    if len(failed) > 0:
        print("Failed:")
        print(failed.keys())

    if len(pokemon) > 0:
        print("Scraped:")
        print([p.name for p in pokemon])

    save(pokemon, dex=dex)


if __name__ == "__main__":
    main(sys.argv[1:])
