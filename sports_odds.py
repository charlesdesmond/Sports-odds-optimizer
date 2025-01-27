from flask import Flask, render_template, request, jsonify
import requests  # ADDED: To make API requests to The Odds API

app = Flask(__name__)

# ADD YOUR API KEY HERE
API_KEY = "f3cf261f37dd316b06bfebde63311efe"

@app.route("/")
def index():
    return render_template("index.html")

# UPDATED: Fetch sports dynamically from The Odds API
@app.route("/api/sports")
def get_sports():
    url = "https://api.the-odds-api.com/v4/sports"  # API endpoint for sports
    response = requests.get(url, params={"apiKey": API_KEY})

    if response.status_code == 200:
        return jsonify(response.json())  # Return the API's sports data as JSON
    else:
        return jsonify({"error": "Failed to fetch sports data"}), response.status_code

# UPDATED: Fetch games dynamically from The Odds API based on the selected sport
@app.route("/api/games")
def get_games():
    sport = request.args.get("sport")
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": "us",  # Fetch odds from US-based sportsbooks
        "markets": "h2h",  # Get head-to-head odds
        "oddsFormat": "decimal",  # Ensure decimal odds are returned
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        games = response.json()

        # Simplify the response to only include game ID, teams, and bookmakers
        simplified_games = []
        for game in games:
            simplified_games.append({
                "id": game["id"],
                "home_team": game["home_team"],
                "away_team": game["away_team"],
                "bookmakers": game["bookmakers"]
            })
        return jsonify(simplified_games)
    else:
        return jsonify({"error": "Failed to fetch games"}), response.status_code

# NEW: Fetch the best odds for both teams in a selected game
@app.route("/api/odds", methods=["GET"])
def get_odds():
    game_id = request.args.get("game_id")
    sport = request.args.get("sport")  # Pass sport to specify the league
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": "us",  # Fetch odds from US-based sportsbooks
        "markets": "h2h",  # Get head-to-head odds
        "oddsFormat": "decimal",  # Ensure decimal odds are returned
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        games = response.json()
        # Find the selected game
        selected_game = next((g for g in games if g["id"] == game_id), None)
        if not selected_game:
            return jsonify({"error": "Game not found"}), 404

        # Find the best odds for each team
        best_odds = {}
        for bookmaker in selected_game["bookmakers"]:
            for outcome in bookmaker["markets"][0]["outcomes"]:
                team = outcome["name"]
                odds = outcome["price"]
                if team not in best_odds or odds > best_odds[team]["odds"]:
                    best_odds[team] = {"odds": odds, "bookmaker": bookmaker["title"]}

        return jsonify(best_odds)
    else:
        return jsonify({"error": "Failed to fetch odds"}), response.status_code

@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    odds1 = float(data.get("odds1", 0))
    odds2 = float(data.get("odds2", 0))
    stake = float(data.get("stake", 0))

    # Arbitrage calculation
    bet1 = round(stake / (odds2 * ((1 / odds1) + (1 / odds2))), 2)
    bet2 = round(stake / (odds1 * ((1 / odds1) + (1 / odds2))), 2)
    payout = round(bet1 * odds1, 2)
    roi = round(((payout - stake) / stake) * 100, 2)

    return jsonify({
        "Bet 1": bet1,
        "Bet 2": bet2,
        "Payout": payout,
        "ROI": roi
    })

if __name__ == "__main__":
    app.run(debug=True)