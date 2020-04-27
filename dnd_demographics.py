"""
Methods for calculating the expected numbers of levelled NPCs in D&D world populations.
"""
from typing import Dict

ONE_IN_A_MILLION = 1 / 1_000_000


def demographic(population: int, lvl_20_ratio: float = ONE_IN_A_MILLION) -> Dict[int, int]:
    """
    Calculate the number of levelled NPCs in a given population.

    Args:
        population:
            The population to consider these levelled NPCs in.
        lvl_20_ratio:
            The fraction of the population that should be level 20.

    Returns:
        A dict mapping the levels (0-20) to the number of NPCs at each level.
    """
    pass
