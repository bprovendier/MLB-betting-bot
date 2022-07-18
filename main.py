"""Main file putting everything together."""
from odd_scraping import choose_picks
from export import send_email, update_results

picks = choose_picks()
# Update result sheet with daily picks
picks.to_csv("mlb_picks.csv", mode="a", header=False, index=False)
print(picks)
roi = update_results()
send_email(picks, roi)
print("Succesfully sent!")
