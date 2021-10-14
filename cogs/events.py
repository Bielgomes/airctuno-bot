from os import name
from discord.ext.commands.core import check
import discord
import datetime
import asyncio
from discord import message
from discord.ext import tasks, commands
from discord.ext.commands import CommandNotFound

class Events(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print("@============@")
    print("| BOT ONLINE |")
    print("@============@")
    await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name="$help | Beta early access 1.0.5", type=3))


  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command(aliases=['hp'])
  async def help(self, ctx):
    embed = discord.Embed(description='''
    ​
    🐱‍👤**Bem-vindo treinador, ao nosso centro de ajuda a treinadores. Nós os professores iremos listar os comandos e suas ações.**



   ** Convenções:**
    **<>** = parâmetro opcional
    **[]** = parâmetro obrigatório



    **__🐱‍👓POKEMON:__**
    **abreviações**: 'p', 'pm'
    O comando pokemon spawna um pokemon aleatório que pode-ser pego por qualquer um, então seja rápido.

    **Protótipo**: $pokemon

    **Cooldown**: 5 minutos



    **__🏷WISHLIST:__**
    O Comando wishlist mostra os pokemons na sua lista de desejos.

    **Protótipo**: $wishlist



    **__🏷WISH:__**
    O Comando wish adiciona um pokemon a sua lista de desejos.

    **Protótipo**: $wish [pokemon]



    **__🏷UNWISH:__**
    O Comando unwish remove um pokemon de sua lista de desejos.

    **Protótipo**: $unwish [pokemon]



    **__💻PERSONALCOMPUTER:__**
    **abreviação**: 'pc'
    O Comando personalcomputer mostra todos os pokemons capturados pelo treinador.

    **Protótipo**: $personalcomputer <treinador>



    **__🔎POKEDEX:__**
    **abreviação**: 'pd'
    O comando pokedex procura o pokemon escolhido dentro da nossa API e retorna suas informações.

    **Protótipo**: $pokedex [nome ou id]



    **__🤝TRADE:__**
    **abreviação**: 'tr'
    O comando trade faz uma troca de pokemons entre dois treinadores.

    **Protótipo**: $trade [treinador] [pokemon a ser dado] <pokemon a ser recebido>
    OBS: pode ser informado o nome ou id do pokemon.



    **__🛒POKESHOP:__**
    **abreviação**: 'shop'
    O comando pokeshop irá mostra a loja e seus itens que podem ser comprados.

    **Protótipo**: $pokeshop



    **__💳BUY:__**
    **abreviação**: 'b'
    O comando buy serve para comprar itens da loja.

    **Protótipo**: $buy [item] <quantidade>
    OBS: quando a quantidade não é informada o bot irá comprar uma unidade.



    **__🎁DAILY:__**
    O comando daily da ao treinador um bônus todo dia, dentre eles, pokecoins, pokeballs e ultraballs

    **Protótipo**: $daily

    **Cooldown**: acaba quando o dia passar



    **__📂INVENTORY:__**
    **abreviação**: 'inv'
    O comando inventory permite ao treinador ver sua inventário. Estão nele informações como seus pokecoins e pokebolas.

    **Protótipo**: $inventory



    **__📦OPEN:__**
    O comando open abre uma mistery box.

    **Protótipo:** $open [boxName]



    **__📦PROFILE:__**
    **abreviação**: 'pfl'
    O comando profile mostra o seu perfil

    **Protótipo:** $profile



    **__📦EQUIP:__**
    **abreviação**: 'eq'
    O comando equip equipa um pokemon que irá aparecer em seu profile

    **Protótipo:** $equipe [pokemon]



    **__📦UNEQUIP:__**
    **abreviação**: 'uq'
    O comando unequip irá desequipar qualquer pokemon que esteja equipado.

    **Protótipo:** $unequip



    **__🎉PREFIX:__**
    O comando prefix seta um novo prefixo para o bot em um servidor

    **Protótipo:** $prefix [prefixo]


    
    **Após aprender os comandos você está pronto para seguir sua jornada e se tornar o melhor treinador pokemon.**

    ''', color=0x474F70)
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/891140932160880641/help.png")
    embed.set_author(name=f"{self.bot.user.name}", icon_url=f"{self.bot.user.avatar_url}")
    await ctx.author.send(embed=embed)
  @help.error
  async def help_error(self, ctx, error): pass

  @commands.Cog.listener()
  async def on_command_error(self, ctx, error):
    if isinstance(error, commands.CommandNotFound):
      return await ctx.channel.send(f"{ctx.author.name}, comando não encontrado.")
    if isinstance(error, commands.MissingPermissions):
      return await ctx.channel.send(f"{ctx.author.name}, você não tem permissão.")

def setup(bot):
  bot.add_cog(Events(bot))