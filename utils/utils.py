import discord
import os
import random
from utils.config import all_emojis, emojis_pokeball, pokemon_rarity, pokemon_rarity_prices
from utils.api import get_pokemon

path = os.getcwd()

async def get_emoji(Src = None):
    if Src == 'pokeballs':
      return emojis_pokeball

    try:
      return all_emojis[Src]
    except:
      return 404

async def get_misteryBox(pokemonRarity, res = None):
  if pokemonRarity == 'common':
    if random.randint(1, 100) <= 20:
      res = {'quant': 1, 'mName': 'Cb', 'mNameEmbed': 'common box'}
  elif pokemonRarity == 'uncommon':
    if random.randint(1, 100) <= 12:
      res = {'quant': 1, 'mName': 'Ub', 'mNameEmbed': 'uncommon box'}
  elif pokemonRarity == 'rare':
    if random.randint(1, 100) <= 10:
      res = {'quant': 1, 'mName': 'Rb', 'mNameEmbed': 'rare box'}
  else:
    if random.randint(1, 2) == 1:
      res = {'quant': 2, 'mName': 'Rb', 'mNameEmbed': 'rare box'}
    else:
      res = {'quant': 1, 'mName': 'Mb', 'mNameEmbed': 'master box'}

  return res

async def get_pokemon_embed(pokemon, user):
  embed_pokemon_details = {
    'ultra-beast': [f"Como um {pokemon['name']} ultra beast apareceu? ele não faz parte da nossa dimensão.", 0x6930FF],
    'legendary': [f"Um {pokemon['name']} lendário apareceu! absolutamente incrível.", 0xFFFF4A],
    'mythical': [f"Um {pokemon['name']} mítico apareceu? eu pensei que eram só mitos.", 0x51486B],
    'rare': [f"Uau, eu nunca vi um {pokemon['name']} por aqui! isso é raro.", 0x5858BD],
    'uncommon': [f"Um {pokemon['name']} apareceu! não é muito comum ver ele por aqui.", 0x8283E6],
    'common': [f"Um {pokemon['name']} selvagem apareceu!", 0xBDBDE6]
  }

  embed_details = embed_pokemon_details[pokemon['rarity']]

  embed = discord.Embed(title=f"{embed_details[0]}", description="Reaja com uma Pokebola para capturar", color=embed_details[1])
  embed.set_author(name=f"{user.name}", icon_url=f"{user.avatar_url}")
  embed.set_image(url=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon['id']}.png")
  embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/897886024179548160/bush.png")

  return embed

async def get_pokemon_run_embed(pokemon):
  embed = discord.Embed(title=f"{pokemon['name']} fugiu!", description="Que pena, mas agora não é hora de desanimar, vá e procure outros pokemons.", color=0xFF1331)
  embed.set_image(url=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon['id']}.png")
  embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/897626126027989062/apper.png")

  return embed

async def get_none_pokemon_embed(user):
  embed = discord.Embed(title=f"Você não encontrou nada!", description="Que pena, mas agora não é hora de desanimar. Vá e procure outros pokemons.", color=0xFF1331)
  embed.set_author(name=f"{user.name}", icon_url=f"{user.avatar_url}")
  embed.set_image(url="https://images-ext-2.discordapp.net/external/gvYTfqkFmNuzjcbbYycwEAUHRka6DyDMMaEj4Pqsaio/https/media.discordapp.net/attachments/887158781832749086/888779438123253770/trade_nothing.png")

  return embed

async def pokemon_exists(pokemonSrc):
  if pokemonSrc.isnumeric():
    pokemon = await get_pokemon(pokemonSrc)
  else:
    pokemon = await get_pokemon(pokemonSrc.lower())

  return pokemon

async def get_pokemon_price(pokemonRarity, quant):
  price = pokemon_rarity_prices[pokemonRarity] * quant
  return price

async def get_trade_embed(user, member, tradeItem1, tradeItem2):
  embed = discord.Embed(title=f"{member.name}​, o treinador {user.name} quer trocar com você!", color=0xFF003F)
  embed.add_field(name=f"{user.name} recebe", value=f"{tradeItem2['name']}", inline=True)
  embed.add_field(name=f"{user.name} recebe", value=f"{tradeItem1['name']}", inline=True)

  embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/898242329620647967/trade.png")
  embed.set_author(name=f"{user.name}", icon_url=f"{user.avatar_url}")
  embed.set_footer(text='Reaja com ✅ para aceitar')

  return {'embed': embed}

async def get_user_pokemons_rarity(pokemons):
  quants = []

  for i in pokemon_rarity:
    res = sum([len(pokemons[x]) for x in pokemons if pokemons[x]['rarity'] == i])
    res /= 2
    quants.append(round(res))

  return {'exclusive': f"{quants[0]}", 'ultra-beast': f"{quants[1]}/11", 'legendary': f"{quants[2]}/57", 'mythical': f"{quants[3]}/22", 'rare': f"{quants[4]}/332", 'uncommon': f"{quants[5]}/126", 'common': f"{quants[6]}/350"}