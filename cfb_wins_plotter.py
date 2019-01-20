#!/usr/bin
# Python Standard Library Imports
# Third Party Imports
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from adjustText import adjust_text


def parseData():
    """!"""
    # Parse conference teams from CSV files
    aac = pd.read_csv('data/aac.csv', header=1, usecols=[1, 3])
    acc = pd.read_csv('data/acc.csv', header=1, usecols=[1, 3])
    big10 = pd.read_csv('data/big10.csv', header=1, usecols=[1, 3])
    big12 = pd.read_csv('data/big12.csv', header=1, usecols=[1, 3])
    cusa = pd.read_csv('data/cusa.csv', header=1, usecols=[1, 3])
    ind = pd.read_csv('data/ind.csv', header=1, usecols=[1, 3])
    mac = pd.read_csv('data/mac.csv', header=1, usecols=[1, 3])
    mwc = pd.read_csv('data/mwc.csv', header=1, usecols=[1, 3])
    pac12 = pd.read_csv('data/pac12.csv', header=1, usecols=[1, 3])
    sec = pd.read_csv('data/sec.csv', header=1, usecols=[1, 3])
    sunbelt = pd.read_csv('data/sunbelt.csv', header=1, usecols=[1, 3])

    # Only add current teams in the conference
    year = 2018
    conf_data = {
        "AAC": (aac.where(aac['To'] >= year)).dropna()['School'].values,
        "ACC": (acc.where(acc['To'] >= year)).dropna()['School'].values,
        "Big 10": (big10.where(big10['To'] >= year)).dropna()['School'].values,
        "Big 12": (big12.where(big12['To'] >= year)).dropna()['School'].values,
        "CUSA": (cusa.where(cusa['To'] >= year)).dropna()['School'].values,
        "Independent": (ind.where(ind['To'] >= year)).dropna()['School'].values,
        "MAC": (mac.where(mac['To'] >= year)).dropna()['School'].values,
        "MWC": (mwc.where(mwc['To'] >= year)).dropna()['School'].values,
        "PAC 12": (pac12.where(pac12['To'] >= year)).dropna()['School'].values,
        "SEC": (sec.where(sec['To'] >= year)).dropna()['School'].values,
        "Sun Belt": (sunbelt.where(sunbelt['To'] >= year)).dropna()['School'].values
    }

    # Reformat data to be DFs with School and Conference columns
    conf_data_list = list()
    for conf, schools in conf_data.items():
        conf_list = [conf for ii in enumerate(schools)]
        conf_data_list.append(
            pd.DataFrame({'School': schools, 'Conference': conf_list})
        )

    # Concat all DFs into a single DF
    parsed_conf_data = pd.concat(conf_data_list, ignore_index=True)

    # Parse all team's win/loss data into DF
    all_win_loss_data = pd.read_csv('data/total_win_loss.csv', header=1, usecols=[1, 5, 6, 7, 8, 9])

    # Remove non-FBS teams
    fbs_schools = all_win_loss_data['School'].isin(parsed_conf_data['School'].values)
    school_idx = np.where(fbs_schools.values == False)[0]
    reduced_wins_data = all_win_loss_data.drop(school_idx)

    # Add conference data to wins data
    fbs_wins_data = reduced_wins_data.join(parsed_conf_data.set_index('School'), on='School')

    return fbs_wins_data


def plotData(stats, adjust=False):
    """!"""
    # Query information from cfb stats data
    names = stats.get('School').values
    confs = stats.get('Conference').values
    wins = stats.get('W').values
    losses = stats.get('L').values

    # Add conference-color mapping for legend
    conference_color = {}
    conf_handles = []
    conferences = set(stats['Conference'].values)
    colors = sns.color_palette("hls", len(conferences))
    for ii, conference in enumerate(conferences):
        conference_color[conference] = [colors[ii]]
        conf_handles.append(mpatches.Patch(color=colors[ii], label=conference))

    # Create plot object. Add data points and text schools
    fig, ax = plt.subplots(figsize=(12, 6))
    texts = []
    for w, l, name, conf in zip(wins, losses, names, confs):
        ax.scatter(l, w, s=4, c=conference_color[conf], label=conf)
        texts.append(ax.text(l, w, name, fontsize=6, verticalalignment='top', horizontalalignment='center'))

    # Add legend
    first_legend = plt.legend(handles=conf_handles, loc='upper left', title='Conferences')
    plt.gca().add_artist(first_legend)

    # Get max losses & wins
    max_losses = max(losses)
    max_wins = max(wins)
    low_line, med_line, high_line = [], [], []
    for ii in range(max_losses):
        low_line.append(ii*(1/3))
        med_line.append(ii)
        if ii*3 <= max_wins:
            high_line.append(ii*(3))

    # Add lines to plot & line legend
    high, = ax.plot(high_line, c='k', linestyle=(0, (5, 5)), label='0.750')
    med, = ax.plot(med_line, c='k', linestyle=(0, (5, 1)), label='0.500')
    low, = ax.plot(low_line, c='k', linestyle=(0, (3, 1, 1, 1)), label='0.250')
    plt.legend(handles=[low, med, high], loc='upper right', title='Win Percentage')

    # Add legend, labels, & grid
    plt.ylabel('Wins')
    plt.xlabel('Losses')
    plt.grid(True)
    plt.title('Total Wins vs. Total Losses - Unadjusted')
    plt.tight_layout()
    fig.set_dpi(1800)

    # Text adjustment
    if adjust:
        adjust_text(texts, autoalign='', only_move={'text':'y'}, arrowprops=dict(arrowstyle="-", color='r', lw=0.5))


if __name__ == "__main__":
    # Plot style
    plt.style.use('ggplot')

    # Parse & plot data
    cfb_stats = parseData()
    plotData(cfb_stats, adjust=True)

    # Save & show plot
    plt.savefig('output/cfb-adjusted.svg', dpi=1800, format='svg')
    plt.show()
