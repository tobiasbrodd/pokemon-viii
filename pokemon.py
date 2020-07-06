from enum import Enum


class Pokemon:
    def __init__(
        self,
        no,
        name,
        types,
        stats,
        weaknesses,
        stage=1,
        is_final=False,
        is_legendary=False,
        is_mythical=False,
    ):
        self.no = no
        self.name = name
        self.type_1 = None if len(types) < 1 else types[0]
        self.type_2 = None if len(types) < 2 else types[1]
        self.stage = stage
        self.is_final = is_final
        self.is_legendary = is_legendary
        self.is_mythical = is_mythical
        self.hp = stats[Stats.HP]
        self.attack = stats[Stats.ATTACK]
        self.defense = stats[Stats.DEFENSE]
        self.sp_attack = stats[Stats.SP_ATTACK]
        self.sp_defense = stats[Stats.SP_DEFENSE]
        self.speed = stats[Stats.SPEED]
        self.weaknesses = weaknesses

    def __str__(self):
        strings = []

        for var in vars(self):
            attr = getattr(self, var)
            if attr is None:
                attr = ""
            elif var == "weaknesses":
                attr = ",".join([str(val) for val in list(attr.values())])
            elif isinstance(attr, bool):
                attr = int(attr)
            elif isinstance(attr, Type):
                attr = attr.value
            strings.append(f"{attr}")

        return ",".join(strings)

    def get_total_stat(self):
        return (
            self.hp
            + self.attack
            + self.defense
            + self.sp_attack
            + self.sp_defense
            + self.speed
        )


class Type(Enum):
    NORMAL = "normal"
    FIRE = "fire"
    WATER = "water"
    ELECTRIC = "electric"
    GRASS = "grass"
    ICE = "ice"
    FIGHTING = "fighting"
    POISON = "poison"
    GROUND = "ground"
    FLYING = "flying"
    PSYCHIC = "psychic"
    BUG = "bug"
    ROCK = "rock"
    GHOST = "ghost"
    DRAGON = "dragon"
    DARK = "dark"
    STEEL = "steel"
    FAIRY = "fairy"


class Stats(Enum):
    HP = "hp"
    ATTACK = "attack"
    DEFENSE = "defense"
    SP_ATTACK = "sp_attack"
    SP_DEFENSE = "sp_defense"
    SPEED = "speed"
    TOTAL = "total"
