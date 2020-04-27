"""
Methods for calculating the expected numbers of levelled NPCs in D&D world populations.
"""
import sys
from typing import Dict

from scipy import optimize

_MAX_ITER = 1000

ONE_MILLION = 1_000_000
NUM_LEVELS = 20 + 1  # for level "0"


def demographic(population: int, lvl_20_ratio: int = ONE_MILLION) -> Dict[int, int]:
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


def calc_geometric_ratio(target_sum: int, num_levels: int = NUM_LEVELS) -> float:
    """
    Calculate the needed ratio to make a geometric series which sums to the right total.

    Args:
        target_sum:
            The target sum for the geometric series.
        num_levels:
            The number of levels and hence terms in the geometric series.

    Returns:
        The calculated ratio.
    """
    # r = 1 represents a trivial solution so the base must be larger than that
    # r = 10 gives a target sum of 1.11E20 (for 21 levels) so unlikely we'll ever be looking that high!
    lower = 1. + sys.float_info.epsilon
    upper = _get_rough_upper(target_sum, num_levels)

    solution = optimize.root_scalar(ratio_formula, args=(target_sum,), bracket=[lower, upper])
    if solution.converged:
        return solution.root
    else:
        raise ValueError(f"Cannot find acceptable ratio for target sum of {target_sum} with {num_levels} levels.")


def _get_rough_upper(target_sum: int, num_levels: int = NUM_LEVELS):
    """Calculate a rough upper bound for the ratio by simply running through the numbers"""
    if num_levels <= 1:
        raise ValueError("Number of levels must be greater than 1 for geometric series to work.")

    # Start at 2 as 1 is invalid
    upper = 2
    while True:
        if _geo_sum(upper, num_levels) > target_sum:
            return upper
        elif upper > _MAX_ITER:
            raise ValueError(f"Unable to find appropriate upper bound before reaching {_MAX_ITER=} iterations.")
        upper += 1


def _geo_sum(r: int, n: int):
    """Calculate the geometric sum for ratio, r, and number of terms, n."""
    return (1 - r ** n) / (1 - r)


def ratio_formula(x: float, target_sum: int, num_levels: int = NUM_LEVELS) -> float:
    """
    A function representing the ratio formula found from rearranging the geometric series sum formula to make it
    possible to find the roots:

    S = (1-r^n)/(1-r) => r^n - Sr + S-1 = 0

    i.e. y = x^n - cx + c-1

    Args:
        x:
            Input value
        target_sum:
            The target sum we are trying to get.
        num_levels:
            The number of levels and hence terms in the series.

    Returns:
        The evaluated value of the formula
    """
    return (x ** num_levels) - (target_sum * x) + target_sum - 1
