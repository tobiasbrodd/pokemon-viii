from generators.generator import Generator
import numpy as np
import tools


class GeneticGenerator(Generator):
    def __init__(self, pokemon, team_no=[], size=6):
        self.pokemon = pokemon
        self.team_no = team_no
        self.size = size
        self.team = []

    def generate(self, size=(100, 6), gens=10, prop=0.8):
        """Runs simulation."""

        self.team = []

        teams = self._population(size=size)
        fit = self._fitness(teams)
        best = np.argmax(fit)
        best_fit = fit[best]
        prev_fit = best_fit
        initial = fit[best]

        evolving = True
        gen = 0
        while evolving:
            fit = self._fitness(teams)
            best = np.argmax(fit)
            best_fit = fit[best]
            self._progress(prev_fit, best_fit)
            prev_fit = best_fit
            teams = self._evolve(teams, prop=prop)
            gen += 1
            evolving = gen < gens

        self._summary(initial, best_fit)

        team_idx = teams[best]
        pkmns = self.pokemon.iloc[team_idx, :]
        rows = pkmns.shape[0]
        for row in range(rows):
            self.team.append(tools.frame_to_pokemon(pkmns.iloc[row, :]))

        return self.team

    def _progress(self, prev, best):
        """Prints progress."""

        prev_out = f"Progress: {prev:.2f}"
        out = f"Progress: {best:.2f}"
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

    def _population(self, size=(100, 6)):
        """Creates a team population."""

        n = self.pokemon.shape[0]
        teams = np.random.choice(n, size=size, replace=True)

        return teams

    def _evolve(self, teams, prop=0.5):
        """Evolves a team population."""

        sel = self._select(teams, prop=prop)
        evo = self._crossover(sel)
        evo = self._mutate(evo)

        n_pop = teams.shape[0]
        n_evo = evo.shape[0]
        n_rest = n_pop - n_evo

        if n_rest <= 0:
            return evo

        fit = self._fitness(teams)
        idx = np.argsort(fit)[::-1][:n_rest]
        best = teams[idx, :]
        evol = np.concatenate((best, evo), axis=0)

        return evol

    def _select(self, teams, prop=0.5, cross=2):
        """Selects a team subpopulation."""

        n = teams.shape[0]
        fit = self._fitness(teams)
        fit_sum = np.sum(fit)
        min_fit = np.amin(fit_sum)
        if min_fit < 0:
            fit_sum += np.abs(min_fit) * n
            fit += np.abs(min_fit)
        probs = fit / fit_sum

        rows = int(n * prop)
        idx_size = (rows, cross)
        idx = np.random.choice(n, size=idx_size, replace=True, p=probs)

        cols = teams.shape[1]
        sel_size = (rows, cols, cross)
        sel = np.zeros(sel_size)
        for col in range(cross):
            teams_idx = idx[:, col]
            sel[:, :, col] = teams[teams_idx, :]

        return sel

    def _fitness(self, teams, weight=0.25):
        """Evaluates fitness for a team population."""

        rows = teams.shape[0]
        fit = np.zeros((rows,))
        for row in range(rows):
            team_idx = teams[row, :]
            team = self.pokemon.iloc[team_idx, :]

            stats = team.iloc[:, tools.STAT_COLS].to_numpy(dtype=float)
            weaknesses = team.iloc[:, tools.WEAK_COLS].to_numpy(dtype=float)

            n_team = team.shape[0]
            stat_score = np.mean(np.sum(stats, axis=0))
            weak_score = np.sum(np.sum(weaknesses, axis=0)) / n_team

            stat_score /= tools.MAX_STAT
            weak_score /= tools.MIN_WEAK

            stat_score = np.minimum(stat_score, 1)
            weak_score = np.minimum(weak_score, 1)

            weak_score = 1 - weak_score
            fit[row] = weight * stat_score + (1 - weight) * weak_score

        return fit

    def _individual_fitness(self, team, weight=0.25):
        """Evaluates fitness for team members."""

        team_idx = team
        team = self.pokemon.iloc[team_idx, :]

        stats = team.iloc[:, tools.STAT_COLS].to_numpy(dtype=float)
        weaknesses = team.iloc[:, tools.WEAK_COLS].to_numpy(dtype=float)

        n_stats = stats.shape[1]
        n_types = weaknesses.shape[1]
        stat_scores = np.sum(stats, axis=1)
        weak_scores = np.sum(weaknesses, axis=1)

        stat_scores /= tools.MAX_STAT
        weak_scores /= tools.MIN_WEAK

        stat_scores = np.minimum(stat_scores, 1)
        weak_scores = np.minimum(weak_scores, 1)

        weak_scores = 1 - weak_scores

        fit = weight * stat_scores + (1 - weight) * weak_scores

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
            pokemon_fit = self._individual_fitness(pokemon)
            pokemon_best = np.argsort(pokemon_fit)[::-1][:cols]
            teams[row, :] = pokemon_best

        return teams

    def _mutate(self, teams, replace=2):
        """Mutates a team population."""

        n = self.pokemon.shape[0]
        n_teams = teams.shape[0]
        n_team = teams.shape[1]
        size = (n_teams, replace)
        replace_idx = np.random.choice(n_team, size=size, replace=True)
        new_idx = np.random.choice(n, size=size, replace=True)

        for row in range(n_teams):
            teams[row, replace_idx[row]] = new_idx[row]

        return teams
