import os
from flask import Flask, render_template, jsonify
from api import fetch_live_matches, fetch_match_details, fetch_tournament_logo

app = Flask(__name__)

@app.route("/")
def index():
    live_matches = fetch_live_matches()

    if "error" in live_matches:
        return render_template("index.html", error=live_matches["error"])

    grouped_matches = {}

    for match in live_matches.get("events", []):
        country = match["tournament"]["category"]["name"]
        tournament_id = match["tournament"]["id"]
        tournament_name = match["tournament"]["name"]

        if country not in grouped_matches:
            grouped_matches[country] = {}

        if tournament_name not in grouped_matches[country]:
            grouped_matches[country][tournament_name] = {
                "matches": [],
                "logo": fetch_tournament_logo(tournament_id)
            }

        grouped_matches[country][tournament_name]["matches"].append(match)

    return render_template("index.html", matches=grouped_matches)

@app.route("/match/<match_id>")
def match_details(match_id):
    match_data = fetch_match_details(match_id)

    if "error" in match_data:
        return jsonify(match_data)

    return render_template("match.html", match=match_data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
