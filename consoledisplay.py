

def print_match_details(fighter1, fighter2, Pa, Pb):
    print("MATCH :: Fighter: {0} [ W: {1} | L: {2} | W%: {3} | R: {4:.0f}] Fighter: {5} [ W: {6} | L: {7} | W%: {8} | R: {9:.0f} ]".format(fighter1['fighter'], fighter1['wins'], fighter1['losses'], fighter1['win_ratio'], fighter1['elo'], fighter2['fighter'], fighter2['wins'], fighter2['losses'], fighter2['win_ratio'], fighter2['elo']))
    print("MATCH :: Fighter {0} has {1:.0%} probability of winning".format(fighter1['fighter'], Pa))
    print("MATCH :: Fighter {0} has {1:.0%} probability of winning".format(fighter2['fighter'], Pb))

def print_last_match_results(previous_balance, total_balance, placed_bet):
    if (previous_balance < total_balance):
        difference = total_balance - previous_balance
        print("WINNER :: ${}!".format(difference))
    elif (previous_balance > total_balance):
        difference = previous_balance - total_balance
        print("LOSER :: ${}!".format(difference))
    elif (placed_bet == False):
        print("- we did not place a bet-")
    else:
        print("Wait? Draws are possible? Or did you forget to bet? No change to balance.")

def print_welcome_message():
    print("WELCOME :: Let's GO!!!!!")

def print_user_stats(rank, streak, balance):
    print("USER STATS :: Rank: {0} | Bet Streak: {1} | Balance: {2}".format(rank, streak, balance))

def print_bet_details(fighter, wager, odds):
    potential_winning = wager * odds
    print("BET DETAILS :: Putting ${0} on {1} at {2:.2f} odds for a chance at ${3:.0f}".format(wager, fighter, odds, potential_winning))

def print_site_message(message):
    print("SALTY NOTE :: {}".format(message))

def print_winner(winner):
    print("MATCH RESULT: {} wins!".format(winner))