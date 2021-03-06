"""
Methods for calculating the expected numbers of levelled NPCs in D&D world populations.
"""
import argparse
import random
import sys
from pprint import pprint
from typing import Dict, List

from scipy import optimize

_MAX_ITER = 1000

ONE_MILLION = 1_000_000
NUM_LEVELS = 20


def demographic(population: int, highest_lvl_ratio: int = ONE_MILLION, num_levels: int = NUM_LEVELS) -> Dict[int, int]:
    """
    Calculate the number of levelled NPCs in a given population.

    Args:
        population:
            The population to consider these levelled NPCs in.
        highest_lvl_ratio:
            The fraction of the population that should be of the highest level.
        num_levels:
            The number of levels to consider.

    Returns:
        A dict mapping the levels (0-highest) to the number of NPCs at each level.
    """
    # Generate the proportions of each level and scale to the desired population
    fractions = generate_per_level_fractions(highest_lvl_ratio, num_levels)
    rough_numbers = {(k + 1): (v * population) for k, v in enumerate(fractions)}

    # Take the rough numbers use the whole number part and probabilistically add the remainder
    final_numbers = dict()
    for level, rough_num in rough_numbers.items():
        num, extra_prob = divmod(rough_num, 1)
        if random.random() < extra_prob:
            num += 1
        final_numbers[level] = int(num)
    final_numbers[0] = population - sum(final_numbers.values())

    return final_numbers


def generate_per_level_fractions(highest_level_ratio: int, num_levels: int = NUM_LEVELS) -> List[float]:
    """
    Generates the per-level fractions to reach the target sum (i.e. the highest level ratio).

    Args:
        highest_level_ratio:
            The 1:highest_level_ratio ratio for the highest level; i.e. the target sum for the geometric series.
        num_levels:
            The number of levels to calculate the sum over.

    Returns:
        A list of fractions of the population, per-level.
    """
    ratio = calc_geometric_ratio(highest_level_ratio, num_levels)
    per_level = [(ratio ** i) / highest_level_ratio for i in range(num_levels)]

    # Change so that the highest level information is at the end
    per_level.reverse()
    return per_level


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate per-level demographic information for D&D. Given a target "
                                                 "ratio for the highest level in the population, creates an "
                                                 "exponentially decreasing ratio of each lower level to meet that "
                                                 "target.")
    parser.add_argument("--population", required=True, type=int,
                        help="The population size to consider.")
    parser.add_argument("--levels", type=int, default=20,
                        help="The number of levels to consider. A level \"0\" will automatically be added to capture "
                             "unlevelled NPCs. Default = 20.")
    parser.add_argument("--ratio", type=int, default=ONE_MILLION,
                        help="The 1:X frequency of the highest level in the population. Default = 1,000,000.")
    args = parser.parse_args()

    output = demographic(args.population, args.ratio, args.levels)

    pprint(output)
