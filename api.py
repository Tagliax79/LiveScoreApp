import http.client
import base64
import os

RAPIDAPI_HOST = "allsportsapi2.p.rapidapi.com"
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

def fetch_tournament_logo(tournament_id):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    }

    endpoint = f"/api/tournament/{tournament_id}/image"
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()
    
    if res.status == 200 and res.getheader('Content-Type') == 'image/png':
        image_data = res.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        return f"data:image/png;base64,{base64_image}"
    
    return None
