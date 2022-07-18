"""Small functions and dictionnaries."""
import pandas as pd


def percentage2float(percentage):
    """
    Convert series containg percentage strings to series of float.

    Argument:
        percentage (Series.str).

    Returns:
        (Series.float).
    """
    temp = []
    for num in percentage:
        temp.append(float(num.strip("%")) / 100)
    return pd.Series(temp)


def change_name(team_short_name):
    """
    Convert abbrevation of team names into names that match model records.

    Argument:
        team_short_name (Series.str).

    Returns:
        matching_name (Series.str).
    """
    matching_name = []
    for team in team_short_name:
        matching_name.append(teamdict[team])
    return matching_name


def find_opponent(teams_index, all_teams):
    """
    Match playing team with its opponent and specify it is home or away game.

    Arguments:
        teams_index (list): list of index from 'Team' column.
        all_teams (Series): all events listed in order.

    Returns:
        opponents (Series): opponents column.
        home (Series): column specifying wheter home or away game.
    """
    opponents = []
    home = []
    for index in teams_index:
        if (index % 2) == 0:
            opponents.append(all_teams.iloc[index + 1])
            home.append("H")
        else:
            opponents.append(all_teams.iloc[index - 1])
            home.append("A")
    return opponents, home


teamdict = {
    "TB": "TBRays",
    "STL": "STLCardinals",
    "NYY": "NYYYankees",
    "NYM": "NYMMets",
    "KC": "KCRoyals",
    "MIN": "MINTwins",
    "SD": "SDPadres",
    "MIA": "MIAMarlins",
    "ATL": "ATLBraves",
    "CWS": "CHWWhite Sox",
    "BOS": "BOSRed Sox",
    "PHI": "PHIPhillies",
    "COL": "COLRockies",
    "LAA": "LAAAngels",
    "HOU": "HOUAstros",
    "BAL": "BALOrioles",
    "TOR": "TORBlue Jays",
    "PIT": "PITPirates",
    "SF": "SFGiants",
    "CHC": "CHCCubs",
    "MIL": "MILBrewers",
    "LAD": "LADDodgers",
    "CIN": "CINReds",
    "CLE": "CLEIndians",
    "OAK": "OAKAthletics",
    "ARI": "ARIDiamondbacks",
    "WSH": "WSHNationals",
    "TEX": "TEXRangers",
    "DET": "DETTigers",
    "SEA": "SEAMariners",
}
