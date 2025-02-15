import os
from flask import Flask, render_template, jsonify
from api import fetch_live_matches, fetch_match_details, fetch_tournament_logo

app = Flask(__name__)

@app.route("/")
def index():
    live_matches = fetch_live_matches()

    if "error" in live_matches:
        return render_template("index.html", error=live_matches["error"])

    return render_template("index.html", matches=live_matches.get("events", []))

@app.route("/test_logo/<int:tournament_id>")
def test_logo(tournament_id):
    logo_url = fetch_tournament_logo(tournament_id)
    return jsonify({"tournament_id": tournament_id, "logo_url": logo_url})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
