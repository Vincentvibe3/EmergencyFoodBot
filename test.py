import requests

r = requests.get('https://nhentai.net/api/gallery/212121')
print(r.json().dumps())