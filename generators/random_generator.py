from generators.generator import Generator
import numpy as np
import tools


class RandomGenerator(Generator):
    def __init__(self, pokemon, team_no=[], size=6):
        self.pokemon = pokemon
        self.team_no = team_no
        self.size = size
        self.team = []

    def generate(self):
        self.team = []

        for no in self.team_no:
            pkmn = self.pokemon[self.pokemon["no"] == no].squeeze()
            if pkmn.empty:
                continue
            self.team.append(tools.frame_to_pokemon(pkmn))

        n = self.pokemon.shape[0]
        rdx = []
        if unique:
            rdx = np.random.choice(n, self.size - len(self.team))
        else:
            rdx = np.random.randint(0, n, self.size - len(self.team))
        pkmns = self.pokemon.iloc[rdx, :]
        rows = pkmns.shape[0]
        for row in range(rows):
            self.team.append(tools.frame_to_pokemon(pkmns.iloc[row, :]))

        return self.team
