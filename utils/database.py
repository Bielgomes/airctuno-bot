import os
import datetime
import pytz
import random
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
from utils.config import all_items, box_id, price_itens, conversor, badges, badges_order, classes, chances_pokeball

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
      collection.insert_one({"_id": id, "class": 0, "pokecoins": 100, "inv": {}, "pokemons": {}, "wishlist": {}, "pokemon_equip": ""})
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
    content += f"**{aux}. {user.name}**\n Pokemons: {len(i['pokemons'])}\n"
    aux += 1
    if aux > 10: return content

  return content

async def get_user_inventory(guildId : int, id : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user = collection.find_one({'_id': id})

  return user['pokecoins'], user['inv']

async def add_user_badge(guildId : int, id : int, badge : str):
  await create_account(guildId, id)

  user_badges = globalusers.find_one({'_id': id})['badges']

  try:
    badges_order[badge]
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

  return {'pokecoins': user['pokecoins'], 'pokemons': pokemons, 'ranking': ranking, 'class': classes[user['class']][0], 'badges': user_badges, 'pokemon_equip': user['pokemon_equip']}

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

  pokemon_equip = collection.find_one({'_id': id})['pokemon_equip']

  if pokemon_equip == pokemon:
    return 400

  collection.find_one_and_update({'_id':id}, {'$set': {'pokemon_equip': pokemon}})

async def user_unequip_pokemon(guildId : int, id : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  pokemon_equip = collection.find_one({'_id': id})['pokemon_equip']
  if pokemon_equip == '':
    return 404

  collection.find_one_and_update({'_id':id}, {'$set': {'pokemon_equip': ""}})

async def add_in_user_wishlist(guildId : int, id : int, pokemon):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user = collection.find_one({'_id': id})

  if len(user['wishlist']) == classes[user['class']][3]:
    return 400

  try:
    user['wishlist'][pokemon['name']]
  except:
    user['wishlist'][pokemon['name']] = pokemon['id']
  else:
    return 401

  collection.find_one_and_update({'_id': id}, {'$set': {'wishlist': user['wishlist']}})

async def remove_in_user_wishlist(guildId : int, id : int, pokemon):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user_wishlist = collection.find_one({'_id': id})['wishlist']

  if len(user_wishlist) == 0:
    return 400

  try:
    user_wishlist[pokemon['name']]
  except:
    return 401
  else:
    del user_wishlist[pokemon['name']]

  collection.find_one_and_update({'_id':id}, {'$set': {'wishlist': user_wishlist}})

async def get_wishlist_ids(guildId : int, id : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user = collection.find_one({'_id': id})

  content = []
  for i in user['wishlist']:
    content.append(user['wishlist'][i])
  return {'content': content}

async def get_user_wishlist(guildId : int, id : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user = collection.find_one({'_id': id})

  wishlist_len = len(user['wishlist'])

  if wishlist_len == 0: return {'code': 400}

  content = ''
  aux = 1
  for i in user['wishlist']:
    content += f"{aux}. {i}\n"
    aux += 1

  return {'code': 200, 'content': content, 'len': wishlist_len, 'max': classes[user['class']][3]}

async def add_in_user_inventory(guildId : int, id : int, itemName : str, quant : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  if itemName in all_items:
    user_inventory = collection.find_one({'_id': id})['inv']

    try:
      user_inventory[itemName] += quant
    except:
      user_inventory[itemName] = quant

    collection.find_one_and_update({'_id': id}, {'$set': {'inv': user_inventory}})
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
    user['inv'][itemName] += quant
  except:
    user['inv'][itemName] = quant

  collection.find_one_and_update({'_id': id}, {'$set': {'inv': user['inv']}, '$inc': {'pokecoins': -price}})

  return

async def user_use_box(guildId : int, id : int, mName : str, quant : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user_inventory = collection.find_one({'_id': id})['inv']

  try:
    box = box_id[mName]
  except: return {'code': 400}

  try:
    user_inventory[mName]
  except:
    return {'code': 404}

  if user_inventory[mName] < quant:
    return {'code': 401}

  user_inventory[mName] -= quant

  if user_inventory[mName] <= 0:
    del user_inventory[mName]

  content = ''
  pokeballs = 0
  greatballs = 0
  ultraballs = 0
  masterballs = 0
  pokecoins = 0

  for i in range(0, quant):
    if box == 1:
      pokeballs += random.randint(1, 2)
      pokecoins += random.randint(10, 20)
    elif box == 2:
      greatballs += random.randint(1, 2)
      pokecoins += random.randint(50, 100)
    elif box == 3:
      ultraballs += random.randint(1, 3)
      pokecoins += random.randint(100, 300)
    else:
      if random.randint(1,2) == 1:
        masterballs += 1
        pokecoins += random.randint(100, 300)
      else:
        ultraballs += random.randint(5, 8)
        pokecoins += random.randint(200, 350)
  
  content += f"{pokecoins}x Pokecoins\n"

  if pokeballs != 0:
    try:
      user_inventory['Pokeball'] += pokeballs
    except:
      user_inventory['Pokeball'] = pokeballs
    content += f"{pokeballs}x Pokeballs\n"

  if greatballs != 0:
    try:
      user_inventory['Greatball'] += greatballs
    except:
      user_inventory['Greatball'] = greatballs
    content += f"{greatballs}x greatballs\n"

  if ultraballs != 0:
    try:
      user_inventory['Ultraball'] += ultraballs
    except:
      user_inventory['Ultraball'] = ultraballs
    content += f"{ultraballs}x Ultraballs\n"

  if masterballs != 0:
    try:
      user_inventory['Masterball'] += masterballs
    except:
      user_inventory['Masterball'] = masterballs
    content += f"{masterballs}x masterballs\n"

  collection.find_one_and_update({'_id': id}, {'$inc': {'pokecoins': pokecoins}, '$set': {'inv': user_inventory}})

  return {'code': 200, 'content': content}

async def catch_successful(guildId, id, pokeball : str, pokemonRarity : str):
  await create_account(guildId, id)
  collection = db[str(guildId)]
  
  user_class = collection.find_one({'_id': id})['class']

  try:
    pokeball = conversor[f"{pokeball}"]
  except:
    return 404

  try:
    chance = (chances_pokeball[pokeball][pokemonRarity] + user_class)
  except: pass

  if pokeball == 'masterball' or random.randint(0, 100) < chance: return 200

async def user_catch_pokemon(guildId : int, id : int, pokemon, quant : int = None):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  if quant == None: quant = 1

  user_pokemons = collection.find_one({'_id': id})['pokemons']

  try:
    user_pokemons[pokemon['name']]['quant'] += quant
  except:
    user_pokemons[pokemon['name']] = {
      'quant': quant,
      'rarity': pokemon['rarity']
    }
    
  collection.find_one_and_update({'_id':id}, {'$set': {'pokemons': user_pokemons}})

  return

async def user_has_pokemon(guildId : int, id, pokemonName):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user_pokemons = collection.find_one({'_id': id})['pokemons']

  try:
    user_pokemons[pokemonName]
  except:
    return 404
  else:
    return 200

async def user_use_pokeball(guildId : int, id : int, pokeball, pokemonRarity : str):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  try:
    pokeball = conversor[pokeball].capitalize()
  except: return {'code': 403, 'pokeball': pokeball}

  user = collection.find_one({'_id': id})

  try:
    user['inv'][pokeball]
  except:
    return {'code': 404, 'pokeball': pokeball}
  else:
    if user['inv'][pokeball] > 0:
      user['inv'][pokeball] -= 1
    if user['inv'][pokeball] <= 0:
      del user['inv'][pokeball]

  try:
    chance = (chances_pokeball[pokeball.lower()][pokemonRarity] + user['class'])
  except: pass

  collection.find_one_and_update({'_id': id}, {'$set': {'inv': user['inv']}})

  if pokeball == 'Masterball' or random.randint(0, 100) < chance:
    return {'code': 200}
    
  return {'code': None}

async def user_in_cooldown(guildId : int, id : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  try:
    user = collection.find_one({'_id': id})
    final_time = user['last_pokemon'] + datetime.timedelta(seconds=classes[user['class']][1])
  except:
    pass
  else:
    if datetime.datetime.now() <= final_time:
      time = final_time.replace(microsecond=0) - datetime.datetime.now().replace(microsecond=0)
      return {'code': 408, 'time': time}

  current_time = datetime.datetime.now()
  collection.find_one_and_update({'_id': id}, {'$set': {'last_pokemon': current_time}})

  return {'code': 200}

async def get_diary_bonus(guildId : int, id : int):
  await create_account(guildId, id)
  collection = db[str(guildId)]

  user_inventory = collection.find_one({'_id': id})['inv']

  try:
    final_time = collection.find_one({'_id': id})['last_daily']
  except: pass
  else:
    current_time = datetime.datetime.now(pytz.timezone('America/Sao_Paulo')).replace(microsecond=0,tzinfo=None) - datetime.timedelta(hour=1)
    if current_time <= final_time:
      time = final_time - current_time
      return {'code': 408, 'time': time}

  pokeballs = random.randint(0, 5)
  ultrabolls = random.randint(0, 3)
  pokecoins = random.randint(400, 500)

  content = f"{pokecoins}$ Pokecoins\n"
  if pokeballs != 0:
    try:
      user_inventory['Pokeball'] += pokeballs
    except:
      user_inventory['Pokeball'] = pokeballs
    content += f"{pokeballs}x Pokeballs\n"
  if ultrabolls != 0:
    content += f"{ultrabolls}x Ultraball"
    try:
      user_inventory['Ultraball'] += ultrabolls
    except:
      user_inventory['Ultraball'] = ultrabolls

  final_time = datetime.datetime.now(pytz.timezone('America/Sao_Paulo')).replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None) + datetime.timedelta(days=1)

  collection.find_one_and_update({'_id': id}, {'$inc': {'pokecoins': pokecoins}, '$set': {'inv': user_inventory, 'last_daily': final_time}})

  return {'code': 200, 'content': content}

async def user_trade_with_two_pokemon(guildId : int, tradeOwner : int, tradeUser : int, pokemon1, pokemon2):
  await create_account(guildId, tradeOwner)
  await create_account(guildId, tradeUser)
  collection = db[str(guildId)]

  tradeOwner_pokemons = collection.find_one({'_id': tradeOwner})['pokemons']
  tradeUser_pokemons = collection.find_one({'_id': tradeUser})['pokemons']

  tradeOwner_pokemons[pokemon1['name']]['quant'] -= 1

  if tradeOwner_pokemons[pokemon1['name']]['quant'] <= 0:
    del tradeOwner_pokemons[pokemon1['name']]

  try:
    tradeOwner_pokemons[pokemon2['name']]['quant'] += 1
  except:
    tradeOwner_pokemons[pokemon2['name']] = {
      'quant': 1,
      'rarity': pokemon2['rarity']
    }

  tradeUser_pokemons[pokemon2['name']]['quant'] -= 1

  if tradeUser_pokemons[pokemon2['name']]['quant'] <= 0:
    del tradeUser_pokemons[pokemon2['name']]

  try:
    tradeUser_pokemons[pokemon1['name']]['quant'] += 1
  except:
    tradeUser_pokemons[pokemon1['name']] = {
      'quant': 1,
      'rarity': pokemon1['rarity']
    }

  tradeOwner_pokemon_equip = collection.find_one({'_id': tradeOwner})['pokemon_equip']

  tradeUser_pokemon_equip = collection.find_one({'_id': tradeUser})['pokemon_equip']

  try:
    tradeOwner_pokemons[tradeOwner_pokemon_equip]
  except: 
    pokemon_equip1 = ""
    collection.find_one_and_update({'_id': tradeOwner}, {'$set': {'pokemon_equip': pokemon_equip1}})

  try:
    tradeUser_pokemons[tradeUser_pokemon_equip]
  except: 
    pokemon_equip2 = ""
    collection.find_one_and_update({'_id': tradeUser}, {'$set': {'pokemon_equip': pokemon_equip2}})

  collection.find_one_and_update({'_id': tradeOwner}, {'$set': {'pokemons': tradeOwner_pokemons}})
  collection.find_one_and_update({'_id': tradeUser}, {'$set': {'pokemons': tradeUser_pokemons}})

async def user_trade_with_one_pokemon(guildId : int, tradeOwner, tradeUser, pokemon):
  await create_account(guildId, tradeOwner)
  await create_account(guildId, tradeUser)
  collection = db[str(guildId)]

  tradeOwner_pokemons = collection.find_one({'_id': tradeOwner})['pokemons']
  tradeUser_pokemons = collection.find_one({'_id': tradeUser})['pokemons']

  tradeOwner_pokemons[pokemon['name']]['quant'] -= 1

  if tradeOwner_pokemons[pokemon['name']]['quant'] <= 0:
    del tradeOwner_pokemons[pokemon['name']]

  try:
    tradeUser_pokemons[pokemon['name']]['quant'] += 1
  except:
    tradeUser_pokemons[pokemon['name']] = {
      'quant': 1,
      'rarity': pokemon['rarity']
    }

  tradeUser_pokemon_equip = collection.find_one({'_id': tradeUser})['pokemon_equip']

  try:
    tradeUser_pokemons[tradeUser_pokemon_equip]
  except: 
    pokemon_equip = ""
    collection.find_one_and_update({'_id': tradeUser}, {'$set': {'pokemon_equip': pokemon_equip}})

  collection.find_one_and_update({'_id': tradeOwner}, {'$set': {'pokemons': tradeOwner_pokemons}})
  collection.find_one_and_update({'_id': tradeUser}, {'$set': {'pokemons': tradeUser_pokemons}})