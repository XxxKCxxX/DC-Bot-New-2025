import discord
import json
import mysql.connector
from discord.ext import commands

# Lade die Konfigurationsdatei
with open('config.json') as f:
    config = json.load(f)




# Initialisiere den Bot
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Event, wenn der Bot bereit ist
@bot.event
async def on_ready():
    print(f'Bot {bot.user} ist online!')

# Event, wenn eine Nachricht gesendet wird
@bot.event
async def on_message(message):
    if message.channel.id == int(config['channel_id']):     
        print(f"Nachricht empfangen!")



# Starte den Bot
bot.run(config["token"])
