import os
import requests
import json
from dotenv import load_dotenv, find_dotenv
from utils.database import get_huntlist_ids

load_dotenv(find_dotenv())
api_request = os.getenv('api_request')
api_requests_random = os.getenv('api_requests_random')

async def get_random_pokemon(guildId, id : int):
  res = await get_huntlist_ids(guildId, id)

  request = requests.get(f"{api_requests_random}{res}")
  
  data = json.loads(request.content)
 
  try:
    if data['statusCode'] == 204: 
      return 204
  except:
    return {'id': data['id'], 'name': data['name'].replace('-',' ').capitalize(), 'rarity': data['rarity']}

async def get_pokemon(pokemon):
  pokemon = pokemon.replace(' ', '-').lower()
  request = requests.get(f"{api_request}{pokemon}/")

  if request.status_code == 404: 
    return 404

  data = json.loads(request.content)

  try: 
    data['image']
  except: 
    data['image'] = ''
  
  return {"id": data["id"], "name": data["name"].replace('-',' ').title(), 'rarity': data['rarity'], 'type': data['types'], 'image': data['image']}

async def pokemon_rate_test(num : int):
  request = requests.get(f"https://pokemon-api-bot.herokuapp.com/test/{num}")

  data = json.loads(request.content)

  return data