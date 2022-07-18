"""Odd scraping file for betting website and model."""
from pysbr import *
import datetime as dt
import pandas as pd
import requests
import pytz
from utils import change_name, percentage2float, find_opponent


def choose_picks():
    """
    Choose picks of the day based on odds and conditions.

    Returns:
        picks (dataframe): teams to bet on as well as odds and margin value.
    """
    betting_df = betting_odds()
    model_df = model_odds()

    combined_odds = pd.merge(betting_df, model_df, "left")
    combined_odds["Margin"] = round(
        ((combined_odds["decimal odds"] / combined_odds["Real odds"]) - 1) * 100, 2
    )
    combined_odds.columns = ["Team", "Bookmaker Odds", "Real odds", "Margin"]

    picks = combined_odds.loc[
        (combined_odds["Margin"] > 0)
        & (combined_odds["Bookmaker Odds"] >= 1.4)
        & (combined_odds["Bookmaker Odds"] <= 3.2),
        ["Team", "Bookmaker Odds", "Real odds", "Margin"],
    ]
    picks["Margin"] = picks["Margin"].astype(str) + "%"
    picks["Opponent"], picks["Home/Away"] = find_opponent(
        list(picks["Team"].index.values), combined_odds["Team"]
    )

    date = dt.datetime.now().strftime("%Y-%m-%d")
    picks["Date"] = date
    picks = picks[
        [
            "Date",
            "Team",
            "Opponent",
            "Home/Away",
            "Bookmaker Odds",
            "Real odds",
            "Margin",
        ]
    ].reset_index(drop=True)

    return picks


def betting_odds():
    """
    Get the current baseball odds from Bet365.

    Returns:
        bet_odds (dataframe): teams and their odds.
    """
    tz = pytz.timezone("America/New_York")
    date = dt.datetime.strptime(
        dt.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"
    )

    mlb = MLB()
    sb = Sportsbook()

    event = EventsByDate(mlb.league_id, date)
    cols = ["datetime", "event", "participant", "participant full name", "decimal odds"]

    current_lines = CurrentLines(
        event.ids(), mlb.market_ids("money-line"), sb.ids("Bovada")[0]
    )
    final = current_lines.dataframe(event)[cols]
    final["Team"] = change_name(final["participant"])
    final["decimal odds"] = round(final["decimal odds"], 2)
    necessary_columns = ["Team", "decimal odds"]

    bet_odds = final[necessary_columns]

    return bet_odds


def model_odds():
    """
    Get real odds based on model win probability.

    Returns:
        model_odds (dataframe): real odds from model.
    """
    url = "https://projects.fivethirtyeight.com/2022-mlb-predictions/games/"
    html = requests.get(url).content
    full_df = pd.read_html(html)

    columns_interest = ["Date", "Team", "Win prob.Chance of winning"]
    date = dt.datetime.now().strftime("%#m/%#d")
    selected_df = full_df[0][columns_interest]

    filtered_df = selected_df[selected_df["Date"].str.contains(date)].copy()
    filtered_df = filtered_df.reset_index(drop=True)

    filtered_df["Value"] = percentage2float(filtered_df["Win prob.Chance of winning"])

    filtered_df["Real odds"] = round(1 / filtered_df["Value"], 2)
    necessary_columns = ["Team", "Real odds"]

    model_odds = filtered_df[necessary_columns]

    return model_odds
