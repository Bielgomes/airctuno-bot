import os
import datetime
import pytz
import random
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
from utils.config import *

load_dotenv(find_dotenv())
database_connection = os.getenv('database_connection')

ca = certifi.where()

client = MongoClient(database_connection, tlsCAFile=ca)
db = client['servers']
globalusers = client['global']['users']

async def get_prefix(bot, ctx):
  guildId = str(ctx.guild.id)

  if guildId in db.list_collection_names():
    collection = db[guildId]
    prefix = collection.find_one({"_id": 0})['prefix']
    return prefix
  else:
    collection = db.create_collection(guildId)
    collection.insert_one({"_id": 0, "prefix": "$"})
    return '$'

async def change_prefix(guildId : int, nPrefix : str):
  collection = db[str(guildId)]
  prefix = collection.find_one({'_id': 0})['prefix']
  if prefix == nPrefix:
    return 400
  collection.find_one_and_update({'_id': 0}, {'$set': {'prefix': nPrefix}})

async def create_account(guildId : int, id : int):
    collection = db[str(guildId)]
    if not collection.find_one({"_id": id}):
      collection.insert_one({'_id': id, 'class': 0, 'pokecoins': 100, 'bag': {}, 'gotInitial': False, 'pokemons': {}, 'huntArea': '', 'huntlist': {}, 'pokemonEquip': '', 'dailyTime': '', 'pokemonTime': ''})
    if not globalusers.find_one({'_id': id}):
      globalusers.insert_one({'_id': id, "badges": ['Betatester']})

async def get_user_pokemons(guildId : int, id : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]
  
  user_pokemons = collection.find_one({'_id': id})['pokemons']
  return user_pokemons

async def get_user_ranking(guildId : int, id : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  users = collection.find().skip(1)
  users = reversed(sorted(users, key = lambda x: len(x['pokemons'].keys())))
  ranking = (next(i for i, x in enumerate(users) if x['_id'] == id)) + 1

  return ranking

async def get_guild_ranking(bot, guildId : int):
  collection = db[str(guildId)]

  users = collection.find().skip(1)
  users = reversed(sorted(users, key = lambda x: len(x['pokemons'].keys())))

  content = ''
  aux = 1
  for i in users:
    user = bot.get_user(i['_id'])
    content += f"**{aux}. {user.name}**\n Pokedex: {len(i['pokemons'])} / 898\n"
    aux += 1
    if aux > 10: return content

  return content

async def get_user_bag(guildId : int, id : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user = collection.find_one({'_id': id})

  return user['pokecoins'], user['bag']

async def add_user_badge(guildId : int, id : int, badge : str):
  await create_account(guildId, id)

  user_badges = globalusers.find_one({'_id': id})['badges']

  try:
    badges[badge.lower()]
  except:
    return 404

  if badge in user_badges:
    return 400
  else:
    user_badges.append(badge)

  globalusers.find_one_and_update({'_id':id}, {'$set': {'badges': user_badges}})

async def get_user_profile(guildId : int, id):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user = collection.find_one({'_id': id})
  userBadges = globalusers.find_one({'_id': id})

  pokemons = sum([(user['pokemons'][x]['quant']) for x in user['pokemons']])

  ranking = await get_user_ranking(guildId, id)

  if len(userBadges['badges']) == 0:
    user_badges = "Nenhum"
  else:
    user_badges = ''
    sort_badges = sorted(userBadges['badges'], key=lambda x: badges_order.index(x))
    for i in sort_badges:
      user_badges += f"{badges[i.lower()]}"

  return {'pokecoins': user['pokecoins'], 'pokemons': pokemons, 'ranking': ranking, 'class': classes[user['class']][0], 'badges': user_badges, 'pokemonEquip': user['pokemonEquip']}

async def get_class_utils(guildId : int, id : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user = collection.find_one({'_id': id})

  if user['class'] == 12: return {'code': 401}

  return {'code': 200, 'class_price': classes[user['class']][2]}

async def user_class_upgrade(guildId : int, id : int):
  collection = db[str(guildId)]

  user = collection.find_one({'_id': id})

  if user['class'] == 12: return {'code': 401}

  class_price = classes[user['class']][2]

  if class_price > user['pokecoins']: return {'code': 400, 'pokecoins': class_price}

  collection.find_one_and_update({'_id':id}, {'$inc': {'class': 1, 'pokecoins': -class_price}})
  return {'code': 200, 'class': classes[user['class']+1][0]}

async def get_pokemon_price(guildId : id, id : id, pokemon, quant):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  if await user_has_pokemon(guildId, id, pokemon['name']) == 404:
    return 404

  user_pokemons = collection.find_one({'_id': id})['pokemons']

  if quant > user_pokemons[pokemon['name']]['quant']:
    return 401

  price = pokemon_rarity_prices[pokemon['rarity']] * quant

  return price

async def release_pokemon(guildId, id, pokemon, quant, price):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  if await user_has_pokemon(guildId, id, pokemon['name']) == 404:
    return 404

  user_pokemons = collection.find_one({'_id': id})['pokemons']

  if quant > user_pokemons[pokemon['name']]['quant']:
    return 401

  user_pokemons[pokemon['name']]['quant'] -= quant

  if user_pokemons[pokemon['name']]['quant'] <= 0:
    del user_pokemons[pokemon['name']]

  collection.update_one({'_id': id}, {'$set': {'pokemons': user_pokemons}, '$inc': {'pokecoins': price}})
  return 200

async def user_equip_pokemon(guildId : int, id : int, pokemon : str):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  pokemonEquip = collection.find_one({'_id': id})['pokemonEquip']

  if pokemonEquip == pokemon:
    return 400

  collection.find_one_and_update({'_id':id}, {'$set': {'pokemonEquip': pokemon}})

async def user_unequip_pokemon(guildId : int, id : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  pokemonEquip = collection.find_one({'_id': id})['pokemonEquip']
  if pokemonEquip == '':
    return 404

  collection.find_one_and_update({'_id':id}, {'$set': {'pokemonEquip': ""}})

async def add_to_huntlist(guildId : int, id : int, pokemon):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user = collection.find_one({'_id': id})

  if len(user['huntlist']) == classes[user['class']][3]:
    return 400

  try:
    user['huntlist'][pokemon['name']]
  except:
    user['huntlist'][pokemon['name']] = pokemon['id']
  else:
    return 401

  collection.find_one_and_update({'_id': id}, {'$set': {'huntlist': user['huntlist']}})

async def remove_from_huntlist(guildId : int, id : int, pokemon):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user_huntlist = collection.find_one({'_id': id})['huntlist']

  if len(user_huntlist) == 0:
    return 400

  try:
    user_huntlist[pokemon['name']]
  except:
    return 401
  else:
    del user_huntlist[pokemon['name']]

  collection.find_one_and_update({'_id':id}, {'$set': {'huntlist': user_huntlist}})

async def get_huntlist_ids(guildId : int, id : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user = collection.find_one({'_id': id})

  content = []
  for i in user['huntlist']:
    content.append(user['huntlist'][i])
  return {'content': content}

async def get_user_huntlist(guildId : int, id : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user = collection.find_one({'_id': id})

  huntlist_len = len(user['huntlist'])

  if huntlist_len == 0: return {'code': 400}

  content = ''
  aux = 1
  for i in user['huntlist']:
    content += f"{aux}. {i}\n"
    aux += 1

  return {'code': 200, 'content': content, 'len': huntlist_len, 'max': classes[user['class']][3]}

async def add_in_user_bag(guildId : int, id : int, itemName : str, quant : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  if itemName in all_items:
    user_bag = collection.find_one({'_id': id})['bag']

    try:
      user_bag[itemName] += quant
    except:
      user_bag[itemName] = quant

    collection.find_one_and_update({'_id': id}, {'$set': {'bag': user_bag}})
  else:
    return 404

async def user_inc_money(guildId : int, id : int, quant : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  collection.find_one_and_update({'_id': id}, {'$inc': {'pokecoins': quant}})

async def user_buy_item(guildId : int, id : int, itemName, quant):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  try:
    itemName = itemName.lower().capitalize()
  except: return 404

  try:
    price_itens[itemName]
  except:
    return 404

  user = collection.find_one({'_id': id})

  price = (price_itens[itemName] * quant)

  if price > user['pokecoins']:
    return 507

  try:
    user['bag'][itemName] += quant
  except:
    user['bag'][itemName] = quant

  collection.find_one_and_update({'_id': id}, {'$set': {'bag': user['bag']}, '$inc': {'pokecoins': -price}})

  return

async def user_use_box(guildId : int, id : int, mName : str, quant : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user_bag = collection.find_one({'_id': id})['bag']

  try:
    box = box_ids[mName]
  except: return {'code': 400}

  try:
    user_bag[mName]
  except:
    return {'code': 404}

  if user_bag[mName] < quant:
    return {'code': 401}

  user_bag[mName] -= quant

  if user_bag[mName] <= 0:
    del user_bag[mName]

  content = ''
  pokecoins = 0
  aux = {'Pokeball': 0, 'Greatball': 0, 'Ultraball': 0, 'Masterball': 0}

  for i in range(0, quant):
    if box == 1:
      aux['Pokeball'] += random.randint(1, 2)
      pokecoins += random.randint(25, 50)
    elif box == 2:
      aux['Greatball'] += random.randint(1, 2)
      pokecoins += random.randint(50, 100)
    elif box == 3:
      aux['Ultraball'] += random.randint(1, 3)
      pokecoins += random.randint(100, 300)
    else:
      if random.randint(1,2) == 1:
        aux['Masterball'] += 1
        pokecoins += random.randint(100, 300)
      else:
        aux['Ultraball'] += random.randint(5, 8)
        pokecoins += random.randint(200, 350)

  content += f"{pokecoins}$ Pokecoins\n"
  for i in aux:
    if aux[i] != 0:
      try:
        user_bag[i] += aux[i]
      except:
        user_bag[i] = aux[i]
      content += f"{aux[i]}x {i.capitalize()}\n"

  collection.find_one_and_update({'_id': id}, {'$inc': {'pokecoins': pokecoins}, '$set': {'bag': user_bag}})

  return {'code': 200, 'content': content}

async def catch_successful(guildId, id, pokeball : str, pokemonRarity : str):
  await create_account(guildId, id)
  collection = db[str(guildId)]
  
  user_class = collection.find_one({'_id': id})['class']

  try:
    pokeball = emojis_conversor[f"{pokeball}"]
  except:
    return 404

  try:
    chance = chances_pokeball[pokeball][pokemonRarity] + user_class
    print(f"{pokeball} na classe {user_class} com a chance em {chance}")
  except: pass

  if pokeball == 'masterball' or random.randint(0, 100) < chance: return 200

async def user_catch_pokemon(guildId : int, id : int, pokemon, box = None, quant : int = None):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  if quant == None: quant = 1

  user = collection.find_one({'_id': id})

  try:
    user['pokemons'][pokemon['name']]['quant'] += quant
  except:
    user['pokemons'][pokemon['name']] = {
      'quant': quant,
      'rarity': pokemon['rarity']
    }

  if box != None:
    try:
      user['bag'][box['mName']] += box['quant']
    except:
      user['bag'][box['mName']] = box['quant']

  collection.find_one_and_update({'_id':id}, {'$set': {'pokemons': user['pokemons'], 'bag': user['bag']}})

  return

async def user_has_pokemon(guildId : int, id, pokemonName):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user_pokemons = collection.find_one({'_id': id})['pokemons']

  try:
    user_pokemons[pokemonName]
  except:
    return 404

async def user_use_pokeball(guildId : int, id : int, pokeball, pokemonRarity : str):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  pokeball = emojis_conversor[pokeball].capitalize()

  user = collection.find_one({'_id': id})

  try:
    user['bag'][pokeball]
  except:
    return {'code': 404, 'pokeball': pokeball}
  else:
    if user['bag'][pokeball] > 0:
      user['bag'][pokeball] -= 1
    if user['bag'][pokeball] <= 0:
      del user['bag'][pokeball]

  try:
    chance = (chances_pokeball[pokeball.lower()][pokemonRarity] + user['class'])
  except: pass

  collection.find_one_and_update({'_id': id}, {'$set': {'bag': user['bag']}})

  if pokeball == 'Masterball' or random.randint(0, 100) < chance:
    return {'code': 200}
    
  return {'code': None}

async def user_starter_pokemon(guildId : int, id : int, pokemonName : str):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user = collection.find_one({'_id': id})

  user['pokemons'][f"{pokemonName}"] = {
    'quant': 1,
    'rarity': 'common'
  }

  collection.find_one_and_update({'_id':id}, {'$set': {'pokemons': user['pokemons'], 'gotInitial': True}})

async def user_can_use(guildId : int, id : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user = collection.find_one({'_id': id})

  if user['gotInitial'] == False:
    return {'code': 401}

  if user['pokemonTime'] != '':
    final_time = user['pokemonTime'] + datetime.timedelta(seconds=classes[user['class']][1])
    
    if datetime.datetime.now() <= final_time:
      time = final_time.replace(microsecond=0) - datetime.datetime.now().replace(microsecond=0)
      return {'code': 402, 'time': time}

  current_time = datetime.datetime.now()
  collection.find_one_and_update({'_id': id}, {'$set': {'pokemonTime': current_time}})

  return {'code': 200}

async def users_can_trade(guildId, id1, id2):
  await create_account(guildId, id1)
  await create_account(guildId, id2)
  collection = db[str(guildId)]

  user1 = collection.find_one({'_id': id1})['pokemons']
  if len(user1) == 0:
    return 1
  if id2 != None:
    user2 = collection.find_one({'_id': id2})['pokemons']
    if len(user2) == 0:
      return 2

async def get_daily_bonus(guildId : int, id : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user = collection.find_one({'_id': id})

  if user['dailyTime'] != '':
    current_time = datetime.datetime.now(pytz.timezone('America/Santarem')).replace(microsecond=0,tzinfo=None)
    if current_time <= user['dailyTime']:
      time = user['dailyTime'] - current_time
      return {'code': 408, 'time': time}

  aux = {'Pokeball': 0, 'Ultraball': 0}
  pokecoins = random.randint(700, 800)

  aux['Pokeball'] = random.randint(1, 5)
  aux['Ultraball'] = random.randint(0, 3)

  content = f"{pokecoins}$ Pokecoins\n"
  for i in aux:
    if aux[i] != 0:
      try:
        user['bag'][i] += aux[i]
      except:
        user['bag'][i] = aux[i]
      content += f"{aux[i]}x {i}\n"

  final_time = datetime.datetime.now(pytz.timezone('America/Sao_Paulo')).replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None) + datetime.timedelta(days=1)

  collection.find_one_and_update({'_id': id}, {'$inc': {'pokecoins': pokecoins}, '$set': {'bag': user['bag'], 'dailyTime': final_time}})

  return {'code': 200, 'content': content}

async def user_trade_with_two_pokemon(guildId : int, tradeOwner : int, tradeUser : int, pokemon1, pokemon2):
  await create_account(guildId, tradeOwner)
  await create_account(guildId, tradeUser)
  collection = db[str(guildId)]

  tradeOwner_pokemons = collection.find_one({'_id': tradeOwner})['pokemons']
  tradeUser_pokemons = collection.find_one({'_id': tradeUser})['pokemons']

  try:
    tradeOwner_pokemons[pokemon1['name']]['quant'] -= 1
  except:
    return 404

  if tradeOwner_pokemons[pokemon1['name']]['quant'] <= 0:
    del tradeOwner_pokemons[pokemon1['name']]

  try:
    tradeOwner_pokemons[pokemon2['name']]['quant'] += 1
  except:
    tradeOwner_pokemons[pokemon2['name']] = {
      'quant': 1,
      'rarity': pokemon2['rarity']
    }

  try:
    tradeUser_pokemons[pokemon2['name']]['quant'] -= 1
  except:
    return 403

  if tradeUser_pokemons[pokemon2['name']]['quant'] <= 0:
    del tradeUser_pokemons[pokemon2['name']]

  try:
    tradeUser_pokemons[pokemon1['name']]['quant'] += 1
  except:
    tradeUser_pokemons[pokemon1['name']] = {
      'quant': 1,
      'rarity': pokemon1['rarity']
    }

  tradeOwner_pokemonEquip = collection.find_one({'_id': tradeOwner})['pokemonEquip']

  tradeUser_pokemonEquip = collection.find_one({'_id': tradeUser})['pokemonEquip']

  try:
    tradeOwner_pokemons[tradeOwner_pokemonEquip]
  except: 
    collection.find_one_and_update({'_id': tradeOwner}, {'$set': {'pokemonEquip': ""}})

  try:
    tradeUser_pokemons[tradeUser_pokemonEquip]
  except: 
    collection.find_one_and_update({'_id': tradeUser}, {'$set': {'pokemonEquip': ""}})

  collection.find_one_and_update({'_id': tradeOwner}, {'$set': {'pokemons': tradeOwner_pokemons}})
  collection.find_one_and_update({'_id': tradeUser}, {'$set': {'pokemons': tradeUser_pokemons}})

async def user_trade_with_one_pokemon(guildId : int, tradeOwner, tradeUser, pokemon):
  await create_account(guildId, tradeOwner)
  await create_account(guildId, tradeUser)
  collection = db[str(guildId)]

  tradeOwner_pokemons = collection.find_one({'_id': tradeOwner})['pokemons']
  tradeUser_pokemons = collection.find_one({'_id': tradeUser})['pokemons']

  try:
    tradeOwner_pokemons[pokemon['name']]['quant'] -= 1
  except:
    return 404

  if tradeOwner_pokemons[pokemon['name']]['quant'] <= 0:
    del tradeOwner_pokemons[pokemon['name']]

  try:
    tradeUser_pokemons[pokemon['name']]['quant'] += 1
  except:
    tradeUser_pokemons[pokemon['name']] = {
      'quant': 1,
      'rarity': pokemon['rarity']
    }

  tradeUser_pokemonEquip = collection.find_one({'_id': tradeUser})['pokemonEquip']

  try:
    tradeUser_pokemons[tradeUser_pokemonEquip]
  except:
    collection.find_one_and_update({'_id': tradeUser}, {'$set': {'pokemonEquip': ""}})

  collection.find_one_and_update({'_id': tradeOwner}, {'$set': {'pokemons': tradeOwner_pokemons}})
  collection.find_one_and_update({'_id': tradeUser}, {'$set': {'pokemons': tradeUser_pokemons}})