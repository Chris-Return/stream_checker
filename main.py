import requests
import os

# Configuration via les Secrets GitHub
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
STREAMER_NAME = os.getenv('STREAMER_NAME')

GITHUB_PAT = os.getenv('MY_GITHUB_PAT')
REPO_CIBLE = os.getenv('REPO_CIBLE')
WORKFLOW_ID = os.getenv('WORKFLOW_ID')

def is_streamer_live():
    auth_res = requests.post(
        f'https://id.twitch.tv/oauth2/token?client_id={TWITCH_CLIENT_ID}&client_secret={TWITCH_CLIENT_SECRET}&grant_type=client_credentials'
    )
    access_token = auth_res.json().get('access_token')
    
    headers = {'Client-ID': TWITCH_CLIENT_ID, 'Authorization': f'Bearer {access_token}'}
    res = requests.get(f'https://api.twitch.tv/helix/streams?user_login={STREAMER_NAME}', headers=headers)
    return len(res.json().get('data', [])) > 0

def is_workflow_already_running():
    headers = {'Authorization': f'token {GITHUB_PAT}', 'Accept': 'application/vnd.github.v3+json'}
    url = f'https://api.github.com/repos/{REPO_CIBLE}/actions/workflows/{WORKFLOW_ID}/runs?status=in_progress'
    res = requests.get(url, headers=headers)
    runs = res.json().get('workflow_runs', [])
    return len(runs) > 0

def trigger_workflow():
    headers = {'Authorization': f'token {GITHUB_PAT}', 'Accept': 'application/vnd.github.v3+json'}
    url = f'https://api.github.com/repos/{REPO_CIBLE}/actions/workflows/{WORKFLOW_ID}/dispatches'
    # 'ref' est obligatoire : branche sur laquelle lancer le workflow
    data = {'ref': 'main'} 
    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 204:
        print("Workflow cible lancé avec succès !", flush=True)
    else:
        print(f"Erreur lors du lancement : {res.status_code}, {res.text}", flush=True)

if __name__ == "__main__":
    if is_streamer_live():
        print(f"{STREAMER_NAME} est en LIVE.")
        if not is_workflow_already_running():
            trigger_workflow()
        else:
            print("Le workflow cible tourne déjà, inutile de le relancer.", flush=True)
    else:
        print(f"{STREAMER_NAME} est hors ligne.", flush=True)