import http.client
import json
import os

# Configura l'host e l'API key
RAPIDAPI_HOST = "allsportsapi2.p.rapidapi.com"
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")  # Usa la chiave API dai secrets

# Funzione per ottenere le partite in corso
def fetch_live_matches():
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    }

    conn.request("GET", "/api/matches/live", headers=headers)
    res = conn.getresponse()
    data = res.read()

    try:
        return json.loads(data.decode("utf-8"))
    except json.JSONDecodeError:
        return {"error": "Errore nella decodifica della risposta API"}

# Funzione per ottenere i dettagli di una partita
def fetch_match_details(match_id):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    }

    endpoint = f"/api/match/{match_id}"
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()
    data = res.read()

    try:
        return json.loads(data.decode("utf-8"))
    except json.JSONDecodeError:
        return {"error": "Errore nella decodifica della risposta API"}

# Funzione per ottenere il logo della competizione
def fetch_tournament_logo(tournament_id):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    }

    endpoint = f"/api/tournament/{tournament_id}/image"
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()

    if res.status == 200:
        return f"https://allsportsapi2.p.rapidapi.com/api/tournament/{tournament_id}/image"
    else:
        return None
