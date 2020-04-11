from getopt import getopt, GetoptError
from scraper import ImageScraper
import pandas as pd
import sys


def load():
    pokemon = pd.read_csv("data/pokemon.csv", sep=",")
    pokemon.fillna("", inplace=True)

    return pokemon["no"][200:]


def main(argv):
    short_options = "h"
    long_options = [
        "help",
    ]
    help_message = """usage: images.py [options]
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

    scraper = ImageScraper()
    urls = load()
    failed = scraper.download_images(urls)

    if len(failed) > 0:
        print("Failed:")
        print(failed.keys())


if __name__ == "__main__":
    main(sys.argv[1:])
