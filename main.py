import requests
import os
import time

# --- Configuration via Variables d'Environnement ---
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
STREAMER_NAME = os.getenv('STREAMER_NAME')

GITHUB_PAT = os.getenv('MY_GITHUB_PAT')
REPO_CIBLE = os.getenv('REPO_CIBLE')
WORKFLOW_ID = os.getenv('WORKFLOW_ID')

# Intervalle de vérification (3 minutes = 180 secondes)
CHECK_INTERVAL = 180

def get_twitch_token():
    """Récupère un jeton d'accès Twitch."""
    auth_res = requests.post(
        f'https://id.twitch.tv/oauth2/token?client_id={TWITCH_CLIENT_ID}&client_secret={TWITCH_CLIENT_SECRET}&grant_type=client_credentials'
    )
    return auth_res.json().get('access_token')

def is_streamer_live(token):
    """Vérifie si le streamer est en live."""
    headers = {'Client-ID': TWITCH_CLIENT_ID, 'Authorization': f'Bearer {token}'}
    try:
        res = requests.get(f'https://api.twitch.tv/helix/streams?user_login={STREAMER_NAME}', headers=headers)
        data = res.json().get('data', [])
        return len(data) > 0
    except Exception as e:
        print(f"Erreur lors de la vérification Twitch : {e}")
        return False

def is_workflow_already_running():
    """Vérifie si le workflow GitHub est déjà en cours d'exécution."""
    headers = {'Authorization': f'token {GITHUB_PAT}', 'Accept': 'application/vnd.github.v3+json'}
    url = f'https://api.github.com/repos/{REPO_CIBLE}/actions/workflows/{WORKFLOW_ID}/runs?status=in_progress'
    try:
        res = requests.get(url, headers=headers)
        runs = res.json().get('workflow_runs', [])
        return len(runs) > 0
    except Exception as e:
        print(f"Erreur lors de la vérification GitHub : {e}")
        return True # On préfère ne pas relancer en cas d'erreur API

def trigger_workflow():
    """Déclenche le workflow GitHub."""
    headers = {'Authorization': f'token {GITHUB_PAT}', 'Accept': 'application/vnd.github.v3+json'}
    url = f'https://api.github.com/repos/{REPO_CIBLE}/actions/workflows/{WORKFLOW_ID}/dispatches'
    data = {'ref': 'main'} 
    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 204:
        print("✅ Workflow cible lancé avec succès !", flush=True)
    else:
        print(f"❌ Erreur lors du lancement : {res.status_code}, {res.text}", flush=True)

def main():
    print(f"Démarrage du monitoring pour {STREAMER_NAME}...", flush=True)
    
    while True:
        # On récupère un nouveau token à chaque cycle ou on gère sa validité
        token = get_twitch_token()
        
        if token and is_streamer_live(token):
            print(f"[{time.strftime('%H:%M:%S')}] {STREAMER_NAME} est en LIVE.", flush=True)
            
            if not is_workflow_already_running():
                trigger_workflow()
            else:
                print("Le workflow tourne déjà, pause...", flush=True)
        else:
            print(f"[{time.strftime('%H:%M:%S')}] {STREAMER_NAME} est hors ligne.", flush=True)
        
        # Attente avant la prochaine vérification
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()