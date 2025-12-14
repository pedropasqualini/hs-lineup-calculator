"""
Core calculation engine.
This module contains the game theory and lineup calculation logic.
All algorithms are preserved exactly from the original implementation.
"""
import pandas as pd
import random as rd
from copy import deepcopy
from typing import Callable, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed

from .config import RANDOM_TARGET, NUM_ITERATIONS


# ============================================================================
# Game Theory Solver (Lemke-Howson Algorithm)
# This is a Python implementation of the Lemke-Howson algorithm
# Used to find Nash equilibrium in the ban phase
# ============================================================================

def solve(payoff_matrix: list, iterations: int = 1000) -> tuple:
    """
    Solve a payoff matrix for Nash equilibrium using Lemke-Howson algorithm.
    
    Returns:
        Tuple of (row_strategy, col_strategy, value_of_game)
    """
    from operator import add, neg
    
    transpose = list(zip(*payoff_matrix))
    numrows = len(payoff_matrix)
    numcols = len(transpose)
    row_cum_payoff = [0] * numrows
    col_cum_payoff = [0] * numcols
    colpos = list(range(numcols))
    rowpos = list(map(neg, range(numrows)))
    colcnt = [0] * numcols
    rowcnt = [0] * numrows
    active = 0
    
    for _ in range(iterations):
        rowcnt[active] += 1
        col_cum_payoff = list(map(add, payoff_matrix[active], col_cum_payoff))
        active = min(list(zip(col_cum_payoff, colpos)))[1]
        colcnt[active] += 1
        row_cum_payoff = list(map(add, transpose[active], row_cum_payoff))
        active = -max(list(zip(row_cum_payoff, rowpos)))[1]
    
    value_of_game = (max(row_cum_payoff) + min(col_cum_payoff)) / 2.0 / iterations
    return rowcnt, colcnt, value_of_game


# ============================================================================
# Conquest Bo5 Win Rate Calculation
# Calculates win probability after bans are determined
# ============================================================================

def conquest_bo5(mups: list, h1: int, h2: int, h3: int, v1: int, v2: int, v3: int) -> float:
    """
    Calculate chances of winning Bo5 conquest match after ban.
    Uses exact probability calculation for all game states.
    """
    # game 1
    A = (mups[h1][v1] + mups[h1][v2] + mups[h1][v3])/9
    B = (mups[h2][v1] + mups[h2][v2] + mups[h2][v3])/9
    C = (mups[h3][v1] + mups[h3][v2] + mups[h3][v3])/9

    D = (3 - mups[h1][v1] - mups[h2][v1] - mups[h3][v1])/9
    E = (3 - mups[h1][v2] - mups[h2][v2] - mups[h3][v2])/9
    F = (3 - mups[h1][v3] - mups[h2][v3] - mups[h3][v3])/9

    # game 2
    AB = (A*(mups[h2][v1] + mups[h2][v2] + mups[h2][v3]) +
          B*(mups[h1][v1] + mups[h1][v2] + mups[h1][v3]))/6
    AC = (A*(mups[h3][v1] + mups[h3][v2] + mups[h3][v3]) +
          C*(mups[h1][v1] + mups[h1][v2] + mups[h1][v3]))/6
    BC = (B*(mups[h3][v1] + mups[h3][v2] + mups[h3][v3]) +
          C*(mups[h2][v1] + mups[h2][v2] + mups[h2][v3]))/6

    AD = (A*(2 - mups[h2][v1] - mups[h3][v1]) +
          D*(mups[h1][v2] + mups[h1][v3]))/6
    AE = (A*(2 - mups[h2][v2] - mups[h3][v2]) +
          E*(mups[h1][v1] + mups[h1][v3]))/6
    AF = (A*(2 - mups[h2][v3] - mups[h3][v3]) +
          F*(mups[h1][v1] + mups[h1][v2]))/6
    BD = (B*(2 - mups[h1][v1] - mups[h3][v1]) +
          D*(mups[h2][v2] + mups[h2][v3]))/6
    BE = (B*(2 - mups[h1][v2] - mups[h3][v2]) +
          E*(mups[h2][v1] + mups[h2][v3]))/6
    BF = (B*(2 - mups[h1][v3] - mups[h3][v3]) +
          F*(mups[h2][v1] + mups[h2][v2]))/6
    CD = (C*(2 - mups[h1][v1] - mups[h2][v1]) +
          D*(mups[h3][v2] + mups[h3][v3]))/6
    CE = (C*(2 - mups[h1][v2] - mups[h2][v2]) +
          E*(mups[h3][v1] + mups[h3][v3]))/6
    CF = (C*(2 - mups[h1][v3] - mups[h2][v3]) +
          F*(mups[h3][v1] + mups[h3][v2]))/6

    DE = (D*(3 - mups[h1][v2] - mups[h2][v2] - mups[h3][v2]) +
          E*(3 - mups[h1][v1] - mups[h2][v1] - mups[h3][v1]))/6
    DF = (D*(3 - mups[h1][v3] - mups[h2][v3] - mups[h3][v3]) +
          F*(3 - mups[h1][v1] - mups[h2][v1] - mups[h3][v1]))/6
    EF = (E*(3 - mups[h1][v3] - mups[h2][v3] - mups[h3][v3]) +
          F*(3 - mups[h1][v2] - mups[h2][v2] - mups[h3][v2]))/6

    # game 3
    ABC = (AB*(mups[h3][v1] + mups[h3][v2] + mups[h3][v3]) +
           AC*(mups[h2][v1] + mups[h2][v2] + mups[h2][v3]) +
           BC*(mups[h1][v1] + mups[h1][v2] + mups[h1][v3]))/3

    ABD = AB*(1 - mups[h3][v1])/3 + AD*(mups[h2][v2] + mups[h2][v3])/4 + \
                                    BD*(mups[h1][v2] + mups[h1][v3])/4
    ABE = AB*(1 - mups[h3][v2])/3 + AE*(mups[h2][v1] + mups[h2][v3])/4 + \
                                    BE*(mups[h1][v1] + mups[h1][v3])/4
    ABF = AB*(1 - mups[h3][v3])/3 + AF*(mups[h2][v1] + mups[h2][v2])/4 + \
                                    BF*(mups[h1][v1] + mups[h1][v2])/4
    ACD = AC*(1 - mups[h2][v1])/3 + AD*(mups[h3][v2] + mups[h3][v3])/4 + \
                                    CD*(mups[h1][v2] + mups[h1][v3])/4
    ACE = AC*(1 - mups[h2][v2])/3 + AE*(mups[h3][v1] + mups[h3][v3])/4 + \
                                    CE*(mups[h1][v1] + mups[h1][v3])/4
    ACF = AC*(1 - mups[h2][v3])/3 + AF*(mups[h3][v1] + mups[h3][v2])/4 + \
                                    CF*(mups[h1][v1] + mups[h1][v2])/4
    BCD = BC*(1 - mups[h1][v1])/3 + BD*(mups[h3][v2] + mups[h3][v3])/4 + \
                                    CD*(mups[h2][v2] + mups[h2][v3])/4
    BCE = BC*(1 - mups[h1][v2])/3 + BE*(mups[h3][v1] + mups[h3][v3])/4 + \
                                    CE*(mups[h2][v1] + mups[h2][v3])/4
    BCF = BC*(1 - mups[h1][v3])/3 + BF*(mups[h3][v1] + mups[h3][v2])/4 + \
                                    CF*(mups[h2][v1] + mups[h2][v2])/4

    ADE = AD*(2 - mups[h2][v2] - mups[h3][v2])/4 + \
          AE*(2 - mups[h2][v1] - mups[h3][v1])/4 + DE*(mups[h1][v3])/3
    ADF = AD*(2 - mups[h2][v3] - mups[h3][v3])/4 + \
          AF*(2 - mups[h2][v1] - mups[h3][v1])/4 + DF*(mups[h1][v2])/3
    AEF = AE*(2 - mups[h2][v3] - mups[h3][v3])/4 + \
          AF*(2 - mups[h2][v2] - mups[h3][v2])/4 + EF*(mups[h1][v1])/3
    BDE = BD*(2 - mups[h1][v2] - mups[h3][v2])/4 + \
          BE*(2 - mups[h1][v1] - mups[h3][v1])/4 + DE*(mups[h2][v3])/3
    BDF = BD*(2 - mups[h1][v3] - mups[h3][v3])/4 + \
          BF*(2 - mups[h1][v1] - mups[h3][v1])/4 + DF*(mups[h2][v2])/3
    BEF = BE*(2 - mups[h1][v3] - mups[h3][v3])/4 + \
          BF*(2 - mups[h1][v2] - mups[h3][v2])/4 + EF*(mups[h2][v1])/3
    CDE = CD*(2 - mups[h1][v2] - mups[h2][v2])/4 + \
          CE*(2 - mups[h1][v1] - mups[h2][v1])/4 + DE*(mups[h3][v3])/3
    CDF = CD*(2 - mups[h1][v3] - mups[h2][v3])/4 + \
          CF*(2 - mups[h1][v1] - mups[h2][v1])/4 + DF*(mups[h3][v2])/3
    CEF = CE*(2 - mups[h1][v3] - mups[h2][v3])/4 + \
          CF*(2 - mups[h1][v2] - mups[h2][v2])/4 + EF*(mups[h3][v1])/3

    # game 4
    ABCD = (ABD*(mups[h3][v2] + mups[h3][v3]) +
            ACD*(mups[h2][v2] + mups[h2][v3]) +
            BCD*(mups[h1][v2] + mups[h1][v3]))/2
    ABCE = (ABE*(mups[h3][v1] + mups[h3][v3]) +
            ACE*(mups[h2][v1] + mups[h2][v3]) +
            BCE*(mups[h1][v1] + mups[h1][v3]))/2
    ABCF = (ABF*(mups[h3][v1] + mups[h3][v2]) +
            ACF*(mups[h2][v1] + mups[h2][v2]) +
            BCF*(mups[h1][v1] + mups[h1][v2]))/2

    ABDE = (ABD*(1 - mups[h3][v2]) + ABE*(1 - mups[h3][v1]) +
            ADE*mups[h2][v3] + BDE*mups[h1][v3])/2
    ABDF = (ABD*(1 - mups[h3][v3]) + ABF*(1 - mups[h3][v1]) +
            ADF*mups[h2][v2] + BDF*mups[h1][v2])/2
    ABEF = (ABE*(1 - mups[h3][v3]) + ABF*(1 - mups[h3][v2]) +
            AEF*mups[h2][v1] + BEF*mups[h1][v1])/2
    ACDE = (ACD*(1 - mups[h2][v2]) + ACE*(1 - mups[h2][v1]) +
            ADE*mups[h3][v3] + CDE*mups[h1][v3])/2
    ACDF = (ACD*(1 - mups[h2][v3]) + ACF*(1 - mups[h2][v1]) +
            ADF*mups[h3][v2] + CDF*mups[h1][v2])/2
    ACEF = (ACE*(1 - mups[h2][v3]) + ACF*(1 - mups[h2][v2]) +
            AEF*mups[h3][v1] + CEF*mups[h1][v1])/2
    BCDE = (BCD*(1 - mups[h1][v2]) + BCE*(1 - mups[h1][v1]) +
            BDE*mups[h3][v3] + CDE*mups[h2][v3])/2
    BCDF = (BCD*(1 - mups[h1][v3]) + BCF*(1 - mups[h1][v1]) +
            BDF*mups[h3][v2] + CDF*mups[h2][v2])/2
    BCEF = (BCE*(1 - mups[h1][v3]) + BCF*(1 - mups[h1][v2]) +
            BEF*mups[h3][v1] + CEF*mups[h2][v1])/2

    # game 5
    ABCDE = ABDE*mups[h3][v3] + ACDE*mups[h2][v3] + BCDE*mups[h1][v3]
    ABCDF = ABDF*mups[h3][v2] + ACDF*mups[h2][v2] + BCDF*mups[h1][v2]
    ABCEF = ABEF*mups[h3][v1] + ACEF*mups[h2][v1] + BCEF*mups[h1][v1]

    return ABC + ABCD + ABCE + ABCF + ABCDE + ABCDF + ABCEF


def ban_list_bo5(mups: list, hero_decks: list, villain_decks: list) -> list:
    """
    Calculate win chances for each ban option in Bo5 Conquest.
    
    Args:
        mups: Matchup matrix as 2D list
        hero_decks: List of 4 deck indices for the player
        villain_decks: List of 4 deck indices for the opponent
    
    Returns:
        4x4 matrix of win rates for each ban combination
    """
    final = [[] for _ in range(4)]
    
    for i in range(4):
        h_subset = hero_decks[:i] + hero_decks[i+1:]
        for j in range(4):
            v_subset = villain_decks[:j] + villain_decks[j+1:]
            final[i].append(conquest_bo5(mups, *h_subset, *v_subset))
    
    return final


# ============================================================================
# Field Generation
# Creates an artificial field based on deck frequencies
# ============================================================================

def alter_num_line(line: list, classes: dict, random_target: int) -> None:
    """Potentially alter lineup frequency based on deck representation."""
    change = 0
    for deck in range(4):
        if classes[line[deck]][1] > classes[line[deck]][0]:
            change += 1
        elif classes[line[deck]][0] > classes[line[deck]][1]:
            change -= 1
    
    if change > 0:
        if change > rd.randrange(random_target):
            line[4] += 1
            for deck in range(4):
                classes[line[deck]][0] += 1
    
    if change < 0:
        if line[4] == 0:
            return
        change = -change
        if change > rd.randrange(random_target):
            line[4] -= 1
            for deck in range(4):
                classes[line[deck]][0] -= 1


def generate_field(
    deck_pct: pd.Series,
    lineups: list,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    random_target: int = RANDOM_TARGET,
    num_iterations: int = NUM_ITERATIONS
) -> pd.DataFrame:
    """
    Generate artificial field of ~400 lineups based on deck frequencies.
    Uses iterative approach to approximate bell curve distribution.
    
    Args:
        deck_pct: Series with deck names as index and frequency as values
        lineups: List of all possible lineups
        progress_callback: Optional callback(progress, message)
        random_target: Randomness parameter (lower = less realistic)
        num_iterations: Number of iterations for field generation
    
    Returns:
        DataFrame with lineups and their frequencies
    """
    lineups_tmp = deepcopy(lineups)
    classes = {}
    
    for deck in deck_pct.index:
        classes[deck] = [0, deck_pct[deck] * 4]
    
    for line in lineups_tmp:
        line.append(0)
    
    for i in range(num_iterations):
        for line in lineups_tmp:
            alter_num_line(line, classes, random_target)
        
        if progress_callback and i % 100 == 0:
            progress = i / num_iterations
            progress_callback(progress, f"Generating field... {int(progress * 100)}%")
    
    # Remove empty lineups
    elements_to_remove = []
    for i in range(len(lineups_tmp)):
        if lineups_tmp[i][4] == 0:
            elements_to_remove.append(i)
    
    for element in elements_to_remove[::-1]:
        lineups_tmp.pop(element)
    
    df = pd.DataFrame(lineups_tmp)
    return df


# ============================================================================
# Lineup Calculation (Main Solver)
# ============================================================================

def solve_single_lineup(args: tuple) -> list:
    """
    Solve a single lineup against the entire field.
    This function is designed to be called in parallel.
    
    Args:
        args: Tuple of (mups_list, line, field, num_lines, reverse_translator)
    
    Returns:
        Line with appended win rate
    """
    mups_list, line, field_data, num_lines, reverse_translator = args
    value_line = 0
    
    for opp in field_data:
        hero_decks = [reverse_translator[l] for l in line[:4]]
        villain_decks = [reverse_translator[o] for o in opp[:4]]
        banlist = ban_list_bo5(mups_list, hero_decks, villain_decks)
        value_line += solve(banlist)[2] * opp[4]
    
    result = line.copy()
    result.append(value_line / num_lines)
    return result


def calculate_lineups(
    matchups: pd.DataFrame,
    field: pd.DataFrame,
    lineups: list,
    archetypes: pd.DataFrame,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    max_workers: Optional[int] = None
) -> pd.DataFrame:
    """
    Calculate win rates for all lineups against the field.
    
    Args:
        matchups: Matchup matrix DataFrame
        field: Field DataFrame with lineup frequencies
        lineups: List of all possible lineups
        archetypes: DataFrame with deck info
        progress_callback: Optional callback(progress, message)
        max_workers: Maximum parallel workers (None = auto)
    
    Returns:
        DataFrame with lineups and win rates, sorted by win rate
    """
    # Normalize matchups to 0-1 range
    matchups_normalized = matchups / 100
    matchups_list = matchups_normalized.values.tolist()
    
    num_lines = sum(field[4])
    
    # Create translators
    translator = archetypes['name'].to_dict()
    reverse_translator = {deck: index for index, deck in translator.items()}
    
    # Convert field to list for parallel processing
    field_data = field.values.tolist()
    
    # Prepare tasks
    tasks = [
        (matchups_list, line, field_data, num_lines, reverse_translator)
        for line in lineups
    ]
    
    results = []
    total = len(tasks)
    
    # Process with progress tracking
    # Note: Using ProcessPoolExecutor for CPU-bound work
    from multiprocessing import Pool
    
    completed = 0
    with Pool(processes=max_workers) as pool:
        for result in pool.imap_unordered(solve_single_lineup, tasks, chunksize=10):
            results.append(result)
            completed += 1
            if progress_callback and completed % 50 == 0:
                progress = completed / total
                progress_callback(progress, f"Calculating lineups... {completed}/{total}")
    
    if progress_callback:
        progress_callback(1.0, "Sorting results...")
    
    results_df = pd.DataFrame(results)
    sorted_results = results_df.sort_values(by=[4], ascending=False)
    
    return sorted_results
