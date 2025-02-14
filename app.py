import os
import json
import logging
from flask import Flask, render_template, jsonify
import openai
from api import fetch_live_matches, fetch_match_details, fetch_match_statistics, fetch_match_scorers, fetch_match_incidents

# Configura il logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Recupera la chiave API di OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    logger.error("ERRORE: La chiave API di OpenAI non è stata trovata nelle variabili d'ambiente!")
else:
    openai.api_key = openai_api_key

def generate_commentary(match_data):
    """Genera un commento breve sulla partita utilizzando GPT-3.5."""
    
    if not openai.api_key:
        logger.error("Tentativo di usare OpenAI senza chiave API!")
        return "Errore: API Key mancante."

    # **DEBUG: Verifica se i dati della partita sono validi**
    logger.info("\n=== DEBUG: DATI PARTITA ===\n%s", json.dumps(match_data, indent=4))

    if not match_data or "event" not in match_data:
        return "Errore: Dati partita non validi."

    # Protezione per evitare crash se i dati sono incompleti
    try:
        home_team = match_data["event"]["homeTeam"]["name"]
        away_team = match_data["event"]["awayTeam"]["name"]
        home_score = match_data["event"]["homeScore"]["display"]
        away_score = match_data["event"]["awayScore"]["display"]
    except KeyError as e:
        logger.error(f"Errore nei dati della partita: {e}")
        return "Errore: Dati partita incompleti."

    # Creiamo il prompt per ChatGPT
    prompt = f"""
    Sei un commentatore sportivo. Analizza brevemente la partita tra {home_team} e {away_team}.
    Risultato: {home_score} - {away_score}.
    Sii conciso e oggettivo.
    """

    try:
        logger.info("Invio richiesta a OpenAI...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Fornisci un'analisi breve e concisa della partita."},
                      {"role": "user", "content": prompt}],
            max_tokens=50,
            timeout=5  # Timeout breve per evitare attese lunghe
        )
        
        commento = response["choices"][0]["message"]["content"].strip()
        logger.info("Commento generato: %s", commento)
        return commento
    
    except Exception as e:
        logger.error("\n=== DEBUG: ERRORE GPT ===\n%s", str(e))
        return f"Errore nella generazione del commento: {str(e)}"

@app.route("/")
def index():
    """Mostra le partite in diretta."""
    live_matches = fetch_live_matches()
    
    if "error" in live_matches:
        return render_template("index.html", error=live_matches["error"])

    return render_template("index.html", matches=live_matches.get("events", []))

@app.route("/match/<match_id>")
def match_details(match_id):
    """Mostra i dettagli di una partita specifica."""
    match_data = fetch_match_details(match_id)
    statistics = fetch_match_statistics(match_id)
    scorers = fetch_match_scorers(match_id)
    incidents = fetch_match_incidents(match_id)

    if "error" in match_data:
        return jsonify(match_data)

    # **Aggiungiamo il commento generato da OpenAI**
    commento_chatgpt = generate_commentary(match_data)

    return render_template("match.html", match=match_data, statistics=statistics, scorers=scorers, incidents=incidents, commento=commento_chatgpt)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
