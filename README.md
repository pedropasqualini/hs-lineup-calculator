# Hearthstone Lineup Calculator

## Overview

The Hearthstone Lineup Calculator is a software tool designed to calculate the win rates of lineups in competitive Hearthstone tournaments. By leveraging matchup data and mathematical algorithms, it provides insights into optimal deck lineups against a simulated tournament field.

## How It Works

### Data Input

The tool gathers data from HSReplay (or allows manual user input, though currently limited to decks available on HSReplay). Using this data:

It generates an artificial field of lineups based on the frequency of each deck.

The distribution of decks approximates a bell curve, ensuring realistic simulation conditions.

### Win Rate Calculation

For each lineup:

1. Matchup Simulation: Simulates all possible ban combinations and calculates the win rate of the player for each scenario.
2. Game Theory: Applies the Lemke-Howson algorithm to model perfect decision-making by both the player and the opponent.
3. Average Performance: Averages the results across all lineups and outputs a comprehensive CSV report.

## Supported Tournament Formats

The default configuration is for Conquest Best of 5 with ban. However, the tool supports additional formats through functions in ```analysis/series.py```, including Generalized Conquest (any number of decks) and Last Hero Standing.

## Usage Instructions

### Environment Setup

Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure the configurations.py file to match your needs, and then run the script:
```bash
python3 main.py
```
It was developed using Python 3.9.17.

### Using HSReplay Advanced Filters

If using HSReplay advanced filters, you'll need cookies from an HSReplay Premium account.

Create a ```.env``` file and input your cookies in the following format:
```
COOKIES='...'
``` 
### Using Custom Input Files

Examples of the expected input file format are available in the data folder.

Ensure deck names match the exact names used in HSReplay (to correctly identify each archetype's class).

Set the ```USER_INPUT``` flag to ```True``` in the configuration file.

## Optimizing Performance

If the script takes too long, adjust the MIN_GAMES parameter in the configuration. Increasing this value can reduce the number of decks analyzed, ideally resulting in about ~20 decks.

## Future Plans

While I do not intend to make major updates to this code due to no longer competing, I am happy to assist friends or others interested in using it. Feel free to reach out if you need help—you know where to find me!
