import os
import json
from flask import Flask, render_template, jsonify
import openai
from api import fetch_live_matches, fetch_match_details, fetch_match_statistics, fetch_match_scorers, fetch_match_incidents

app = Flask(__name__)

# Imposta la chiave API di OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_commentary(match_data, statistics, incidents):
    """Genera un commento dettagliato e coinvolgente sulla partita con stile giornalistico."""
    
    if not openai.api_key:
        return "Errore: API Key mancante."

    if not match_data or "event" not in match_data:
        return "Errore: Dati partita non validi."

    home_team = match_data["event"]["homeTeam"]["name"]
    away_team = match_data["event"]["awayTeam"]["name"]
    home_score = match_data["event"]["homeScore"]["display"]
    away_score = match_data["event"]["awayScore"]["display"]
    status = match_data["event"]["status"]["description"]

    # Determiniamo se la partita è in corso o conclusa
    if "HT" in status or "Intervallo" in status or "Half-time" in status:
        match_phase = "Il primo tempo si è appena concluso."
    elif "FT" in status or "Terminata" in status or "Full-time" in status:
        match_phase = "La partita è terminata."
    else:
        match_phase = f"La partita è attualmente in corso ({status})."

    # Raccolta statistiche principali
    stats_text = ""
    if statistics and "statistics" in statistics:
        for stat_group in statistics["statistics"]:
            if stat_group["period"] == "ALL":
                for group in stat_group["groups"]:
                    stats_text += f"{group['groupName']}:\n"
                    for stat in group["statisticsItems"]:
                        stats_text += f"- {stat['name']}: {home_team} {stat['home']} - {stat['away']} {away_team}\n"

    # Raccolta eventi principali (goal, cartellini, sostituzioni)
    event_text = ""
    if incidents and "incidents" in incidents:
        for event in incidents["incidents"]:
            if event["incidentType"] == "goal":
                event_text += f"⚽ Gol di {event['player']['name']} per il {event['team']['name']} al minuto {event['time']}!\n"
            elif event["incidentType"] == "card":
                if event["incidentClass"] == "yellow":
                    event_text += f"🟨 Ammonizione per {event['player']['name']} ({event['team']['name']}) al {event['time']}'.\n"
                elif event["incidentClass"] == "red":
                    event_text += f"🟥 ESPULSIONE! {event['player']['name']} del {event['team']['name']} al {event['time']}'.\n"
            elif event["incidentType"] == "substitution":
                event_text += f"🔄 Cambio: {event['playerOut']['name']} esce, entra {event['playerIn']['name']} per il {event['team']['name']} al {event['time']}'.\n"

    # Creazione del prompt per ChatGPT
    prompt = f"""
    Sei un commentatore sportivo esperto. Scrivi un commento coinvolgente e realistico sulla partita tra {home_team} e {away_team}.
    {match_phase}
    
    RISULTATO ATTUALE: {home_team} {home_score} - {away_score} {away_team}

    EVENTI SALIENTI:
    {event_text}

    STATISTICHE CHIAVE:
    {stats_text}

    Crea un'analisi dettagliata dello svolgimento della partita, parlando di chi sta dominando, eventuali sorprese e le prestazioni dei giocatori chiave.
    Il commento deve essere in stile giornalistico, avvincente e descrivere l'atmosfera della gara.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Fornisci un'analisi coinvolgente della partita."},
                      {"role": "user", "content": prompt}]
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
    commento_chatgpt = generate_commentary(match_data, statistics, incidents)

    return render_template("match.html", match=match_data, statistics=statistics, scorers=scorers, incidents=incidents, commento=commento_chatgpt)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
