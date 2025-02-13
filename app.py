import os
import openai
from flask import Flask, render_template, jsonify
from api import fetch_live_matches, fetch_match_details, fetch_match_statistics, fetch_match_scorers, fetch_match_incidents

app = Flask(__name__)

# Recupera la chiave API di OpenAI dalle variabili d'ambiente
openai.api_key = os.getenv("OPENAI_KEY")

# Funzione per generare un commento sulla partita usando ChatGPT
def generate_commentary(match_data):
    try:
        prompt = f"Descrivi la partita tra {match_data['event']['homeTeam']['name']} e {match_data['event']['awayTeam']['name']}. Il punteggio finale è stato {match_data['event']['homeScore']['display']} - {match_data['event']['awayScore']['display']}."

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "Sei un commentatore sportivo."},
                      {"role": "user", "content": prompt}]
        )

        comment = response["choices"][0]["message"]["content"].strip()
        print(f"Commento ChatGPT: {comment}")  # Debug per controllare nei log
        return comment

    except Exception as e:
        print(f"Errore nella generazione del commento: {e}")
        return "Non è stato possibile generare un commento per questa partita."

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

    # Genera il commento usando OpenAI
    commento_chatgpt = generate_commentary(match_data)

    return render_template("match.html", match=match_data, statistics=statistics, scorers=scorers, incidents=incidents, commento=commento_chatgpt)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Usa la porta dinamica fornita da Render
    app.run(host="0.0.0.0", port=port)
