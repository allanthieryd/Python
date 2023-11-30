'''
Bot discord en Python
Allan et Hugo Wehrlé
'''

import discord
from discord.ext import commands
import forex_python.converter as converter
import random

#On met toutes les autorisations à True
intents = discord.Intents().all()
bot = commands.Bot(command_prefix="!", intents=intents)
intents.messages = True
intents.message_content = True
intents.members = True
intents.guilds = True
intents.presences = True
channel = bot.get_channel(1179716275224707143) #ID du channel général du serveur Bot Discord

@bot.event #Message dans la console permettant de vérifier si le bot est opérationnel
async def on_ready():
    print("Prêt!")
    if channel:
        await channel.send(f"{bot.user.name} vient de se réveiller de sa sieste !")

@bot.event
async def on_error():
    print("Repos...")
    if channel:
        await channel.send(f"{bot.user.name} est parti faire une sieste...")


'''
Fonction helpme: Liste toutes les fonctions existantes
Utilisation: !helpme
 '''
@bot.command()
async def helpme(ctx):
	await ctx.send(':arrow_right:	-	**!serverInfo** : Donne des infos sur le serveur'
		'\n:arrow_right:	-	**!online** : Affiche les gens connectés'
		'\n:arrow_right:	-	**!chifoumi <pierre,feuille ou ciseaux>** : Pierre feuille ciseaux.'
		'\n:arrow_right:	-	**!sondage <question>** : Lance un sondage.'
		'\n:arrow_right:	-	**!convert <devise1> <devise2> <montant>** : Convertir des monnaies.')

#Fonction de bienvenue, lorsqu'un membre rejoint le serveur
@bot.event
async def on_member_join(member):
    await channel.send(f"Souhaitez la bienvenue à {member.mention} sur le serveur")

@bot.event
async def on_message(message):
    if message.author == bot.user:#si l'auteur du message est le bot, on ne retourne rien
        return

    ban_word_list = ["Allan", "Ranvir", "Python", "Laurent", "Tristan"] #Liste de mots bannis

    # Vérification qu'il n'y a pas de mots bannis dans le message converti en minuscule 
    if any(word.lower() in message.content.lower() for word in ban_word_list):
        await message.delete()
        await message.channel.send(f"Bah alors {message.author.mention}, on se permet d'envoyer des mots bannis ?")
        return
    
    await bot.process_commands(message)

@bot.command() #Test de la fonctionnalité du bot...
async def members(ctx):
    await ctx.send("Coucou !")


'''
Fonction serverInfo: Permet de donner des infos sur le serveur, tel que le nom du serveur
et son nombre de membres ainsi que le nombre de channels textuels et vocaux
Utilisation: !serverInfo
 '''
@bot.command()
async def serverInfo(ctx):
    server = ctx.guild
    numberOfTextChannels = len(server.text_channels)
    numberOfVoiceChannels = len(server.voice_channels)
    numberOfPerson = server.member_count
    serverName = server.name
    await ctx.send(f"Le seveur {serverName} contient {numberOfPerson} personnes.\nIl y a {numberOfTextChannels} channels textuels et {numberOfVoiceChannels} channels vocaux.")

'''
Fonction online: Permet de donner le nombre de membres en ligne
Utilisation: !online
 '''
@bot.command()
async def online(ctx):
    count = 0
    for member in ctx.guild.members:
        if member.status == discord.Status.online:
            count += 1
    await ctx.send(f"Il y a {count} membres en ligne.")

'''
Fonction sondage: Permet de créer un sondage avec 2 choix
Utilisation: !sondage <question>
Exemple: !sondage Tu préfères le pain au chocolat ou la chocolatine @everyone ?
 '''
sondage_reactions = {}

@bot.command()
async def sondage(ctx, *, question):
    global sondage_reactions
    message = await ctx.send(f"Sondage: {question}")
    message_id = message.id
    sondage_reactions[message_id] = {}

    # Réactions
    reactions = [
        '\N{DIGIT ONE}\N{COMBINING ENCLOSING KEYCAP}',
        '\N{DIGIT TWO}\N{COMBINING ENCLOSING KEYCAP}',
    ]

    for reaction in reactions:
        await message.add_reaction(reaction)

#Permet d'ajouter une réaction au message et les compter
@bot.event
async def on_raw_reaction_add(payload):
    global sondage_reactions
    message_id = payload.message_id
    if message_id in sondage_reactions:
        emoji = str(payload.emoji)
        if emoji in sondage_reactions[message_id]:
            sondage_reactions[message_id][emoji] += 1
        else:
            sondage_reactions[message_id][emoji] = 1

'''
Fonction convert: Permet de changer convertir un montant d'une monnaie à l'autre
Utilisation: !convert <monnaie1> <monnaie2> <montant>
Exemple: !convert EUR USD 100
 '''
@bot.command()
async def convert(ctx, src_currency: str, dest_currency: str, amount: float):
    try:

        if amount is None or amount == "":
            raise ValueError("Montant non fourni")
        # Taux de conversion
        conversion_rate = converter.get_rate(src_currency, dest_currency)


        converted_amount = amount * conversion_rate


        formatted_amount = "{:.2f}".format(converted_amount)

        # Conversion entre les deux devises
        await ctx.send(f'{amount} {src_currency} équivaut à {formatted_amount} {dest_currency}.')
    except converter.RatesNotAvailableError:
        await ctx.send("Erreur: Impossible d'interpréter les taux de conversion. Merci de réesayer.")
    except converter.CurrencyCodesError:
        await ctx.send("Erreur: Codes de devises non valides. Veuillez fournir des codes de devises valides")
    except ValueError as ve:
        await ctx.send(f"Erreur de valeur: {str(ve)}")
    except Exception as e:
        await ctx.send(f"Une erreur est survenue: {str(e)}")

@bot.command()
async def chifoumi(ctx, choix: str):
    choix_possibles = ["pierre", "feuille", "ciseaux"]
    choix_bot = random.choice(choix_possibles)

    if choix.lower() not in choix_possibles:
        await ctx.send("Choix invalide. Veuillez choisir entre pierre, feuille ou ciseaux.")
        return

    resultat = determiner_gagnant(choix.lower(), choix_bot)

    await ctx.send(f'Tu as choisi {choix.lower()}\nJ\'ai choisi {choix_bot}\nRésultat : {resultat}')

def determiner_gagnant(choix_joueur, choix_bot):
    if choix_joueur == choix_bot:
        return "C'est une égalité !"
    elif (
        (choix_joueur == "pierre" and choix_bot == "ciseaux") or
        (choix_joueur == "feuille" and choix_bot == "pierre") or
        (choix_joueur == "ciseaux" and choix_bot == "feuille")
    ):
        return "Ouais mais t'as triché aussi..."
    else:
        return "T'es NUL j'ai gagné !"

bot.run('MTE3OTcwMjU1NTA1NjU0MTczNw.GAQVtg.I9f3kHG4Zm-BOFD7JgIV-bX1DUAABeivr_J5YY') #Exécution du programme grace au token unique du bot