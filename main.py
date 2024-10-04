import discord
from discord.ext import commands
import os
import asyncio
import random
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
import aiohttp

# Remplacer la récupération du token directement dans le code
TOKEN = os.environ.get("DISCORD_TOKEN")  # Assure-toi que ton token est défini dans les secrets

# Vérifier que le token est bien récupéré
if not TOKEN:
    raise ValueError("Le token Discord est introuvable.")

# Configurer les intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Flask pour garder le bot en vie
app = Flask('')

@app.route('/')
def home():
    print("Requête reçue : Bot est actif !")  # Log lorsque le serveur reçoit une requête
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

async def ping():
    while True:
        await asyncio.sleep(120)  # Pinger toutes les 1 minutes
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://2dd9b7af-8fee-4f2d-817e-ef80e8c49d6f-00-2roadzq2ihlt2.kirk.replit.dev/') as resp:
                    print(f"Pinger le bot: {resp.status}")
        except Exception as e:
            print(f"Erreur lors du ping: {e}")

# Liste de blagues
jokes = [
    "Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant ? Parce que sinon ils tombent dans le bateau !",
    "Pourquoi les fantômes sont-ils de si mauvais menteurs ? Parce qu'on peut lire à travers eux !",
    "Pourquoi les mathématiciens détestent-ils la forêt ? Parce qu'il y a trop de racines !",
]

# Liste d'insultes
insults = [
    "T'es marrant toi, retourne faire les trottoirs ! 😄",
    "Tu devrais vraiment réfléchir avant de parler, mon ami.",
    "On dirait que quelqu'un a besoin d'un peu de repos.",
]

# Questions de quiz
quiz_questions = {
    "Quel est le plus grand océan du monde ?": "pacifique",
    "Quelle est la capitale de la France ?": "paris",
    "Combien de continents y a-t-il ?": "sept",
}

# Suivi des messages pour détecter le spam
user_message_times = {}
user_warnings = {}

# Avertir pour spam
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f"Message reçu de {message.author}: {message.content}")  # Log des messages reçus

    # Gérer les réponses automatiques
    content = message.content.lower()

    # Répondre à "hey"
    if "hey" in content:
        await message.channel.send("Hey, Bien et toi mon poulet ?")

    # Répondre à "bien" de manière plus souple et variée
    if any(bien in content.split() for bien in ["bien", "ça va", "tout roule"]):
        responses = [
            "Cool ! Voici quelques trucs à savoir sur ce serveur...",
            "Content de l'entendre ! Si t'as des questions, n'hésite pas.",
            "Bien, merci ! Dis-moi, qu'est-ce qui t'amène ici ?",
        ]
        await message.channel.send(random.choice(responses))

    # Gérer les insultes
    insult_triggers = ["ferme la", "tais-toi", "stop", "dégage", "fils de pute", "gros lard", "tais toi", "degage", "fils dup", "connard"]
    if any(trigger in content for trigger in insult_triggers):
        await message.channel.send(random.choice(insults))

    # Calculer automatiquement les expressions mathématiques
    try:
        if any(op in content for op in ['+', '-', '*', '/']):
            result = eval(content)
            await message.channel.send(f"Résultat : {result}")
    except Exception as e:
        await message.channel.send(f"Erreur dans le calcul : {e}")

    # Vérifier les messages envoyés par l'utilisateur pour détecter le spam
    now = datetime.now()
    user_id = message.author.id

    if user_id not in user_warnings:
        user_warnings[user_id] = 0

    if user_id not in user_message_times:
        user_message_times[user_id] = []

    user_message_times[user_id].append(now)
    user_message_times[user_id] = [t for t in user_message_times[user_id] if t > now - timedelta(seconds=10)]

    if len(user_message_times[user_id]) > 5:
        user_warnings[user_id] += 1
        await message.channel.send(f"Attention {message.author.mention}, ce message semble être du spam. Avertissement #{user_warnings[user_id]}.")

        if user_warnings[user_id] >= 3:
            await message.channel.send(f"{message.author.mention}, tu es interdit d'écrire dans le salon pendant 10 secondes.")
            user_message_times[user_id] = []  # Réinitialiser le compteur de messages
            user_warnings[user_id] = 0  # Réinitialiser les avertissements
            await message.channel.set_permissions(message.author, send_messages=False)

            await asyncio.sleep(10)
            await message.channel.set_permissions(message.author, send_messages=True)

    await bot.process_commands(message)

# Commande pour afficher toutes les commandes disponibles
@bot.command(name='commands')
async def commands(ctx):
    commands_list = """
    Voici les commandes disponibles :
    !flip - Joue à Pile ou Face
    !quiz - Lance un quiz
    """
    await ctx.send(commands_list)

# Commande pour Pile ou Face
@bot.command(name='flip')
async def flip(ctx):
    result = random.choice(['Pile', 'Face'])
    await ctx.send(f"Résultat : {result}")

# Commande pour le quiz
@bot.command(name='quiz')
async def quiz(ctx):
    question, answer = random.choice(list(quiz_questions.items()))
    await ctx.send(question)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
        if msg.content.lower() == answer:
            await ctx.send("Correct ! 🎉")
        else:
            await ctx.send(f"Incorrect. La réponse était : {answer}.")
    except asyncio.TimeoutError:
        await ctx.send("Temps écoulé ! Réponds plus vite la prochaine fois.")

# Lancer le serveur Flask pour garder le bot en vie et le ping
keep_alive()  # Garde le bot en vie en lançant le serveur web
bot.loop.create_task(ping())  # Lancer le ping
bot.run(TOKEN)  # Lancer le bot avec le token sécurisé
