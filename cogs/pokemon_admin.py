import discord
from discord.ext import commands

from utils.database import *
from utils.api import *
from utils.utils import *
from utils.config import emojis_pokeball

import asyncio
import os

class Pokemon_admin(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.is_owner()
  @commands.command()
  async def unload(self, ctx, extension):
    self.bot.unload_extension(f"cogs.{extension}")

  @commands.is_owner()
  @commands.command()
  async def reload(self, ctx):
    for filename in os.listdir("./cogs"):
      if filename.endswith(".py"):
        self.bot.unload_extension(f"cogs.{filename[:-3]}")
        self.bot.load_extension(f"cogs.{filename[:-3]}")
    
  @commands.is_owner()
  @commands.command(aliases=['sp'])
  async def spawn(self, ctx, pokemonSrc = None):
    pokemon =  await pokemon_exists(pokemonSrc)
    
    if pokemon == 404:
      return await ctx.channel.send("O pokemon informado é inválido.")

    embed = await get_pokemon_embed(pokemon, ctx.author)
    
    msg = await ctx.channel.send(embed=embed)

    for i in emojis_pokeball:
      await msg.add_reaction(emojis_pokeball[i])

    def check(reaction, user):
        return user != self.bot.user and reaction.message.id == msg.id

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

          embed.set_image(url=pokemon['image'])
          embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/899811541971513384/pokeball.png")

          if res != None:
            embed.set_footer(text=f"Você ganhou {res['quant']}x de {res['mNameEmbed']}")

          await msg.edit(embed=embed)
          return await msg.clear_reactions()
        else:
          embed = await get_pokemon_run_embed(pokemon)
          await msg.edit(embed=embed)
          return await msg.clear_reactions()
  @commands.is_owner()
  @commands.command(aliases=['ap'])
  async def addpokemon(self, ctx, member : discord.Member = None, pokemonSrc = None, quant : int = None):
    if member == None:
      return await ctx.channel.send(f"{ctx.author.name}, Especifique um treinador.")
    if pokemonSrc == None:
      return await ctx.channel.send(f"{ctx.author.name}, Especifique um pokemon para adicionar ao treinador.")

    pokemon = await pokemon_exists(pokemonSrc)

    if pokemon == 404: 
      return await ctx.channel.send(f"{ctx.author.name}, pokemon não encontrado.")

    if quant == None or quant <= 0:
      quant = 1

    user_id = ctx.author

    if member != None:
      user_id = member

    await user_catch_pokemon(ctx.guild.id, user_id.id, pokemon, None, quant)

    await ctx.channel.send(f"Adicionados {quant}x de {pokemon['name']} ao pc de {user_id.name}.")

  @commands.is_owner()
  @commands.command(aliases=['apc'])
  async def addpokecoins(self, ctx, member : discord.Member = None, quant : int = None):
    if member == None:
      return await ctx.channel.send(f"{ctx.author.name}, Especifique um treinador para dar o dinhero.")
    if quant == None or quant <= 0:
      return await ctx.channel.send("Quantidade invalida.")

    await user_inc_money(ctx.guild.id, member.id, quant)

    await ctx.channel.send(f"Foram adicionados {quant} pokecoin(s) ao inventário de {member.name}")

  @commands.is_owner()
  @commands.command(aliases=['ait'])
  async def additem(self, ctx, member : discord.Member = None, itemName : str = None, quant : int = None):
    if member == None:
      return await ctx.channel.send(f"{ctx.author.name}, especifique um treinador.")
    if itemName == None or itemName.isnumeric():
      return await ctx.channel.send("Item inválido.")

    if quant == None or quant <= 0: quant = 1

    itemName = itemName.lower().capitalize()

    res = await add_in_user_bag(ctx.guild.id, member.id, itemName, quant)

    if res == 404: return await ctx.channel.send("Item inválido.")

    await ctx.channel.send(f"Adicionados {quant}x de {itemName} ao inventário de {member.name}")

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

  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.has_permissions(ban_members=True)
  @commands.command(aliases=['pf', 'changep'])
  async def changeprefix(self, ctx, prefix : str = None):
    if prefix != None:
      res = await change_prefix(ctx.guild.id, prefix)
      if res == 400:
        return await ctx.channel.send(f"{ctx.author.name}, esse prefixo é **igual** ao anterior.")
      return await ctx.channel.send(f"{ctx.author.name}, prefixo regional alterado para ``{prefix}``.")
  @changeprefix.error
  async def changeprefix_error(self, ctx, error): pass

def setup(bot):
  bot.add_cog(Pokemon_admin(bot))
