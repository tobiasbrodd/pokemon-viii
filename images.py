from getopt import getopt, GetoptError
from scraper import ImageScraper, Dex, Game
import pandas as pd
import sys


def load(game=Game.SWSH, dex=Dex.GALAR):
    file_name = f"pokemon/{game.value}/{dex.value}.csv"
    pokemon = pd.read_csv(file_name, sep=",")
    pokemon.fillna("", inplace=True)

    return pokemon["no"]


def main(argv):
    short_options = "h"
    long_options = ["help", "game=", "dex="]
    help_message = """usage: images.py [options]
    options:
        -h, --help          Prints help message.
        --game g            Downloads game 'g'. Default: 'SWSH'.
        --dex d             Downloads dex 'd'. Default: 'GALAR'."""

    try:
        opts, args = getopt(argv, shortopts=short_options, longopts=long_options)
    except GetoptError:
        print(help_message)
        return

    game = Game.SWSH
    dex = Dex.GALAR

    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print(help_message)
            return
        elif opt == "--game":
            game = Game[arg.upper()]
        elif opt == "--dex":
            dex = Dex[arg.upper()]

    scraper = ImageScraper()
    urls = load(game=game, dex=dex)
    failed = scraper.download_images(urls, game)

    if len(failed) > 0:
        print("Failed:")
        print(failed.keys())


if __name__ == "__main__":
    main(sys.argv[1:])
