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
    await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name="$help | Beta early access 1.1.0", type=3))


  @commands.cooldown(1, 2, commands.BucketType.guild)
  @commands.command(aliases=['hp'])
  async def help(self, ctx):
    embed = discord.Embed(description='''
    ​
🐱‍👤**Bem-vindo treinador, este é o nosso centro de ajuda!**

Eu, o professor Ednaldo irei te guiar nos comandos e funcionalidades do bot.

antes de começar temos algumas Convenções
**```
<> = parâmetro opcional⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
[] = parâmetro obrigatório
pokemon = nome ou id
```



__🎁DAILY:__
```
O comando daily dá ao treinador um bônus diario.

Protótipo: $daily

Cooldown: exatamente as 00:00 do dia seguinte.
```



__🛒POKESHOP:__
SINÔNIMOS: shop, loja
```
O comando pokeshop mostra os itens que podem ser comprados.

Protótipo: $pokeshop
```



__💳BUY:__
SINÔNIMOS: b, comprar
```
O comando buy permite ao treinador comprar itens da loja.

Protótipo: $buy [item] <quantidade>
```



__📂BAG:__
SINÔNIMOS: bg, mochila
```
O comando bag permite ao treinador ver sua mochila. Nela estão suas pokecoins e pokebolas.

Protótipo: $bag
```



🐱‍👓__POKEMON:__
SINÔNIMOS: p, pm
```
O comando pokemon permite ao treinador procurar um pokemon aleatório. Qualquer um pode pegar esse pokemon, então seja rápido.

Protótipo: $pokemon

Cooldown Padrão: 30 minutos
```



__📦OPEN:__
SINÔNIMOS: op, abrir
```
O comando open abre uma box.

Protótipo: $open [boxName] <quantidade>
```



__🖼PROFILE:__
SINÔNIMOS: pfl, perfil
```
O comando profile mostra o seu perfil.

Protótipo: $profile
```



__💻PERSONALCOMPUTER:__
SINÔNIMOS: pc
```
O Comando personalcomputer mostra todos os pokemons capturados pelo treinador.

Protótipo: $personalcomputer <treinador>
```



__🏆TOP__
SINÔNIMOS: ranking
```
O comando top mostra os melhores treinadores da sua região.

Protótipo: $top
```



__🥼EQUIP:__
SINÔNIMOS: eq
```
O comando equip equipa um pokemon. Ele aparece em seu profile.

Protótipo: $equipe [pokémon]
```



__🥼UNEQUIP:__
SINÔNIMOS: uq, equipar
```
O comando unequip irá desequipar qualquer pokemon que esteja equipado.

Protótipo: $unequip
```



__🔎POKEDEX:__
SINÔNIMOS: pd
```
O comando pokedex procura as informações do pokemon dentro de nosso banco de dados.

Protótipo: $pokedex [pokémon]
```



__💵RELEASE:__
SINÔNIMOS:
```
O comando release permite ao jogador vender pokemons.

Protótipo: $release [pokémon] <quantidade>
```



__🎎CLASSES:__
```
O comando classes mostra todas as classes de treinador e seus beneficios.

Protótipo: $classes
```



__🔼CLASSUPGRADE:__
SINÔNIMOS: clup, upgrade, up
```
O comando classupgrade permite o jogador passar de classe.

Protótipo: $classupgrade
```



__🤝TRADE:__
SINÔNIMOS: tr, troca
```
O comando trade faz uma troca de pokemons entre dois treinadores.

Protótipo: $trade [treinador] [pokémon a ser dado] <pokémon a ser recebido>
```



__🏷HUNTLIST:__
```
O Comando huntlist mostra os pokemons na sua lista de caça.

Protótipo: $huntlist
```



__🏷HUNT:__
```
O Comando hunt adiciona um pokemon a sua lista de caça.

Protótipo: $hunt [pokémon]
```



__🏷HUNTREMOVE:__
```
O Comando huntremove remove um pokemon de sua lista de caça.

Protótipo: $huntremove [pokémon]
```



COMANDOS DE ADMINISTRADOR



__🎉PREFIX:__
```
O comando prefix seta prefixo novo ao bot na sua região.

Protótipo: $prefix [prefixo]
```



Muito bem! agora que aprendeu tudo você está pronto para ir em sua jornada e se tornar o melhor Mestre Pokémon.**

O Professor Ednaldo te deseja boa sorte!
    ''', color=0x474F70)
    embed.set_image(url="https://media.discordapp.net/attachments/887158781832749086/901569756308570112/Professor_Ednaldo.png")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/887158781832749086/901583410294841354/Professor_Ednaldo.png")
    embed.set_author(name=f"{self.bot.user.name}", icon_url=f"{self.bot.user.avatar_url}")
    try:
      await ctx.author.send(embed=embed)
    except:
      await ctx.channel.send(f"{ctx.author.name}, para receber essa mensagem você precisa liberar sua DM.")
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