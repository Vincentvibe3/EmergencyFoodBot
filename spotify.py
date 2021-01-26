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

DATABASE_URL = os.environ['HEROKU_POSTGRESQL_PURPLE_URL']

client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']

async def check_membership(ctx):
    user_id = str(ctx.author.id)
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id='{}';".format(user_id))
    result = cur.fetchone()
    if result == None:
        return False
    else:
        return True
    cur.close()
    conn.close()

class register():
    def __init__(self, ctx, username):
        self.username = username
        self.user_id = str(ctx.author.id)
        self.ctx = ctx
        uri = 'https://spotify--recommendations.herokuapp.com/Recommendations/callback'
        scope = 'user-follow-read user-top-read user-library-read user-read-private'
        parameters = {'client_id': client_id, 'response_type': 'code', 'redirect_uri': uri, 'scope': scope}
        base_url = 'https://accounts.spotify.com/authorize?'
        self.url = base_url+urllib.parse.urlencode(parameters)

    async def register(self):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute("INSERT INTO users(name, id) VALUES(%(username)s, %(id)s);", {'username':self.username, 'id':self.user_id})
        conn.commit()
        cur.close()
        conn.close()
        await self.ctx.send(self.url)

class recommendations():
    def __init__(self, ctx):
        self.user_id = str(ctx.author.id)
        self.ctx = ctx

    async def get_access(self):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id= %(id)s;", {'id':self.user_id})
        result = cur.fetchone()
        self.expiry_time = result[3]
        self.access_token = result[1]
        self.refresh_token = result[2]
        if self.expiry_time < time.time():
            refresh_headers = {'content-type': 'application/x-www-form-urlencoded'}
            refresh_parameters = {'grant_type': 'refresh_token', "refresh_token": self.refresh_token, 'client_id':client_id, 'client_secret':  client_secret}
            async with aiohttp.ClientSession() as session:
                async with session.post('https://accounts.spotify.com/api/token', data=refresh_parameters, headers=refresh_headers) as new_token:
                    json_data = await new_token.text()
                    content = json.loads(json_data)
                    self.access_token = content['access_token']
                    self.expiry_time = time.time()+content['expires_in']
                    cur.execute("UPDATE users SET access_token='{}', expiry={} WHERE id='{}';".format(self.access_token, self.expiry_time, self.user_id))
                    conn.commit()
        cur.close()
        conn.close()
        self.headers={"Authorization":"Bearer "+self.access_token, "Accept": "application/json", "Content-Type": "application/json"}

    async def toptracksinfo(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.spotify.com/v1/me/top/tracks', headers=self.headers) as response:
                json_data = await response.text()
                content = json.loads(json_data)
        artists = []
        songs = []
        for song in content['items']:
            for artist in song['artists']:
                if artist['id'] not in artists:
                    artists.append(artist['id'])
            songs.append(song['id'])
        
        return artists, songs

    async def get_related_artists(self, artists):
        #print(genres)
        all_related_artists = []
        for artist in artists:
            related_artists = []
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.spotify.com/v1/artists/%s/related-artists' %(artist), headers=self.headers) as results:
                    json_data = await results.text()
                    content = json.loads(json_data)
            
            for related_artist in content['artists']:
                related_artists.append(related_artist['id'])
            
            if related_artists:
                chosen_artist = random.choice(related_artists)
                if chosen_artist not in all_related_artists:
                    all_related_artists.append(chosen_artist)
            else:
                continue

        return all_related_artists

    async def get_user_market(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.spotify.com/v1/me', headers=self.headers) as results:
                json_data = await results.text()
                content = json.loads(json_data)
        
        market = content["country"]
        return market

    async def get_top_tracks(self, artists):
        toptracks = []
        info = {}
        usermarket = await recommendations.get_user_market(self)
        for artist in artists:
            parameters={'market':usermarket}
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.spotify.com/v1/artists/%s/top-tracks' %(artist), params=parameters, headers=self.headers) as results:
                    json_data = await results.text()
                    content = json.loads(json_data)

            for track in content['tracks'][:5]:
                allartists = ""
                artists_list = track['artists']
                for song_artist in artists_list:
                    allartists += song_artist['name']+", "
                
                allartists = allartists[:-2]
                toptracks.append(track['id'])
                info[track['id']] = {'name':track['name'], 'url':track['external_urls']['spotify'], 'artist':allartists}
        return toptracks, info

    async def get_tracks_analysis(self, tracks):
        analysis = []
        alltracks = ""
        for track in tracks:
            alltracks = alltracks+track+","
        alltracks=alltracks[:-1]
        parameters={"ids": alltracks}
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.spotify.com/v1/audio-features', params=parameters, headers=self.headers) as results:
                json_data = await results.text()
                content = json.loads(json_data)
        
        analysis = content['audio_features']
        return analysis

    async def get_user_taste(self, songs, feature):
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
                pass
        score = 0
        for quartile in quartiles:
            if quartiles[quartile]:
                average = sum(quartiles[quartile])/len(quartiles[quartile])
                weight = len(quartiles[quartile])/len(allsongs)
                score += average*weight
            else:
                pass
        
        return score

    async def get_feature_weights(self, songs, feature, features):
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

    async def build_user_profile(self, analysis):
        features = {'danceability':{'max':1, 'min':0}, 'energy':{'max':1, 'min':0}, 'loudness':{'max':0, 'min':-60}, 'speechiness':{'max':1, 'min':0}, 'acousticness':{'max':1, 'min':0}, 'instrumentalness':{'max':1, 'min':0}, 'liveness':{'max':1, 'min':0}, 'valence':{'max':1, 'min':0}, 'tempo':None, 'duration_ms':None}
        profile = {}
        weights = {}
        for feature in features:
            profile[feature] = await recommendations.get_user_taste(self, analysis, feature)
            weights[feature] = await recommendations.get_feature_weights(self, analysis, feature, features)
        return profile, weights

    async def get_feature_sim(self, profile, feature1, feature2, song):
        distance1 = profile[feature1]-song[feature1]
        distance2 = profile[feature1]-song[feature1]
        sim = math.sqrt(pow(distance1, 2)+pow(distance2, 2))
        score = 1/(1+sim)
        return score

    async def build_song_score(self, user, song, weights):
        features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms']
        song_score = 0
        for feature1 in features[:-1]:
            current_index = features.index(feature1)
            for feature2 in features[current_index:]:
                score = await recommendations.get_feature_sim(self, user, feature1, feature2, song)
                song_score += score*weights[feature1]*weights[feature2]
        
        return song_score

    async def build_recommendations(self, profile, songs, weights, info):
        embed = discord.Embed(title='Recommendations')
        scores= []
        for song in songs:
            score = await recommendations.build_song_score(self, profile, song, weights)
            scores.append((score, song['id']))
        
        scores.sort()
        scores.reverse()
        for song in scores[:5]:
            song_info = info[song[1]]
            embed.add_field(name=str(scores.index(song)+1), value="["+song_info['name']+" by "+song_info['artist']+"]("+song_info['url']+")", inline=False)
        
        return embed

    async def get_recommendations(self):
        await recommendations.get_access(self)
        message = await self.ctx.send('Getting your top tracks(1/4)')
        top_artists, top_songs = await recommendations.toptracksinfo(self)
        await message.edit(content='Getting related artists(2/4)')
        related_artists = await recommendations.get_related_artists(self, top_artists)
        await message.edit(content='Getting top tracks(3/4)')
        top_related, top_rel_info = await recommendations.get_top_tracks(self, related_artists)
        await message.edit(content='Getting recommendations(4/4)')
        top_analysis = await recommendations.get_tracks_analysis(self, top_songs)
        profile, weights = await recommendations.build_user_profile(self, top_analysis)
        rec_analysis = await recommendations.get_tracks_analysis(self, top_related)
        recs = await recommendations.build_recommendations(self, profile, rec_analysis, weights, top_rel_info)
        await message.delete()
        await self.ctx.send(embed=recs)