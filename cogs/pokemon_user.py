import asyncio
import discord
from discord.ext import *
from discord.ext import commands
import math
from collections import OrderedDict
from utils.database import *
from utils.api import *
from utils.utils import *
from utils.config import *

class Pokemon_user(commands.Cog):

  def __init__(self, bot):
      self.bot = bot
      self.user_list = []
      self.release_list = []

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command(aliases=['p', 'pm'])
  async def pokemon(self, ctx):
    res = await user_can_use(ctx.guild.id, ctx.author.id)

    if res['code'] == 401:
      async def start(isIn = None):
        if isIn == True:
          if ctx.author.id in self.user_list: return
        if ctx.author.id not in self.user_list:
          self.user_list.append(ctx.author.id)

        if isIn == True:
          embed = discord.Embed(title=f"Olá {ctx.author.name}, não vi você chegar!", description=f'''
**```
Eu sou o Professor Ednaldo, aparentemente você é novo por aqui não é mesmo?

Para começar sua jornada no AirticunoBot eu irei te ajudar a escolher seu primeiro Pokémon!
```**
Cada número abaixo representa os iniciais de cada geração.
Basta reagir com eles para ver as opções de pokémon! e então é só escolher um com o ✅.
          ''', color=0x524D68)
        else:
          embed = discord.Embed(title=f"{ctx.author.name}, não gostou de nenhum deles?", description=f'''
          ```Você pode escolher pokémons de outras gerações.```
          ''', color=0x524D68)
        embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/901583410294841354/Professor_Ednaldo.png")

        msg = await ctx.channel.send(embed=embed)
        
        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")
        await msg.add_reaction("3️⃣")
        await msg.add_reaction("4️⃣")
        await msg.add_reaction("5️⃣")
        await msg.add_reaction("6️⃣")
        await msg.add_reaction("7️⃣")
        await msg.add_reaction("8️⃣")

        def check(reaction, user):
          return user != self.bot.user and user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣']
        
        while True:
          try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
          except asyncio.TimeoutError:
            return self.user_list.remove(ctx.author.id)
          else:
            if str(reaction.emoji) == '1️⃣': gen = 1
            elif str(reaction.emoji) == '2️⃣': gen = 2
            elif str(reaction.emoji) == '3️⃣': gen = 3
            elif str(reaction.emoji) == '4️⃣': gen = 4
            elif str(reaction.emoji) == '5️⃣': gen = 5
            elif str(reaction.emoji) == '6️⃣': gen = 6
            elif str(reaction.emoji) == '7️⃣': gen = 7
            elif str(reaction.emoji) == '8️⃣': gen = 8
            else: continue

            await msg.delete()
            return gen

      async def final(gen):
        page = 1
        pages = 3

        embed = discord.Embed(title=f"O que você acha dele?", description=f'''
        **```O {starter_pokemons[gen][page][0]} é um belo pokémon de tipo {starter_pokemons[gen][page][2]}! você vai querer ele?```**
        ''', color=0x524D68)
        embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/901583410294841354/Professor_Ednaldo.png")
        embed.set_image(url=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{starter_pokemons[gen][1][1]}.png")
        embed.set_footer(text=f"Page {page} / 3")

        msg = await ctx.channel.send(embed=embed)
        
        await msg.add_reaction("⬅")
        await msg.add_reaction("➡")
        await msg.add_reaction("✅")
        await msg.add_reaction("🔄")

        def check(reaction, user):
          return user != self.bot.user and user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in ['⬅', '➡', '✅', '🔄']

        while True:
          try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
          except asyncio.TimeoutError:
            return self.user_list.remove(ctx.author.id)
          else:
            if str(reaction.emoji) == '✅':
              await user_starter_pokemon(ctx.guild.id, ctx.author.id, starter_pokemons[gen][page][0])
              self.user_list.remove(ctx.author.id)
 
              embed = discord.Embed(title=f"Essa foi uma ótima escolha!", description=f'''
**```Agora treinador, você está pronto para iniciar sua jornada junto de seu {starter_pokemons[gen][page][0]}!

Colete todos os Pokémons que puder e se torne o melhor treinador da sua Região.

Te desejo boa sorte!```**
              Caso não esteja familiarizado com os comandos eu irei te ajudar no $help
              ''', color=0x524D68)
              embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
              embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/901583410294841354/Professor_Ednaldo.png")
              embed.set_image(url=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{starter_pokemons[gen][page][1]}.png")
              return await msg.edit(embed=embed)
            elif str(reaction.emoji) == '🔄':
              await msg.delete()
              return True
            elif str(reaction.emoji) == '⬅':
              page -= 1
              if page < 1: page = pages
            elif str(reaction.emoji) == '➡':
              page += 1
              if page > pages: page = 1
            else: continue

            await reaction.remove(user)

            embed = discord.Embed(title=f"O que você acha dele?", description=f'''
            **```O {starter_pokemons[gen][page][0]} é um belo pokémon de tipo {starter_pokemons[gen][page][2]}! você vai querer ele?```**
            ''', color=0x524D68)
            embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/901583410294841354/Professor_Ednaldo.png")
            embed.set_image(url=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{starter_pokemons[gen][page][1]}.png")
            embed.set_footer(text=f"Page {page} / 3")

            await msg.edit(embed=embed)
      
      i = 0
      while True:
        if i == 0: gen = await start(True)
        else: gen = await start()
        i = await final(gen)
        if i != True:return

    if res['code'] == 402:
      return await ctx.channel.send(f"{ctx.author.name}, aguarde `{res['time']}` para buscar pokemons novamente.")

    pokemon = await get_random_pokemon(ctx.guild.id, ctx.author.id)

    embed = await get_pokemon_embed(pokemon, ctx.author)

    msg = await ctx.channel.send(embed=embed)

    for i in emojis_pokeball:
      await msg.add_reaction(emojis_pokeball[i])

    def check(reaction, user):
      return user != self.bot.user and reaction.message.id == msg.id and str(reaction.emoji) in emojis_pokeball.values()

    while True:
      try:
        reaction, user = await self.bot.wait_for("reaction_add", timeout=19.0, check=check)
      except asyncio.TimeoutError:
        embed = await get_pokemon_run_embed(pokemon)
        await msg.edit(embed=embed)
        return await msg.clear_reactions()
      else:
        use_pokeball = await user_use_pokeball(ctx.guild.id, user.id, str(reaction), pokemon['rarity'])

        if use_pokeball['code'] == 404:
          await ctx.channel.send(f"{user.name} não tem {use_pokeball['pokeball']}s")
          continue

        if use_pokeball['code'] == 200:
          res = await get_misteryBox(pokemon['rarity'])
          await user_catch_pokemon(ctx.guild.id, user.id, pokemon, res)

          embed = discord.Embed(title=f"{pokemon['name']} Capturado!", description="Que belo pokemon para sua coleção. Agora vá e procure outros pokemons.", color=0x00FF85)
          embed.set_author(name=f"{user.name}", icon_url=f"{user.avatar_url}")
          embed.set_image(url=f"{pokemon['image']}")
          embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/899811541971513384/pokeball.png")

          if res != None:
            embed.set_footer(text=f"Você ganhou {res['quant']}x de {res['mNameEmbed']}")
          
          await msg.edit(embed=embed)
          return await msg.clear_reactions()
        else:
          embed = await get_pokemon_run_embed(pokemon)
          await msg.edit(embed=embed)
          return await msg.clear_reactions()
  @pokemon.error
  async def pokemon_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command(aliases=['pc'])
  async def personalcomputer(self, ctx, rare : str = None):
    user_pokemons = await get_user_pokemons(ctx.guild.id, ctx.author.id)

    quants = []

    if rare == 'rares':
      user_pokemons = OrderedDict(reversed(sorted(user_pokemons.items(), key = lambda x: (pokemon_rarity_ordem.get(x[1]['rarity']), x[1]['quant']))))
      quants = await get_user_pokemons_rarity(user_pokemons)
      embed_color = 0xfc0366
      actually_rarity = None
    else:
      user_pokemons = OrderedDict(reversed(user_pokemons.items()))
      embed_color = 0xfc0367

    if len(user_pokemons) == 0:
      return await ctx.channel.send(f"{ctx.author.name}, você não tem pokémons.")

    pages = math.ceil(len(user_pokemons) / 10)

    content = ''

    aux = 1
    for i in user_pokemons:
      if aux <= 10:
        rarity = user_pokemons[i]['rarity']
        if rare == 'rares':
          if actually_rarity != rarity:
            actually_rarity = rarity
            content += f" \n{emojis_rarity[rarity]}**{rarity.capitalize()}({quants[rarity]}):**\n"
        content += f"**{i} {user_pokemons[i]['quant']}x**\n"
      aux += 1

    embed = discord.Embed(description=f"​ \n{content}", color=embed_color)
    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/890060279692550164/pokedex.png")
    embed.set_footer(text=f"{len(user_pokemons)} / 898 - Page 1 / {pages}")

    msg = await ctx.channel.send(embed=embed)

    if pages > 1:
      await msg.add_reaction("⬅")
      await msg.add_reaction("➡")

    await asyncio.sleep(180)
    message = await ctx.channel.fetch_message(msg.id)
    message.embeds[0].color = 0xfc0365
    await msg.edit(embed=message.embeds[0])

  @personalcomputer.error
  async def personalcomputer_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command(aliases=['pd'])
  async def pokedex(self, ctx, pokemonSrc = None):
    if pokemonSrc == None:
      return await ctx.channel.send(f"{ctx.author.name}, especifique um pokemon para procurar.")

    pokemon =  await pokemon_exists(pokemonSrc)
 
    if pokemon == 404: 
      return await ctx.channel.send(f"{ctx.author.name}, pokemon não encontrado.")

    types = ''
    for i in pokemon['type']:
      types += f"{i.capitalize()} "

    embed = discord.Embed(color=0xDC0A2D)

    embed.set_image(url=f"{pokemon['image']}")

    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/890060279692550164/pokedex.png")
    embed.add_field(name="Espécie",value=f"{pokemon['name']}",inline=True)
    embed.add_field(name="Id",value=f"{pokemon['id']}",inline=True)
    embed.add_field(name="Raridade",value=f"{pokemon['rarity'].capitalize()}",inline=True)
    embed.add_field(name="Tipo",value=f"{types}",inline=False)
    await ctx.channel.send(embed=embed)
  @pokedex.error
  async def pokedex_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command(aliases=['tr', 'troca'])
  async def trade(self, ctx, member : discord.Member = None, tradeItem1 = None, tradeItem2 = None):
    res = await users_can_trade(ctx.guild.id, ctx.author.id, member.id)
    if res == 1:
      return await ctx.channel.send(f"{ctx.author.name}, você não pode trocar antes de pegar seu pokémon inicial.")
    elif res == 2:
      return await ctx.channel.send(f"{member.name} não pode trocar, pois ainda não escolheu seu pokémon inicial.")

    if member == None:
      return await ctx.channel.send(f"{ctx.author.name}, especifique um treinador com quem você quer trocar.") 
    elif ctx.author == member:
      return await ctx.channel.send(f"{ctx.author.name}, você não pode fazer uma troca com si mesmo.")
    elif tradeItem1 == None:
      return await ctx.channel.send(f"{ctx.author.name}, especifique o pokemon a ser trocado.")

    pokemon =  await pokemon_exists(tradeItem1)

    if pokemon == 404: 
      return await ctx.channel.send(f"{ctx.author.name}, pokemon não encontrado.")
    elif await user_has_pokemon(ctx.guild.id, ctx.author.id, pokemon['name']) == 404:
      return await ctx.channel.send(f"{ctx.author.name}, você não tem esse pokemon.")

    if tradeItem2 != None:
      pokemon2 = await pokemon_exists(tradeItem2)

      if pokemon2 == 404: 
        return await ctx.channel.send(f"{ctx.author.name}, pokemon não encontrado.")
      elif await user_has_pokemon(ctx.guild.id, member.id, pokemon2['name']) == 404:
        return await ctx.channel.send(f"{member.name}, não tem esse pokemon.")

    if tradeItem2 == None:
      res = await get_trade_embed(ctx.author, member, pokemon, {'name': 'Nada'})
    else:
      if pokemon['name'] == pokemon2['name']: return await ctx.channel.send(f"{ctx.author.name}, você não pode trocar dois pokemons iguais.")
      res = await get_trade_embed(ctx.author, member, pokemon, pokemon2)

    msg = await ctx.channel.send(embed=res['embed'])

    await msg.add_reaction('✅')

    def check(reaction, user):
      return user != self.bot.user and user == member and str(reaction) == '✅' and msg.id == reaction.message.id

    try:
      await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
      embed = discord.Embed()
      embed.set_image(url='https://media.discordapp.net/attachments/887158781832749086/888159074024292382/expired_trade.png?width=720&height=240')
      embed.set_footer(text=f"{ctx.author.name} x {member.name}")
      await msg.edit(embed=embed)
      await msg.clear_reactions() 
    else:
      if tradeItem2 == None:
        res = await user_trade_with_one_pokemon(ctx.guild.id, ctx.author.id, member.id, pokemon)
      else:
        res = await user_trade_with_two_pokemon(ctx.guild.id, ctx.author.id, member.id, pokemon, pokemon2)

      if res == 404:
        return await ctx.channel.send(f"{ctx.author.name}, você não tem esse pokemon.")
      elif res == 403:
        return await ctx.channel.send(f"{member.name} não tem esse pokemon.")

      embed = discord.Embed()
      embed.set_image(url='https://media.discordapp.net/attachments/887158781832749086/888159086942765076/sucessfull_trade.png?width=720&height=240')
      embed.set_footer(text=f"{ctx.author.name} x {member.name}")
      await msg.edit(embed=embed)
      await msg.clear_reactions() 
  @trade.error
  async def trade_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command(aliases=['shop', 'loja'])
  async def pokeshop(self, ctx):
    embed = discord.Embed(title='Bem-vindo a loja', color=0xFF99CD)
    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
    embed.set_thumbnail(url='https://media.discordapp.net/attachments/887158781832749086/889254271957221376/bolsa-de-compras.png')
    embed.add_field(name=f"{all_emojis['pokeball']}Pokeball", value=f"{price_itens['Pokeball']}", inline=True)
    embed.add_field(name=f"{all_emojis['greatball']}Greatball", value=f"{price_itens['Greatball']}", inline=True)
    embed.add_field(name=f"{all_emojis['ultraball']}Ultraball", value=f"{price_itens['Ultraball']}", inline=True)
    embed.set_footer(text='Use $buy Nome Quantidade para comprar')
    await ctx.channel.send(embed=embed)
  @pokeshop.error
  async def pokestore_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command(aliases=['b', 'comprar'])
  async def buy(self, ctx, itemName = None, quant : int = None):
    if itemName == None:
      return await ctx.channel.send(f"{ctx.author.name}, Especifique o item a ser comprado.")
    
    if quant == None or quant <= 0:
      quant = 1

    res = await user_buy_item(ctx.guild.id, ctx.author.id, itemName, quant)

    if res == 404:
      return await ctx.channel.send(f"{ctx.author.name}, o item especificado é invalido.")
    elif res == 507:
      return await ctx.channel.send(f"{ctx.author.name}, você não tem dinheiro o suficiente.")
    else:
      await ctx.channel.send(f"{ctx.author.name}, comprado {quant}x de {itemName}.")
  @buy.error
  async def buy_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command()
  async def daily(self, ctx):
    content = await get_daily_bonus(ctx.guild.id, ctx.author.id)

    if content['code'] == 408:
      return await ctx.channel.send(f"{ctx.author.name}, você já pegou seu bônus diario. Aguarde `{content['time']}` para pegá-lo novamente.")

    embed = discord.Embed(title="Bônus diario", description=f"**{content['content']}**", color=0x463B83)
    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/888841855893139547/present-box.png")
    await ctx.channel.send(embed=embed)
  @daily.error
  async def daily_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command(aliases=['bg', 'mochila'])
  async def bag(self, ctx):
    user_pokecoins, user_invetory = await get_user_bag(ctx.guild.id, ctx.author.id)

    user_invetory = OrderedDict(sorted(user_invetory.items(), key = lambda x: items_ordem.index(x[0])))

    embed = discord.Embed(title='Mochila', color=0x00B7F0)
    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
    embed.set_thumbnail(url='https://media.discordapp.net/attachments/887158781832749086/901580880164831313/mochila.png')

    embed.add_field(name="Pokecoins", value=f"{user_pokecoins}$", inline=True)

    for i in user_invetory:
      embed.add_field(name=f"{all_emojis[i.lower()]}{i}", value=f"{user_invetory[i]}x", inline=True)

    await ctx.channel.send(embed=embed)
  @bag.error
  async def inventory_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command(aliases=['op', 'abrir'])
  async def open(self, ctx, mName : str = None, quant : int = None):
    if quant == None: quant = 1

    if mName == None:
      return await ctx.channel.send(f"{ctx.author.name}, especifique o nome da caixa.")

    if not mName.isnumeric():
      mName = mName.lower().capitalize()

    res = await user_use_box(ctx.guild.id, ctx.author.id, mName, quant)

    if res['code'] == 400:
      return await ctx.channel.send(f"{ctx.author.name}, especifique uma caixa válida.")
    elif res['code'] == 404:
      return await ctx.channel.send(f"{ctx.author.name}, você não tem essa caixa.")
    elif res['code'] == 401:
      return await ctx.channel.send(f"{ctx.author.name}, você não tem essa quantidade de caixas.")

    embed = discord.Embed(title=f"Abriu {quant}x de {mName} e ganhou", description=f"**{res['content']}**", color=0x80B6FC)
    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
    embed.set_thumbnail(url=box_images[mName])
    await ctx.channel.send(embed=embed)
  @open.error
  async def open_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command(aliases=['pfl', 'perfil'])
  async def profile(self, ctx, member : discord.Member = None):
    if member != None:
      user = member
    else:
      user = ctx.author
 
    res = await get_user_profile(ctx.guild.id, user.id)
 
    embed = discord.Embed(title=f"{user.name}", color=0x28AE64)

    if res['pokemonEquip'] == '':
      res['pokemonEquip'] = "Nenhum"
    else:
      pokemon = await get_pokemon(res['pokemonEquip'])
      embed.set_image(url=f"{pokemon['image']}")

    embed.set_thumbnail(url=f"{user.avatar_url}")
    embed.add_field(name="Pokecoins",value=f"{res['pokecoins']} $",inline=True)
    embed.add_field(name="Total de Pokemons",value=f"{res['pokemons']}",inline=True)
    embed.add_field(name="Ranking",value=f"{res['ranking']}°",inline=True)
    embed.add_field(name="Classe",value=f"{res['class']}",inline=False)
    embed.add_field(name="Emblemas",value=f"{res['badges']}",inline=False)
    embed.add_field(name="Pokemon equipado",value=f"{res['pokemonEquip']}",inline=False)
    await ctx.channel.send(embed=embed)
  @profile.error
  async def profile_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command(aliases=['eq', 'equipar'])
  async def equip(self, ctx, pokemonSrc = None):
    if pokemonSrc == None:
      return await ctx.channel.send(f"{ctx.author.name}, especifique um pokemon.")

    pokemon =  await pokemon_exists(pokemonSrc)
 
    if pokemon == 404: 
      return await ctx.channel.send(f"{ctx.author.name}, pokemon não encontrado.")

    res = await user_has_pokemon(ctx.guild.id, ctx.author.id, pokemonSrc.lower().capitalize())

    if res == 404:
      return await ctx.channel.send(f"{ctx.author.name}, você não tem esse pokemon.")

    equip = await user_equip_pokemon(ctx.guild.id, ctx.author.id, pokemonSrc.lower().capitalize())

    if equip == 400:
      return await ctx.channel.send(f"{ctx.author.name}, esse pokemon já está equipado.")

    await ctx.message.add_reaction("✅")
  @equip.error
  async def equip_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command(aliases=['uq', 'desequipar'])
  async def unequip(self, ctx):
    res = await user_unequip_pokemon(ctx.guild.id, ctx.author.id)

    if res == 404:
      return await ctx.channel.send(f"{ctx.author.name}, você não tem nenhum pokemon equipado.")

    await ctx.message.add_reaction("✅")
  @unequip.error
  async def unequip_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command()
  async def huntlist(self, ctx):
    res = await get_user_huntlist(ctx.guild.id, ctx.author.id)
  
    if res['code'] == 400:
      return await ctx.channel.send(f"{ctx.author.name}, você não tem nenhum pokemon em sua huntlist.")

    embed = discord.Embed(title=f"Huntlist ({res['len']}/{res['max']})", description=f"{res['content']}", color=0xFFF5D2)
    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/900915566783660053/huntlist.png")
    await ctx.channel.send(embed=embed)
  @huntlist.error
  async def huntlist_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command()
  async def hunt(self, ctx, pokemonSrc = None):
    if pokemonSrc == None:
      return await ctx.channel.send(f"{ctx.author.name}, especifique um pokemon.")
      
    pokemon =  await pokemon_exists(pokemonSrc)
 
    if pokemon == 404: 
      return await ctx.channel.send(f"{ctx.author.name}, pokemon não encontrado.")

    res = await add_to_huntlist(ctx.guild.id, ctx.author.id, pokemon)

    if res == 400:
      return await ctx.channel.send(f"{ctx.author.name}, você atingiu o limite de sua huntlist.")
    elif res == 401:
      return await ctx.channel.send(f"{ctx.author.name}, esse pokemon já está em sua huntlist.")

    await ctx.message.add_reaction("✅")
  @hunt.error
  async def hunt_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command()
  async def huntremove(self, ctx, pokemonSrc = None):
    if pokemonSrc == None:
      return await ctx.channel.send(f"{ctx.author.name}, especifique um pokemon.")
      
    pokemon =  await pokemon_exists(pokemonSrc)
 
    if pokemon == 404: 
      return await ctx.channel.send(f"{ctx.author.name}, pokemon não encontrado.")

    res = await remove_from_huntlist(ctx.guild.id, ctx.author.id, pokemon)

    if res == 400:
      return await ctx.channel.send(f"{ctx.author.name}, Você não tem nenhum pokemon em sua huntlist.")
    elif res == 401:
      return await ctx.channel.send(f"{ctx.author.name}, Esse pokemon não está na sua huntlist.")

    await ctx.message.add_reaction("✅")
  @huntremove.error
  async def huntremove_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command(aliases=['ranking'])
  async def top(self, ctx):
    content = await get_guild_ranking(self.bot, ctx.guild.id)

    embed = discord.Embed(title="Top treinadores", description=f"​ \n{content}", color=0xFDBF00)
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/897360888183549962/wreath.png")

    await ctx.channel.send(embed=embed)
  @top.error
  async def top_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command(aliases=['clup', 'upgrade', 'up'])
  async def classupgrade(self, ctx):
    res = await get_class_utils(ctx.guild.id, ctx.author.id)

    if res['code'] == 401:
      return await ctx.channel.send(f"{ctx.author.name}, você está no nivel máximo.")

    msg = await ctx.channel.send(f"<:resource_in_beta:896230169054965760>{ctx.author.name}, você quer gastar ``{res['class_price']}`` pokecoins para passar de classe.")
    await msg.add_reaction('✅')

    def check(reaction, user):
        return user != self.bot.user and user == ctx.author and str(reaction) == '✅' and msg.id == reaction.message.id

    await self.bot.wait_for("reaction_add", timeout=20.0, check=check)

    res = await user_class_upgrade(ctx.guild.id, ctx.author.id)

    if res['code'] == 400:
      return await ctx.channel.send(f"{ctx.author.name}, você não tem pokecoins o suficiente.")
    elif res['code'] == 401:
      return await ctx.channel.send(f"{ctx.author.name}, você está no nivel máximo.")

    await ctx.channel.send(f"{ctx.author.name}, parabéns! agora você está na classe ``{res['class']}``.")
  @classupgrade.error
  async def classupgrade_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command()
  async def release(self, ctx, pokemonSrc = None, quant : int = None):
    if ctx.author.id in self.release_list:
      return
    if pokemonSrc == None:
      return await ctx.channel.send(f"{ctx.author.name}, especifique um pokemon.")

    pokemon = await pokemon_exists(pokemonSrc)

    if pokemon == 404:
      return await ctx.channel.send(f"{ctx.author.name}, pokemon não encontrado.")

    if quant == None or quant <= 0: quant = 1

    price = await get_pokemon_price(ctx.guild.id, ctx.author.id, pokemon, quant)

    if price == 404:
      return await ctx.channel.send(f"{ctx.author.name}, você não tem esse pokemon.")
    elif price == 401:
      return await ctx.channel.send(f"{ctx.author.name}, você não tem **{quant}x de {pokemon['name']}**.")

    self.release_list.append(ctx.author.id)

    await ctx.channel.send(f"{ctx.author.name}, ao vender **{quant}x de {pokemon['name']}** você ganha **{price} pokecoins**, digite(y/n) para aceitar ou cancelar.")

    def check(message):
      return message.author == ctx.author

    while True:
      try:
        message = await self.bot.wait_for("message", timeout=30.0, check=check)
      except:
        return self.release_list.remove(ctx.author.id)
      else:
        if message.author == self.bot.user:
          print("Bot message")
          continue
        if message.content.lower() == 'n':
          self.release_list.remove(ctx.author.id)
          return await ctx.channel.send(f"{ctx.author.name}, release cancelado.")
        elif message.content.lower() == 'y':
          res = await release_pokemon(ctx.guild.id, ctx.author.id, pokemon, quant, price)

          if res == 404:
            return await ctx.channel.send(f"{ctx.author.name}, você não tem esse pokemon.")
          elif res == 401:
            return await ctx.channel.send(f"{ctx.author.name}, você não tem ``{quant}x`` de ``{pokemon['name']}``.")

          await message.add_reaction('✅')
          return self.release_list.remove(ctx.author.id)
        else: continue
  @release.error
  async def release_error(self, ctx, error): pass

  @commands.cooldown(1, 300, commands.BucketType.guild)
  @commands.command()
  async def classes(self, ctx):
    embed = discord.Embed(title="Classes de treinador", description='''
**
Treinador novato:
```
  Preço: -
  Cooldown no P: 30 minutos
  Tamanho da Huntlist: 3
```
Treinador novato II:
```
  Preço: 1000 pokecoins
  Cooldown no P: 28,5 minutos
  Tamanho da Huntlist: 3
  Chance de captura base + 1
```
Treinador novato III:
```
  Preço: 2000 pokecoins
  Cooldown no P: 27 minutos
  Tamanho da Huntlist: 3
  Chance de captura base + 1
```
Treinador:
```
  Preço: 3000 pokecoins
  Cooldown no P: 25,5 minutos
  Tamanho da Huntlist: 4
  Chance de captura base + 1
```
Treinador II:
```
  Preço: 4000 pokecoins
  Cooldown no P: 24 minutos
  Tamanho da Huntlist: 4
  Chance de captura base + 1
```
Treinador III:
```
  Preço: 5000 pokecoins
  Cooldown no P: 22,5 minutos
  Tamanho da Huntlist: 4
  Chance de captura base + 1
```
Treinador de Elite:
```
  Preço: 6000 pokecoins
  Cooldown no P: 21 minutos
  Tamanho da Huntlist: 5
  Chance de captura base + 1
```
Treinador de Elite II:
```
  Preço: 7000 pokecoins
  Cooldown no P: 19,5 minutos
  Tamanho da Huntlist: 5
  Chance de captura base + 1
```
Treinador de Elite III:
```
  Preço: 8000 pokecoins
  Cooldown no P: 18 minutos
  Tamanho da Huntlist: 5
  Chance de captura base + 1
```
Professor Pokémon:
```
  Preço: 9000 pokecoins
  Cooldown no P: 16,5 minutos
  Tamanho da Huntlist: 6
  Chance de captura base + 1
```
Professor Pokémon II:
```
  Preço: 10000 pokecoins
  Cooldown no P: 15 minutos
  Tamanho da Huntlist: 6
  Chance de captura base + 1
```
Professor Pokémon III:
```
  Preço: 11000 pokecoins
  Cooldown no P: 13,5 minutos
  Tamanho da Huntlist: 6
  Chance de captura base + 1
```
Mestre Pokémon:
```
  Preço: 12000 pokecoins
  Cooldown no P: 10 minutos
  Tamanho da Huntlist: 7
  Chance de captura base + 1
```
**
    ''', color=0xE56BFF)
    embed.set_footer(text="use $classupgrade para passar de classe.")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/901585840319397928/classes.png")
    await ctx.channel.send(embed=embed)
  @classes.error
  async def classes_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      m, s = divmod(int(error.retry_after), 60)
      h, m = divmod(m, 60)
      await ctx.channel.send("{},Você só pode usar esse comando novamente em ``{:02d}:{:02d}:{:02d}``.".format(ctx.author.name, h, m, s))

  @commands.Cog.listener()
  async def on_reaction_add(self, reaction, user):
    if user != self.bot.user and str(reaction.emoji) in ['⬅', '➡']:
      if 'AirctunoBot Desenvolvemento#7711' == str(user) or str(reaction.message.embeds[0].color) not in ['#fc0367', '#fc0366']: return

      rare = ''
      color = 0xfc0367

      if str(reaction.message.embeds[0].color) == '#fc0366':
        rare = 'rares'
        color = 0xfc0366

      quants = []

      try:
        footer = reaction.message.embeds[0].footer.text.split(' ')
        author = await self.bot.fetch_user(reaction.message.embeds[0].author.icon_url.split('/')[4])
      except: return

      page = int(footer[5])

      user_pokemons = await get_user_pokemons(reaction.message.guild.id, author.id)

      if rare == 'rares':
        user_pokemons = OrderedDict(reversed(sorted(user_pokemons.items(), key = lambda x: (pokemon_rarity_ordem.get(x[1]['rarity']), x[1]['quant']))))
        quants = await get_user_pokemons_rarity(user_pokemons)
      else:
        user_pokemons = OrderedDict(reversed(user_pokemons.items()))

      if len(user_pokemons) == 0:
        return await reaction.message.channel.send(f"{user.name}, você não tem pokemons.")

      pages = math.ceil(len(user_pokemons) / 10)

      if pages == 1: return

      if str(reaction.emoji) == '⬅':
        page -=  1
        if page < 1: page = pages
      if str(reaction.emoji) == '➡':
        page +=  1
        if page > pages: page = 1

      start = (page - 1) * 10
      end = start + 10

      content = ''
      actually_rarity = ''

      aux = 1
      for i in user_pokemons:
        rarity = user_pokemons[i]['rarity']
        if rare == 'rares':
          if actually_rarity != rarity:
            actually_rarity = rarity
            if not aux < start and aux < end:
              content += f" \n{emojis_rarity[rarity]}**{rarity.capitalize()}({quants[rarity]}):**\n"
        if not aux < start and aux < end:
          content += f"**{i} {user_pokemons[i]['quant']}x**\n"
        aux += 1

      embed = discord.Embed(description=f"​ \n{content}", color=color)
      embed.set_author(name=f"{author.name}", icon_url=f"{author.avatar_url}")
      embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/890060279692550164/pokedex.png")
      embed.set_footer(text=f"{len(user_pokemons)} / 898 - Page {page} / {pages}")

      await reaction.message.edit(embed=embed)

  @commands.Cog.listener()
  async def on_reaction_remove(self, reaction, user):
    if user != self.bot.user and str(reaction.emoji) in ['⬅', '➡']:
      if 'AirctunoBot Desenvolvemento#7711' == str(user) or str(reaction.message.embeds[0].color) not in ['#fc0367', '#fc0366']: return

      rare = ''
      color = 0xfc0367

      if str(reaction.message.embeds[0].color) == '#fc0366':
        rare = 'rares'
        color = 0xfc0366

      quants = []
      
      try:
        footer = reaction.message.embeds[0].footer.text.split(' ')
        page = int(footer[5])
        author = await self.bot.fetch_user(reaction.message.embeds[0].author.icon_url.split('/')[4])
      except: return

      user_pokemons = await get_user_pokemons(reaction.message.guild.id, author.id)

      if rare == 'rares':
        user_pokemons = OrderedDict(reversed(sorted(user_pokemons.items(), key = lambda x: (pokemon_rarity_ordem.get(x[1]['rarity']), x[1]['quant']))))
        quants = await get_user_pokemons_rarity(user_pokemons)
      else:
        user_pokemons = OrderedDict(reversed(user_pokemons.items()))

      if len(user_pokemons) == 0:
        return await reaction.message.channel.send(f"{user.name}, você não tem pokemons.")

      pages = math.ceil(len(user_pokemons) / 10)

      if pages == 1: return

      if str(reaction.emoji) == '⬅':
        page -=  1
        if page < 1: page = pages
      if str(reaction.emoji) == '➡':
        page +=  1
        if page > pages: page = 1

      start = (page - 1) * 10
      end = start + 10

      content = ''
      actually_rarity = ''

      aux = 1
      for i in user_pokemons:
        rarity = user_pokemons[i]['rarity']
        if rare == 'rares':
          if actually_rarity != rarity:
            actually_rarity = rarity
            if not aux < start and aux < end:
              content += f" \n{emojis_rarity[rarity]}**{rarity.capitalize()}({quants[rarity]}):**\n"
        if not aux < start and aux < end:
          content += f"**{i} {user_pokemons[i]['quant']}x**\n"
        aux += 1

      embed = discord.Embed(description=f"​ \n{content}", color=color)
      embed.set_author(name=f"{author.name}", icon_url=f"{author.avatar_url}")
      embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/890060279692550164/pokedex.png")
      embed.set_footer(text=f"{len(user_pokemons)} / 898 - Page {page} / {pages}")

      await reaction.message.edit(embed=embed)

def setup(bot):
  bot.add_cog(Pokemon_user(bot))