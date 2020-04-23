from generators.generator import Generator
import pandas as pd
import numpy as np
import tools


class NaiveGenerator(Generator):
    def __init__(
        self, pokemon, team_no=[], size=6, weights=None, utypes=False, uteam=False
    ):
        self.pokemon = pokemon
        self.team_no = team_no
        self.size = size
        self.utypes = utypes
        self.uteam = uteam
        self.team = []

        stats = self.pokemon.columns[tools.STAT_COLS]
        if weights is None:
            weights = np.ones((1, 6))
        self.weights = pd.DataFrame(weights, columns=stats)

    def generate(self):
        weaknesses, types = self._generate_weakness_chart()
        team_types = self._get_team_types()
        team_types = self._generate_team_types(weaknesses, types, team=team_types)
        self.team = self._get_team(team_types)

        return self.team

    def _generate_weakness_chart(self):
        types = tools.get_types(self.pokemon)
        indices = {}
        weaknesses = []
        for (i, t) in enumerate(types):
            type_1 = t[0]
            type_2 = t[1]
            fltr = np.logical_and(
                self.pokemon["type_1"] == type_1, self.pokemon["type_2"] == type_2
            )
            pkmn = self.pokemon.loc[fltr].head(1).to_numpy()
            weaknesses.append(pkmn[:, tools.WEAK_COLS].reshape(-1,))
            indices[t] = i

        all_types = self.pokemon.columns[tools.WEAK_COLS]
        weaknesses = np.asmatrix(weaknesses)
        multi_index = pd.MultiIndex.from_tuples(types)
        weaknesses = pd.DataFrame(weaknesses, index=multi_index, columns=all_types)

        return weaknesses, types

    def _get_team_types(self):
        team_types = []
        for no in self.team_no:
            pkmn = self.pokemon[self.pokemon["no"] == no]
            if pkmn.empty:
                continue
            pkmn = pkmn.head(1)
            team_types.append(*zip(pkmn["type_1"], pkmn["type_2"]))

        return team_types

    def _generate_team_types(self, weaknesses, types, team=[]):
        team_types = []
        weaknesses -= 1
        weaknesses *= 2
        chart = weaknesses
        split = len(team)

        for i in range(split):
            t = team[i]
            team_types.append(t)
            chart = update_chart(weaknesses, chart, t)

        for i in range(split, self.size):
            t = self._get_best_type(chart, types)
            chart = self._update_chart(weaknesses, chart, t)
            uteam_exists = self._is_unique_team(team_types, t)
            while (t in team_types and self.utypes) or (
                not uteam_exists and self.uteam
            ):
                if (chart.shape[0] <= len(team_types) and self.utypes) or (
                    self._unique_team_exists(team) and self.uteam
                ):
                    t = None
                    break
                t = self._get_best_type(chart, types)
                chart = self._update_chart(weaknesses, chart, t)
                uteam_exists = self._is_unique_team(team_types, t)
            if t is not None:
                team_types.append(t)

        return team_types

    def _get_best_type(self, chart, types):
        perf = np.sum(chart, axis=1)
        best = np.argmin(perf)

        return types[best]

    def _is_unique_team(self, team_types, t):
        n_team_type = len(list(filter(lambda tt: tt == t, team_types))) + 1
        fltr = np.logical_and(
            self.pokemon["type_1"] == t[0], self.pokemon["type_2"] == t[1]
        )
        n_pokemon = self.pokemon.loc[fltr].shape[0]

        return n_pokemon >= n_team_type

    def _unique_team_exists(self, team):
        n_pokemon = self.pokemon.shape[0]
        n_team = len(team)

        return n_pokemon <= n_team

    def _update_chart(self, weaknesses, chart, t):
        type_1 = t[0]
        type_2 = t[1]

        m, n = weaknesses.shape

        update = chart * 0

        type_weaknesses = weaknesses.loc[t, :]
        min_weakness = np.amin(type_weaknesses)
        weak_types = type_weaknesses[type_weaknesses == min_weakness]
        fltr = np.logical_and(weak_types.index != type_1, weak_types.index != type_2)
        update_types = weak_types.loc[fltr]
        update.loc[t, :][update_types.index] += 1

        type_weaknesses = weaknesses.loc[t, :]
        max_weaknesses = np.amax(type_weaknesses)
        strong_types = type_weaknesses[type_weaknesses == max_weaknesses].index
        effective = weaknesses[strong_types]
        update_indices = []
        update_types = []
        for row in range(m):
            weakness_types = effective.columns[(effective.iloc[row, :] < 0).values]
            e_type_1 = effective.index[row][0]
            e_type_2 = effective.index[row][1]
            not_in_strong_types = (e_type_1 not in strong_types) and (
                e_type_2 not in strong_types
            )
            if len(weakness_types) > 0 and not_in_strong_types:
                update_indices.append(row)
                update_types.append(weakness_types)

        for i in range(len(update_indices)):
            index = update_indices[i]
            weakness_types = update_types[i]
            update.iloc[index, :][weakness_types] -= 1

        chart = chart.add(update)

        return chart

    def _get_team(self, team_types):
        team = []

        for no in self.team_no:
            pkmn = self.pokemon[self.pokemon["no"] == no].squeeze()
            if pkmn.empty:
                continue
            team.append(tools.frame_to_pokemon(pkmn))

        if len(self.team_no) > 0:
            team_types = team_types[len(team) :]

        for t in team_types:
            pkmn = self._get_pokemon(team, t)
            if pkmn is not None:
                team.append(tools.frame_to_pokemon(pkmn))

        return team

    def _get_pokemon(self, team, t):
        type_1 = t[0]
        type_2 = t[1]
        fltr = np.logical_and(
            self.pokemon["type_1"] == type_1, self.pokemon["type_2"] == type_2
        )
        pkmns = self.pokemon.loc[fltr]
        if self.uteam:
            team_names = [p.name for p in team]
            pkmns = pkmns[~pkmns.loc[:, "name"].isin(team_names)]
        if pkmns.empty:
            return None
        stats = pkmns.iloc[:, tools.STAT_COLS]
        weighted_stats = stats.multiply(self.weights.to_numpy())
        index = weighted_stats.sum(axis=1).idxmax(axis=0)
        pkmn = pkmns.loc[index]

        return pkmn
