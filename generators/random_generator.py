from generators.generator import Generator
from numpy.random import default_rng
import numpy as np
import tools


class RandomGenerator(Generator):
    def __init__(self, pokemon, team_no=[], size=6, utypes=False, uteam=False, seed=None):
        self.pokemon = pokemon
        self.team_no = team_no
        self.size = size
        self.utypes = utypes
        self.uteam = uteam
        self.team = []
        self.rng = default_rng(seed)

    def generate(self):
        self.team = []

        for no in self.team_no:
            pkmn = self.pokemon[self.pokemon["no"] == no].squeeze()
            if pkmn.empty:
                continue
            self.team.append(tools.frame_to_pokemon(pkmn))

        if self.utypes:
            self._filter_unique_types()

        return self._get_team()

    def _get_team(self):
        n = self.pokemon.shape[0]
        replace = not self.uteam
        rdx = self.rng.choice(n, self.size - len(self.team), replace=replace)
        pkmns = self.pokemon.iloc[rdx, :]
        rows = pkmns.shape[0]
        for row in range(rows):
            self.team.append(tools.frame_to_pokemon(pkmns.iloc[row, :]))

        return self.team

    def _get_unique_types(self):
        all_types = self.pokemon[["type_1","type_2"]]
        unique_types = all_types.drop_duplicates().reset_index()

        return unique_types

    def _filter_unique_types(self):
        unique_types = self._get_unique_types()
        n = unique_types.shape[0]
        rdx = self.rng.choice(n, self.size - len(self.team), replace=False)
        team_types = unique_types.iloc[rdx, :]
        fltr = np.logical_and(
            self.pokemon["type_1"].isin(unique_types["type_1"]), self.pokemon["type_2"].isin(unique_types["type_2"])
        )
        self.pokemon = self.pokemon.loc[fltr]
