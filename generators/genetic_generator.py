from generators.generator import Generator
import numpy as np
import tools


class GeneticGenerator(Generator):
    def __init__(
        self,
        pokemon,
        team_no=[],
        size=6,
        uteam=False,
        weight=1,
        gens=10,
        prop=0.8,
        teams=100,
        cross=2,
        replace=3,
    ):
        self.pokemon = pokemon
        self.team_no = team_no
        self.size = size
        self.uteam = uteam
        self.weight = weight
        self.gens = gens
        self.prop = prop
        self.teams = teams
        self.cross = cross
        self.replace = replace
        self.team = []

    def generate(self):
        """Runs simulation."""

        self.team = []

        teams = self._population()
        fit = self._fitness(teams)
        best = np.argmax(fit)
        best_fit = fit[best]
        prev_fit = best_fit
        best_team = self.pokemon.iloc[teams[best], :]["name"].to_numpy()
        prev_team = best_team
        initial = fit[best]

        evolving = True
        gen = 0
        while evolving:
            fit = self._fitness(teams)
            best = np.argmax(fit)
            best_fit = fit[best]
            best_team = self.pokemon.iloc[teams[best], :]["name"].to_numpy()
            self._progress(prev_fit, prev_team, best_fit, best_team)
            prev_fit = best_fit
            prev_team = best_team
            teams = self._evolve(teams)
            gen += 1
            evolving = gen < self.gens

        self._summary(initial, best_fit)

        team_idx = teams[best]
        pkmns = self.pokemon.iloc[team_idx, :]
        rows = pkmns.shape[0]
        for row in range(rows):
            self.team.append(tools.frame_to_pokemon(pkmns.iloc[row, :]))

        return self.team

    def _progress(self, prev, prev_team, best, best_team):
        """Prints progress."""

        prev_out = f"Progress: {prev:.2f}: {prev_team}"
        out = f"Progress: {best:.2f}: {best_team}"
        clear = " " * len(prev_out)
        print(f"\r{clear}", end="")
        print(f"\r{out}", end="")

    def _summary(self, initial, best):
        """Prints summary."""

        prev_out = f"Progress: {best:.2f}"
        clear = " " * len(prev_out)
        print(f"\r{clear}", end="")
        print(f"\rInitial: {initial:.2f}")
        print(f"Best: {best:.2f}")

    def _population(self):
        """Creates a team population."""

        teams = None
        n = self.pokemon.shape[0]
        size = (self.teams, self.size)
        if self.uteam:
            teams = np.zeros(size)
            for row in range(size[0]):
                teams[row, :] = np.random.choice(n, size=size[1], replace=False)
        else:
            teams = np.random.choice(n, size=size, replace=True)

        return teams

    def _evolve(self, teams):
        """Evolves a team population."""

        sel = self._select(teams)
        evo = self._crossover(sel)
        evo = self._mutate(evo)

        n_teams = teams.shape[0]
        n_evo = evo.shape[0]
        n_rest = n_teams - n_evo
        if n_rest <= 0:
            return evo

        fit = self._fitness(teams)
        idx = np.argsort(fit)[::-1][:n_rest]
        best = teams[idx, :]
        evol = np.concatenate((best, evo), axis=0)

        return evol

    def _select(self, teams):
        """Selects a team subpopulation."""

        n = teams.shape[0]
        fit = self._fitness(teams)
        fit_sum = np.sum(fit)
        min_fit = np.amin(fit_sum)
        if min_fit < 0:
            fit_sum += np.abs(min_fit) * n
            fit += np.abs(min_fit)
        probs = fit / fit_sum

        rows = int(n * self.prop)
        idx_size = (rows, self.cross)
        idx = np.random.choice(n, size=idx_size, replace=True, p=probs)

        cols = teams.shape[1]
        sel_size = (rows, cols, self.cross)
        sel = np.zeros(sel_size)
        for col in range(self.cross):
            teams_idx = idx[:, col]
            sel[:, :, col] = teams[teams_idx, :]

        return sel

    def _fitness(self, teams):
        """Evaluates fitness for a team population."""

        rows = teams.shape[0]
        fit = np.zeros((rows,))
        for row in range(rows):
            team_idx = teams[row, :]
            team = self.pokemon.iloc[team_idx, :]

            stats = team.iloc[:, tools.STAT_COLS].to_numpy(dtype=float)
            weaknesses = team.iloc[:, tools.WEAK_COLS].to_numpy(dtype=float)

            stat_score = np.mean(np.sum(stats, axis=0))
            weak_score = np.mean(np.sum(weaknesses, axis=0))

            stat_score = (stat_score - tools.MIN_STAT) / tools.MAX_STAT
            weak_score = (weak_score - tools.MIN_WEAK) / tools.MAX_WEAK

            stat_score = np.minimum(stat_score, 1)
            weak_score = np.minimum(weak_score, 1)

            weak_score = 1 - weak_score
            fit[row] = self.weight * stat_score + (1 - self.weight) * weak_score

        return fit

    def _individual_fitness(self, team):
        """Evaluates fitness for team members."""

        team_idx = team
        team = self.pokemon.iloc[team_idx, :]

        stats = team.iloc[:, tools.STAT_COLS].to_numpy(dtype=float)
        weaknesses = team.iloc[:, tools.WEAK_COLS].to_numpy(dtype=float)

        stat_scores = np.sum(stats, axis=1)
        weak_scores = np.sum(weaknesses, axis=1)

        stat_scores = (stat_scores - tools.MIN_STAT) / tools.MAX_STAT
        weak_scores = (weak_scores - tools.MIN_WEAK) / tools.MAX_WEAK

        stat_scores = np.minimum(stat_scores, 1)
        weak_scores = np.minimum(weak_scores, 1)

        weak_scores = 1 - weak_scores

        fit = self.weight * stat_scores + (1 - self.weight) * weak_scores

        return fit

    def _crossover(self, sel):
        """Crosses a team population."""

        rows = sel.shape[0]
        cols = sel.shape[1]
        cross = sel.shape[2]
        teams = np.zeros((rows, cols))

        for row in range(rows):
            total_size = (cols * cross,)
            pokemon = sel[row, :, :].reshape(total_size, order="F")
            old = pokemon
            if self.uteam:
                pokemon = np.unique(pokemon)
            pokemon_fit = self._individual_fitness(pokemon)
            pokemon_best = np.argsort(pokemon_fit)[::-1][:cols]
            teams[row, :] = pokemon_best

        return teams

    def _mutate(self, teams):
        """Mutates a team population."""

        n = self.pokemon.shape[0]
        n_teams = teams.shape[0]
        n_team = teams.shape[1]
        size = (n_teams, self.replace)
        replace_idx = np.random.choice(n_team, size=size, replace=True)

        if self.uteam:
            for row in range(n_teams):
                new_idx = self._get_unique(teams[row, :], n, size)
                teams[row, replace_idx[row]] = new_idx
        else:
            new_idx = np.random.choice(n, size=size, replace=True)
            for row in range(n_teams):
                teams[row, replace_idx[row]] = new_idx[row]

        return teams

    def _get_unique(self, team, n, size):
        """Returns unique pokemon indices."""

        unique = True
        new_idx = None
        while unique:
            new_idx = np.random.choice(n, size=size[1], replace=False)
            unique = np.sum(np.isin(new_idx, team))

        return new_idx
