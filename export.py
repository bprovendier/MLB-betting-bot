"""Module to export picks and updated excel result sheet."""
import smtplib, ssl
import pandas as pd
import datetime as dt
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def send_email(picks, roi):
    """
    Send picks table by email.

    Argument:
        picks (dataframe).
    """
    date = dt.datetime.now().strftime("%Y-%m-%d")
    subject = f"Sports Picks {date}"

    sender_email = ""
    receiver_email = ""
    password = ""

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    html_picks = picks.to_html(index=False)

    html = f"""\
    <html>
    <head></head>
    <body>
        Here are the MLB picks of the day. ENJOY!! <br>
        The current ROI is <b>{roi}%</b>. <br>
        {html_picks}
        
    </body>
    </html>
    """

    part1 = MIMEText(html, "html")
    message.attach(part1)

    with open("mlb_picks.csv", "rb") as file:
        message.attach(MIMEApplication(file.read(), Name="mlb_picks.csv"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


def update_results():
    """
    Update csv sheet with yesterday's results and compute ROI.

    Returns:
        updated_roi (str): total ROI freshly updated.
    """
    win = []
    team_score = []
    opponent_score = []

    url = "https://projects.fivethirtyeight.com/2022-mlb-predictions/games/"
    html = requests.get(url).content
    full_df = pd.read_html(html)

    columns_interest = ["Date", "Team", "Score"]
    yesterday1 = (dt.datetime.now() - dt.timedelta(days=1)).strftime("%#m/%#d")
    yesterday2 = (dt.datetime.now() - dt.timedelta(days=1)).strftime("%d/%m/%Y")

    selected_df = full_df[1][columns_interest]

    filtered_df = selected_df[selected_df["Date"].str.contains(yesterday1)].copy()
    filtered_df = filtered_df.reset_index(drop=True)

    result_csv = pd.read_csv("mlb_picks.csv")
    result_csv = result_csv.dropna(how="all")
    result_date = result_csv[result_csv["Date"].str.contains(yesterday2)]

    for team in result_date["Team"]:
        idx = filtered_df[filtered_df["Team"] == team].index.values
        score1 = filtered_df.at[idx[0], "Score"]
        score2 = (
            filtered_df.at[idx[0] + 1, "Score"]
            if (idx % 2) == 0
            else filtered_df.at[idx[0] - 1, "Score"]
        )
        if score1 > score2:
            win.append(1)
        else:
            win.append(0)
        team_score.append(score1)
        opponent_score.append(score2)
    indexes = list(result_date["Team"].index.values)
    n = 0
    for idx in indexes:
        result_csv.loc[idx, "Win"] = win[n]
        result_csv.loc[idx, "Team_score"] = team_score[n]
        result_csv.loc[idx, "Opponent_score"] = opponent_score[n]
        n += 1
    sum = 0
    win_only = len(result_csv["Win"].dropna())
    for n in range(win_only):
        sum += result_csv["Bookmaker_odds"].values[n] * result_csv["Win"].values[n]
    try:
        updated_roi = round(
            ((sum - win_only) / win_only) * 100,
            2,
        )
    except:
        updated_roi = 0
    result_csv.to_csv("mlb_picks.csv", index=False)

    return updated_roi
