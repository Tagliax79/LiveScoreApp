import os
import json
from flask import Flask, render_template, jsonify
import openai
from api import fetch_live_matches, fetch_match_details, fetch_match_statistics, fetch_match_scorers, fetch_match_incidents

app = Flask(__name__)

# Imposta la chiave API di OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_commentary(match_data, statistics):
    """Genera un commento dettagliato sulla partita utilizzando GPT-3.5."""
    
    if not openai.api_key:
        return "Errore: API Key mancante."

    if not match_data or "event" not in match_data:
        return "Errore: Dati partita non validi."

    # Raccolta statistiche
    stats_text = ""
    if statistics and "statistics" in statistics:
        for stat_group in statistics["statistics"]:
            if stat_group["period"] == "ALL":
                for group in stat_group["groups"]:
                    stats_text += f"{group['groupName']}:\n"
                    for stat in group["statisticsItems"]:
                        stats_text += f"- {stat['name']}: {match_data['event']['homeTeam']['name']} {stat['home']} - {stat['away']} {match_data['event']['awayTeam']['name']}\n"
    
    # Prompt dettagliato
    prompt = f"""
    Sei un esperto commentatore sportivo. Analizza la partita tra {match_data['event']['homeTeam']['name']} e {match_data['event']['awayTeam']['name']}.
    Risultato: {match_data['event']['homeScore']['display']} - {match_data['event']['awayScore']['display']}.
    Analizza i dati principali come possesso palla, tiri, contrasti, falli e ammonizioni.
    
    STATISTICHE:
    {stats_text}

    Genera un commento dettagliato che descriva l'andamento della partita in modo chiaro e obiettivo.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Fornisci un'analisi dettagliata della partita."},
                      {"role": "user", "content": prompt}],
            max_tokens=200,  # Aumentato per evitare tagli
            timeout=5  
        )
        return response["choices"][0]["message"]["content"].strip()
    
    except Exception as e:
        print("\n=== DEBUG: ERRORE GPT ===")
        print(str(e))  # Stampa l'errore della chiamata a OpenAI
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

    # **Aggiungiamo il commento generato da OpenAI**
    commento_chatgpt = generate_commentary(match_data, statistics)

    return render_template("match.html", match=match_data, statistics=statistics, scorers=scorers, incidents=incidents, commento=commento_chatgpt)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
