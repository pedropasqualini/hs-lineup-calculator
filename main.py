import pandas as pd
import analysis.series as se
import analysis.gt_solver as gt
from tqdm import tqdm
from multiprocessing import Pool
from request_data import request_all_data
from create_field import generate_field
from loguru import logger
from configuration import OUTPUT_PATH
import os

def get_index(arcs, deck):
    return arcs[arcs['name'] == deck].index[0]

def solve_line(task):
    mups_list, line, field_art, num_lines, reverse_translator = task
    value_line = 0
    for _, opp in field_art.iterrows():
        hero_decks = [reverse_translator[l] for l in line[:4]]
        villain_decks = [reverse_translator[o] for o in opp[:4]]
        banlist = se.banList_bo5(mups_list, hero_decks, villain_decks)
        value_line += gt.solve(banlist)[2]*opp[4]

    line.append(value_line/num_lines)
    return line

def main():
    matchups, lineups, deck_pct, arcs = request_all_data()
    field = generate_field(deck_pct, lineups)
    matchups = matchups / 100
    matchups_list = matchups.values.tolist()

    results = []

    num_lines = sum(field[4])

    translator = arcs['name'].to_dict()
    reverse_translator = {deck:index for index, deck in translator.items()}
    tasks = [(matchups_list, line, field, num_lines, reverse_translator) for line in lineups]
    with Pool() as pool:
        for r in tqdm(pool.imap_unordered(solve_line, tasks), total=len(tasks), desc="Calculating the best lineups..."):
            results.append(r)
    results_df = pd.DataFrame(results)
    sorted_results = results_df.sort_values(by=[4],ascending=False)
    breakpoint()
    sorted_results.to_csv(OUTPUT_PATH,index=False,header=False)
    logger.success(f"Results saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    main()
