import pstats
from pstats import SortKey

p = pstats.Stats("profile.txt")
p.sort_stats(SortKey.TIME)
p.print_stats("genetic_generator.py")