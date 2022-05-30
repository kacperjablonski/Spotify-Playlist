import requests
import json
from flask import request, Flask, session, redirect

CLIENT_ID = ""          # wprowadź Client_ID aplikacji
CLIENT_SECRET = ""      # wprowadź Client_Secret aplikacji
AUTH_URL = "https://accounts.spotify.com/"
REDIRECT_URI = "http://localhost:5000/authorize"
SPOTI_URL = 'https://api.spotify.com/v1/'
SCOPE = 'user-read-private user-read-email user-read-currently-playing user-modify-playback-state'
AUTH_LINK = AUTH_URL+'authorize?' + 'response_type=code&client_id=' + \
CLIENT_ID + '&redirect_uri=' + REDIRECT_URI + '&scope=' + SCOPE

app = Flask(__name__)

app.secret_key = 'SOMETHING-RANDOM'
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'


@app.route('/')
def login():
    return redirect(AUTH_LINK)


@app.route('/authorize')
def authorize():
    code = request.args.get('code')
    access_token = get_access_token(code)
    session['access_token'] = access_token
    return redirect('/playlist')


@app.route('/playlist')
def playlist():
    if not 'access_token' in session:
        return redirect('/')
    access_token = session['access_token']
    headers = {'Authorization': 'Bearer ' +
                   access_token, 'content_type': 'application/json'}
    recommendation_music = get_Recommendations(headers)
    for next_music in range(50):
        get_music_queue(headers, recommendation_music[next_music]['id'])
    return 'Done!!!!'


def get_Recommendations(headers):
    try:
        current_song = get_current_play_music(headers)
        seed_artists = '?seed_artists=' + current_song['artists'][0]['id']
        seed_tracks = '&seed_tracks=' + current_song['id']
        url = SPOTI_URL + "recommendations" + \
            seed_artists + seed_tracks + '&limit=50'
        response = requests.get(url, headers=headers)
        song = response.json()
        return song['tracks']
    except requests.exceptions.HTTPError as err:
        print(err)


def get_current_play_music(headers):
    try:
        url = SPOTI_URL +"me/player/currently-playing"
        respone = requests.get(url, headers=headers)
        music = respone.json()
        return music['item']
    except requests.exceptions.HTTPError as err:
        print(err)


def get_music_queue(headers, song):
    try:
        music = '?uri=spotify:track:' + song
        url = SPOTI_URL + "me/player/queue" + music
        requests.post(url, headers=headers)
    except requests.exceptions.HTTPError as err:
        print(err)


def get_access_token(authorization_code):
    try:
        data = {'grant_type': 'authorization_code',
                'code': authorization_code, 'redirect_uri': REDIRECT_URI}
        access_token_response = requests.post(
            AUTH_URL+'api/token', data=data, verify=False, auth=(CLIENT_ID, CLIENT_SECRET))
        tokens = json.loads(access_token_response.text)
        access_token = tokens['access_token']
        return access_token
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


if __name__ == '__main__':
    app.run(debug=True)
