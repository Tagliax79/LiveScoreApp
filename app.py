import os
from flask import Flask, render_template, jsonify
import openai
from api import fetch_live_matches, fetch_match_details, fetch_match_statistics, fetch_match_scorers, fetch_match_incidents

app = Flask(__name__)

# Imposta la chiave API di OpenAI
openai.api_key = os.getenv("OPENAI_KEY")

def generate_commentary(match_data):
    """Genera un commento breve sulla partita utilizzando GPT-3.5."""
    if not openai.api_key:
        return "Non è stato possibile generare un commento per questa partita."

    prompt = f"""
    Sei un commentatore sportivo. Analizza brevemente la partita tra {match_data['event']['homeTeam']['name']} e {match_data['event']['awayTeam']['name']}.
    Risultato: {match_data['event']['homeScore']['display']} - {match_data['event']['awayScore']['display']}.
    Sii conciso e oggettivo.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Fornisci un'analisi breve e concisa della partita."},
                      {"role": "user", "content": prompt}],
            max_tokens=50,  # Limita la lunghezza della risposta
            timeout=5  # Imposta un timeout breve per evitare attese lunghe
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Errore nella generazione del commento: {str(e)}"

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

    commento_chatgpt = generate_commentary(match_data)

    return render_template("match.html", match=match_data, statistics=statistics, scorers=scorers, incidents=incidents, commento=commento_chatgpt)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
