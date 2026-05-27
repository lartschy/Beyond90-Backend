def predict_score(stats, team1, team2):

    t1 = stats[team1]
    t2 = stats[team2]

    home_xg = (t1["attack"] + t2["defense"]) / 2 * 1.2
    away_xg = (t2["attack"] + t1["defense"]) / 2

    return round(home_xg), round(away_xg)