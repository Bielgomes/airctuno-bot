import discord
from discord.ext import commands
import asyncio
from database import *
from api import *
from utils.get_utils import *

class Pokemon_admin(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.is_owner()
  @commands.command(aliases=['sp'])
  async def spawn(self, ctx, pokemonSrc = None):
    pokemon =  await pokemon_exists(pokemonSrc)
    
    if pokemon == 204:
      embed = await get_none_pokemon_embed(ctx.author)
      return await ctx.channel.send(embed=embed)

    embed = await get_embed(pokemon, ctx.author)
    msg = await ctx.channel.send(embed=embed)

    emojis = await get_emoji(True)

    for i in emojis:
      await msg.add_reaction(emojis[i])

    def check(reaction, user):
        return user != self.bot.user and reaction.message.id == msg.id

    while True:
      try:
        reaction, user = await self.bot.wait_for("reaction_add", timeout=19.0, check=check)
      except asyncio.TimeoutError:
        embed = await get_pokemon_run_embed(pokemon)
        await msg.clear_reactions()
        return await msg.edit(embed=embed)
      else:
        use_pokeball = await user_use_pokeball(ctx.guild.id, user.id, str(reaction))

        if use_pokeball['code'] == 404:
          await ctx.channel.send(f"{user.name} não tem {use_pokeball['pokeball']}s")
          continue
        
        if use_pokeball['code'] == 403: continue

        was_captured = await catch_successful(ctx.guild.id, user.id, reaction, pokemon['rarity'])

        if was_captured == 200:
          await msg.clear_reactions()
          await user_catch_pokemon(ctx.guild.id, user.id, pokemon)

          embed = discord.Embed(title=f"{pokemon['name']} Capturado!", description="Que belo pokemon para sua coleção. Agora vá e capture mais!", color=0x00FF85)
          embed.set_author(name=f"{user}", icon_url=f"{user.avatar_url}")
          embed.set_image(url=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon['id']}.png")
          embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/887402098721960036/png-transparent-poke-ball-pokemon-pokemon-rim-mobile-phones-pokemon-thumbnail.png?width=677&height=676")
          
          res = await get_misteryBox(pokemon['rarity'])

          if res != None:
            embed.set_footer(text=f"Você ganhou {res['quant']}x de {res['mNameEmbed']}")
            await add_in_user_inventory(ctx.guild.id, user.id, res['mName'], res['quant'])

          return await msg.edit(embed=embed)
        elif was_captured == None:
          embed = await get_pokemon_run_embed(pokemon)
          await msg.clear_reactions()
          return await msg.edit(embed=embed)
  @spawn.error
  async def spawn_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.is_owner()
  @commands.command(aliases=['ap'])
  async def addpokemon(self, ctx, member : discord.Member = None, pokemonSrc = None, quant : int = None):
    if member == None:
      return await ctx.channel.send(f"{ctx.author.name}, Especifique um treinador.")
    if pokemonSrc == None:
      return await ctx.channel.send(f"{ctx.author.name}, Especifique um pokemon para adicionar ao treinador.")
    
    pokemon =  await pokemon_exists(pokemonSrc)
    
    if pokemon == 404: 
      return await ctx.channel.send("Pokemon não encontrado.")

    if quant == None or quant <= 0 or quant >= 301:
      quant = 1

    user_id = ctx.author

    if member != None:
      user_id = member
    
    await user_catch_pokemon(ctx.guild.id, user_id.id, pokemon, quant)

    await ctx.channel.send(f"Adicionados {quant}x de {pokemon['name']} ao pc de {user_id.name}.")
  @addpokemon.error
  async def addpokemon_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.is_owner()
  @commands.command(aliases=['apc'])
  async def addpokecoins(self, ctx, member : discord.Member = None, quant : int = None):
    if member == None:
      return await ctx.channel.send(f"{ctx.author.name}, Especifique um treinador para dar o dinhero.")
    if quant == None or quant <= 0:
      return await ctx.channel.send("Quantidade invalida.")

    await user_inc_money(ctx.guild.id, member.id, quant)

    await ctx.channel.send(f"Foram adicionados {quant} pokecoin(s) ao inventário de {member.name}")
  @addpokecoins.error
  async def addpokecoins_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.is_owner()
  @commands.command(aliases=['ait'])
  async def additem(self, ctx, member : discord.Member = None, itemName : str = None, quant : int = None):
    if member == None:
      return await ctx.channel.send(f"{ctx.author.name}, especifique um treinador.")
    if itemName == None or itemName.isnumeric():
      return await ctx.channel.send("Item inválido.")

    if quant == None or quant <= 0: quant = 1

    itemName = itemName.lower().capitalize()

    res = await add_in_user_inventory(ctx.guild.id, member.id, itemName, quant)

    if res == 404: return await ctx.channel.send("Item inválido.")

    await ctx.channel.send(f"Adicionados {quant}x de {itemName} ao inventário de {member.name}")
  @additem.error
  async def additem_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.is_owner()
  @commands.command()
  async def pokemonrating(self, ctx, num : int = None):
    if num == None or num > 10000:
      num = 1000

    res = await pokemon_rate_test(num)

    content = ''
    for i in res:
      content += f"**{i}:** {res[i]}\n"

    embed = discord.Embed(title="Debugging", description=f'​ \n\n{content}', color=0x00ACE5)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/887158781832749086/891852083467264000/google-analytics.png")
    await ctx.channel.send(embed=embed)
  @pokemonrating.error
  async def pokemonrating_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.is_owner()
  @commands.command()
  async def addbadge(self, ctx, member : discord.Member = None, badge = None):
    if member == None:
      return await ctx.channel.send(f"{ctx.author.name}, especifique um treinador.")

    if badge == None:
      return await ctx.channel.send(f"{ctx.author.name}, especifique uma badge.")

    res = await add_user_badge(ctx.guild.id, member.id, badge.lower().capitalize())

    if res == 404:
      return await ctx.channel.send(f"{ctx.author.name}, essa badge não existe.")
    elif res == 400:
      return await ctx.channel.send(f"{ctx.author.name}, o usuário já tem essa badge.")

    await ctx.channel.send(f"{ctx.author.name}, a badge foi adiciona ao usuário.")
  @addbadge.error
  async def addbadge_error(self, ctx, error): pass

  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.has_permissions(ban_members=True)
  @commands.command(aliases=['pf'])
  async def prefix(self, ctx, prefix : str = None):
    if prefix != None:
      await change_prefix(ctx.guild.id, prefix)
    else:
      return await ctx.channel.send("Prefix inválido.")
  @prefix.error
  async def prefix_error(self, ctx, error): pass

def setup(bot):
  bot.add_cog(Pokemon_admin(bot))