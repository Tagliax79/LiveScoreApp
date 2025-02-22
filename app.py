import os
import json
from flask import Flask, render_template, jsonify
import openai
from api import (fetch_live_matches,
                 fetch_match_details,
                 fetch_match_statistics,
                 fetch_match_scorers,
                 fetch_match_incidents,
                 fetch_tournament_logo)

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

    match_phase = f"La partita è attualmente in corso ({status})."
    if "HT" in status or "Intervallo" in status or "Half-time" in status:
        match_phase = "Il primo tempo si è appena concluso."
    elif "FT" in status or "Terminata" in status or "Full-time" in status:
        match_phase = "La partita è terminata."

    # Statistiche
    stats_text = ""
    if statistics and "statistics" in statistics:
        for stat_group in statistics["statistics"]:
            if stat_group["period"] == "ALL":
                for group in stat_group["groups"]:
                    stats_text += f"{group['groupName']}:\n"
                    for stat in group["statisticsItems"]:
                        stats_text += f"- {stat['name']}: {home_team} {stat['home']} - {stat['away']} {away_team}\n"

    # Eventi salienti
    event_text = ""
    if incidents and "incidents" in incidents:
        for event in incidents["incidents"]:
            team_name = event.get("team", {}).get("name", "Sconosciuto")
            if event["incidentType"] == "goal":
                event_text += f"⚽ Gol di {event['player']['name']} per il {team_name} al minuto {event['time']}!\n"
            elif event["incidentType"] == "card":
                if event["incidentClass"] == "yellow":
                    event_text += f"🟨 Ammonizione per {event['player']['name']} ({team_name}) al {event['time']}'.\n"
                elif event["incidentClass"] == "red":
                    event_text += f"🟥 ESPULSIONE! {event['player']['name']} del {team_name} al {event['time']}'.\n"
            elif event["incidentType"] == "substitution":
                event_text += f"🔄 Cambio: {event['playerOut']['name']} esce, entra {event['playerIn']['name']} per il {team_name} al {event['time']}'.\n"

    # Prompt per ChatGPT
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
        print(str(e))
        return f"Errore nella generazione del commento: {str(e)}"


@app.route("/")
def index():
    live_matches = fetch_live_matches()
    if "error" in live_matches:
        return render_template("index.html", error=live_matches["error"])

    # Raggruppiamo le partite per Paese e Competizione
    grouped_matches = {}
    # Aggiungiamo un dizionario logos, se vogliamo usarlo poi in index.html
    # (ma qui non è strettamente necessario: stiamo solo restituendo grouped_matches)
    
    for match in live_matches.get("events", []):
        country = match["tournament"]["category"]["name"]
        tournament_id = match["tournament"]["id"]
        tournament_name = match["tournament"]["name"]

        # Creiamo la struttura raggruppata
        if country not in grouped_matches:
            grouped_matches[country] = {}
        if tournament_name not in grouped_matches[country]:
            grouped_matches[country][tournament_name] = []
        
        grouped_matches[country][tournament_name].append(match)

    # Ritorniamo la pagina index.html
    return render_template("index.html", matches=grouped_matches)


@app.route("/match/<match_id>")
def match_details(match_id):
    match_data = fetch_match_details(match_id)
    # Se usi scorers/incidents/statistics
    # scorers = fetch_match_scorers(match_id)
    # incidents = fetch_match_incidents(match_id)
    # statistics = fetch_match_statistics(match_id)
    
    if "error" in match_data:
        return jsonify(match_data)

    # Esempio: se vuoi generare il commento
    # commento_chatgpt = generate_commentary(match_data, statistics, incidents)
    # return render_template("match.html",
    #                       match=match_data,
    #                       statistics=statistics,
    #                       scorers=scorers,
    #                       incidents=incidents,
    #                       commento=commento_chatgpt)

    # Oppure, se non vuoi generare il commento:
    return render_template("match.html", match=match_data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
