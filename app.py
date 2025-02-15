from flask import Flask, jsonify
from api import fetch_tournament_logo

app = Flask(__name__)

@app.route("/test_logo/<int:tournament_id>")
def test_logo(tournament_id):
    logo_url = fetch_tournament_logo(tournament_id)
    return jsonify({"tournament_id": tournament_id, "logo_url": logo_url})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
