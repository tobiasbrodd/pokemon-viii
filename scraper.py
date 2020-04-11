from pokemon import Pokemon, Stats, Type
from multiprocessing import Manager, Process, Pool, cpu_count
from urllib import request as req
from functools import partial
from bs4 import BeautifulSoup
import requests
import time
import re


class PokemonScraper:
    def __init__(self):
        self.base_url = "https://www.serebii.net"
        self.dex_url = self.base_url + "/swordshield/galarpokedex.shtml"

    def get_urls(self):
        urls = []
        response = requests.get(self.dex_url)

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find_all("table", limit=2)[1]
        links = table.select("td:nth-child(3) > a")

        for a in links:
            urls.append(self.base_url + a["href"])

        return urls

    def get_pokemon(self, urls):
        manager = Manager()
        progress = manager.dict()
        failed = manager.dict()

        jobs = len(urls)
        job = Process(target=self.print_progress, args=(progress, jobs))
        job.start()

        workers = cpu_count()
        with Pool(workers) as pool:
            part = partial(self._get_pokemon, progress=progress, failed=failed)
            res = pool.map(part, urls)

        job.join()

        pokemon = list(filter(lambda p: p is not None, list(res)))

        return pokemon, failed

    def _get_pokemon(self, url, progress={}, failed={}):
        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.select("table.dextable:not(table[align])")

        try:
            table = tables[1]
            row = table.find_all("tr", limit=2)[1]
            cells = row.find_all("td", recursive=False)
            name_cell = cells[0]
            no_cell = cells[2]
            type_cell = cells[4]

            no = self._get_no(no_cell)
            name = self._get_name(name_cell)
            progress[name] = 0

            types = self._get_types(type_cell)

            table = tables[3]
            weaknesses = self._get_weaknesses(table)

            stage, is_final = self._get_stage_final(soup, name)

            table = tables[-1]
            stats = self._get_stats(table)

            progress[name] = 100
        except Exception as error:
            failed[url] = error
            progress[name] = 100

            return None

        return Pokemon(
            no, name, types, stats, weaknesses, stage=stage, is_final=is_final
        )

    def _get_no(self, cell):
        no_node = cell.select("tr:first-child td:nth-child(2)")[0]
        no = no_node.text.replace("#", "")

        return int(no)

    def _get_name(self, cell):
        return cell.text

    def _get_types(self, cell):
        tables = cell.find_all("table")
        if len(tables) > 0:
            table = tables[0]
            row = table.find_all("tr")[0]
            cell = row.find_all("td")[1]
        links = cell.find_all("a")

        return self._extract_types(links)

    def _get_weaknesses(self, table):
        rows = table.find_all("tr", limit=3, recursive=False)

        row = rows[1]
        links = row.select("td > a")
        weak_types = self._extract_types(links)

        row = rows[2]
        cells = row.find_all("td")
        weak_nums = [cell.text.replace("*", "") for cell in cells]

        return dict(zip(weak_types, weak_nums))

    def _get_stage_final(self, soup, name):
        table = soup.select("table.dextable[align]")[0]
        row = table.find_all("tr", recursive=False)[1]
        row = row.find_all("tr")[0]
        links = row.select("td.pkmn a")
        stages = {}
        for (i, a) in enumerate(links):
            link = a["href"]
            if link[-1] == "/":
                link = link[0:-1]
            evo = re.search(r"(?<=\/)(\w+\W*\w*)$", link).group().lower()
            if not (evo in stages):
                stages[evo] = i + 1
        name = name.lower().replace(" ", "")
        if name in stages:
            stage = stages[name]
            is_final = stage >= len(stages)
            return stage, is_final
        else:
            return 0, False

    def _get_stats(self, table):
        row = table.find_all("tr", limit=3, recursive=False)[2]
        cells = row.find_all("td")
        stat_cells = [cell.text for cell in cells]
        stats = {
            Stats.HP: stat_cells[1],
            Stats.ATTACK: stat_cells[2],
            Stats.DEFENSE: stat_cells[3],
            Stats.SP_ATTACK: stat_cells[4],
            Stats.SP_DEFENSE: stat_cells[5],
            Stats.SPEED: stat_cells[6],
        }

        return stats

    def _extract_types(self, links):
        types = []
        for a in links:
            match = re.search(r"(?<=\/)(\w+)(?=\.)", a["href"]).group().upper()
            if match == "PSYCHICT":
                match = "PSYCHIC"
            types.append(Type[match])

        return types

    def print_progress(self, progress, jobs):
        """Prints progress every second."""

        time.sleep(1)
        done = []
        empty_len = 0
        while len(done) < jobs:
            empty_str = " " * empty_len
            for (key, prog) in progress.items():
                if prog >= 100 and (key not in done):
                    done.append(key)
            print_str = f"Progress: {len(done):.0f}/{jobs:.0f}"
            empty_len = len(print_str)
            print(f"\r{empty_str}", end="")
            print(f"\r{print_str}", end="")
            time.sleep(1)

        empty_len = len(print_str)
        print(f"\r{empty_str}", end="")
        print(f"\rProgress: {jobs:.0f}/{jobs:.0f}")


class ImageScraper:
    def __init__(self):
        self.base_url = "https://www.serebii.net"
        self.image_url = self.base_url + "/swordshield/pokemon"

    def download_images(self, urls):
        failed = {}
        jobs = len(urls)
        empty_len = 0

        for (job, url) in enumerate(urls):
            empty_str = " " * empty_len
            print_str = f"Progress: {job:.0f}/{jobs:.0f} - {url}"
            empty_len = len(print_str)
            print(f"\r{empty_str}", end="")
            print(f"\r{print_str}", end="")

            url = str(url)
            while len(url) < 3:
                url = "0" + url
            try:
                req.urlretrieve(f"{self.image_url}/{url}.png", f"./images/{url}.png")
            except Exception as error:
                failed[url] = error

        empty_len = len(print_str)
        print(f"\r{empty_str}", end="")
        print(f"\rProgress: {jobs:.0f}/{jobs:.0f}")

        return failed
