import os
from flask import Flask, render_template, jsonify
from api import fetch_live_matches, fetch_match_details, fetch_match_statistics, fetch_match_scorers, fetch_match_incidents

app = Flask(__name__)

@app.route("/")
def index():
    live_matches = fetch_live_matches()

    if "error" in live_matches:
        return render_template("index.html", error=live_matches["error"])

    return render_template("index.html", matches=live_matches.get("events", []))

@app.route("/match/<match_id>")
def match_details(match_id):
    match_data = fetch_match_details(match_id)
    statistics = fetch_match_statistics(match_id)
    scorers = fetch_match_scorers(match_id)
    incidents = fetch_match_incidents(match_id)

    if "error" in match_data:
        return jsonify(match_data)

    return render_template("match.html", match=match_data, statistics=statistics, scorers=scorers, incidents=incidents)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Usa la porta dinamica fornita da Render
    app.run(host="0.0.0.0", port=port)
