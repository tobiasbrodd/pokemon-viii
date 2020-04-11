from getopt import getopt, GetoptError
from scraper import PokemonScraper
import sys


def save(pokemon):
    with open("data/pokemon.csv", "w") as f:
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
    long_options = [
        "help",
    ]
    help_message = """usage: download.py [options]
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

    scraper = PokemonScraper()
    urls = scraper.get_urls()
    pokemon, failed = scraper.get_pokemon(urls)

    if len(failed) > 0:
        print("Failed:")
        print(failed.keys())

    if len(pokemon) > 0:
        print("Scraped:")
        print([p.name for p in pokemon])

    save(pokemon)


if __name__ == "__main__":
    main(sys.argv[1:])
