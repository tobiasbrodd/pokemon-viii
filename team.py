from getopt import getopt, GetoptError
import pandas as pd
import numpy as np
import sys


def load():
    pokemon = pd.read_csv("pokemon.csv", sep=",")

    return pokemon

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
    print(pokemon.loc[pokemon.stage > 3])


if __name__ == "__main__":
    main(sys.argv[1:])
