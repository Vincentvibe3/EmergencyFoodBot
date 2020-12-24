import json
import time
import os
import psycopg2
import random
import math
import urllib.parse
import aiohttp
import asyncio
import discord
from discord.ext import commands

DATABASE_URL = os.environ['DATABASE_URL']

client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']

async def register(ctx, username):
    user_id = str(ctx.author.id)
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("INSERT INTO users(name, id) VALUES(%s, %s);", (username, user_id))
    login_url = await get_login_url()
    await ctx.send(login_url)

async def get_login_url():
    uri = 'https://spotify--recommendations.herokuapp.com/Recommendations/callback'
    scope = 'user-follow-read user-top-read user-library-read user-read-private'
    parameters = {'client_id': client_id, 'response_type': 'code', 'redirect_uri': uri, 'scope': scope}
    base_url = 'https://accounts.spotify.com/authorize?'
    url = base_url+urllib.parse.urlencode(parameters)
    return url

def toptracksinfo():
    response = requests.get('https://api.spotify.com/v1/me/top/tracks', headers=headers)
    datafile = open("data.json" ,"w")
    content = json.loads(response.text)
    datafile.write(json.dumps(content, indent=4))
    artists = []
    songs = []
    for song in content['items']:
        for artist in song['artists']:
            if artist['id'] not in artists:
                artists.append(artist['id'])
        songs.append(song['id'])
    
    return artists, songs

def get_search_params(query):
    parameters={'q':"genre:"+query, "type":"track,artist"}
    try:
        search = requests.get('https://api.spotify.com/v1/search', headers=headers, params=parameters)
        if search.status_code == 429:
            raise 'too fast'
    except Exception:
        print('toofast')
    results = json.loads(search.text)
    if results['artists']['total'] == 0:
        total = results['tracks']['total']
        return total, 'track'
    else:
        total = results['artists']['total']
    if total > 1:
        if total > 200:
            total = 200
        else:
            total = total-2
    elif total == 1:
        total = 0
    else:
        print('no results')
    return total, 'artist'

def get_related_artists(artists):
    #print(genres)
    all_related_artists = []
    for artist in artists:
        related_artists = []
        results = requests.get('https://api.spotify.com/v1/artists/%s/related-artists' %(artist), headers=headers)
        content = json.loads(results.text)
        for related_artist in content['artists']:
            related_artists.append(related_artist['id'])
        chosen_artist = random.choice(related_artists)
        if chosen_artist not in all_related_artists:
            all_related_artists.append(chosen_artist)
    return all_related_artists

def get_user_market():
    results = requests.get('https://api.spotify.com/v1/me', headers=headers)
    content = json.loads(results.text)
    market = content["country"]
    return market

def get_top_tracks(artists):
    toptracks = []
    info = {}
    usermarket = get_user_market()
    for artist in artists:
        parameters={'market':usermarket}
        results = requests.get('https://api.spotify.com/v1/artists/%s/top-tracks' %(artist), params=parameters, headers=headers)
        content = json.loads(results.text)
        for track in content['tracks'][:5]:
            allartists = ""
            artists_list = track['artists']
            for song_artist in artists_list:
                allartists += song_artist['name']+", "
            
            allartists = allartists[:-2]
            toptracks.append(track['id'])
            info[track['id']] = {'name':track['name'], 'url':track['external_urls']['spotify'], 'artist':allartists}
    return toptracks, info

def get_tracks_analysis(tracks):
    analysis = []
    alltracks = ""
    for track in tracks:
        alltracks = alltracks+track+","
    alltracks=alltracks[:-1]
    parameters={"ids": alltracks}
    results = requests.get('https://api.spotify.com/v1/audio-features', params=parameters, headers=headers)
    content = json.loads(results.text)
    analysis = content['audio_features']
    return analysis

def get_user_taste(songs, feature):
    allsongs=[]
    for song in songs:
        allsongs.append(song[feature])
    allsongs.sort()
    quartiles={'1':[], '2':[], '3':[], '4':[]}
    min = allsongs[0]
    max = allsongs[-1]
    difference = max-min
    interval = difference/4
    separator1 = min+interval
    separator2 = min+interval*2
    separator3 = min+interval*3
    for value in allsongs:
        if value >= min and value < separator1:
            quartiles['1'].append(value)
        elif value >= separator1 and value < separator2:
            quartiles['2'].append(value)
        elif value >= separator2 and value < separator3:
            quartiles['3'].append(value)
        elif value >= separator3 and value <= max:
            quartiles['4'].append(value)
        else:
            print('something went wrong')
    score = 0
    for quartile in quartiles:
        if quartiles[quartile]:
            average = sum(quartiles[quartile])/len(quartiles[quartile])
            weight = len(quartiles[quartile])/len(allsongs)
            score += average*weight
        else:
            pass
    
    return score

def get_feature_weights(songs, feature, features):
    allsongs=[]
    for song in songs:
        allsongs.append(song[feature])
    allsongs.sort()
    difference = allsongs[-1]-allsongs[0]
    if features[feature] != None:
        max_difference = features[feature]['max']-features[feature]['min']
        weight = 1/(1+(difference/max_difference))
    else:
        weight = 1/(1+difference)
    return weight

def build_user_profile(analysis):
    features = {'danceability':{'max':1, 'min':0}, 'energy':{'max':1, 'min':0}, 'loudness':{'max':0, 'min':-60}, 'speechiness':{'max':1, 'min':0}, 'acousticness':{'max':1, 'min':0}, 'instrumentalness':{'max':1, 'min':0}, 'liveness':{'max':1, 'min':0}, 'valence':{'max':1, 'min':0}, 'tempo':None, 'duration_ms':None}
    profile = {}
    weights = {}
    for feature in features:
        profile[feature] = get_user_taste(analysis, feature)
        weights[feature] = get_feature_weights(analysis, feature, features)
    return profile, weights

def get_feature_sim(profile, feature1, feature2, song):
    distance1 = profile[feature1]-song[feature1]
    distance2 = profile[feature1]-song[feature1]
    sim = math.sqrt(pow(distance1, 2)+pow(distance2, 2))
    score = 1/(1+sim)
    return score

def build_song_score(user, song, weights):
    features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms']
    song_score = 0
    for feature1 in features[:-1]:
        current_index = features.index(feature1)
        for feature2 in features[current_index:]:
            score = get_feature_sim(user, feature1, feature2, song)
            song_score += score*weights[feature1]*weights[feature2]
    
    return song_score

def get_recommendations(profile, songs, weights, info):
    recommendations = ""
    scores= []
    for song in songs:
        score = build_song_score(profile, song, weights)
        scores.append((score, song['id']))
    
    scores.sort()
    scores.reverse()
    for song in scores[:5]:
        song_info = info[song[1]]
        recommendations+=(str(scores.index(song)+1)+". "+song_info['name']+" by "+song_info['artist']+" url: "+song_info['url']+"\n")
    
    return recommendations

def request_recommendations(ctx):
    while True:
        auth_key = open("auth_key.json", "r")
        auth = json.loads(auth_key.read())
        expiry_time = auth['expiry_time']
        access_token = auth['access_token']
        refresh_token = auth['refresh_token']
        user = auth['name']
        headers={"Authorization":"Bearer "+access_token, "Accept": "application/json", "Content-Type": "application/json"}
        if time.time() < expiry_time:
            top_artists, top_songs = toptracksinfo()
            print('user top songs and artists completed', end = " (1/5)\r")
            related_artists = get_related_artists(top_artists)
            print(" "*100, end="\r")
            print('related artists completed', end = " (2/5)\r")
            top_related, top_rel_info = get_top_tracks(related_artists)
            print(" "*100, end="\r")
            print('related songs completed', end = " (3/5)\r")
            top_analysis = get_tracks_analysis(top_songs)
            profile, weights = build_user_profile(top_analysis)
            print(" "*100, end="\r")
            print('user profile completed', end = " (4/5)\r")
            rec_analysis = get_tracks_analysis(top_related)
            recs = get_recommendations(profile, rec_analysis, weights, top_rel_info)
            print('recommendations completed (5/5)')
            print(recs)
            break
        
        else:
            refresh_headers = {'content-type': 'application/x-www-form-urlencoded'}
            parameters = {'grant_type': 'refresh_token', "refresh_token": refresh_token, 'client_id':client_id, 'client_secret':  client_secret}
            new_token = requests.post('https://accounts.spotify.com/api/token', data=parameters, headers=refresh_headers)
            content = json.loads(new_token.text)
            content['expiry_time'] = time.time()+content['expires_in']
            content['name'] = user
            content['refresh_token'] = refresh_token
            keyfile = open("auth_key.json" ,"w")
            keyfile.write(json.dumps(content, indent=4))
            print(new_token)