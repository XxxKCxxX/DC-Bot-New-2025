import discord
import json
import mysql.connector
from discord.ext import commands

# Lade die Konfigurationsdatei
with open('config.json') as f:
    config = json.load(f)

# Verbinde mit der MySQL-Datenbank
db = mysql.connector.connect(
    host=config["db_host"],
    user=config["db_user"],
    password=config["db_password"],
    database=config["db_name"]
)

cursor = db.cursor()

# Erstelle die Tabelle, wenn sie nicht existiert
cursor.execute("""
    CREATE TABLE IF NOT EXISTS message_counter (
        id INT AUTO_INCREMENT PRIMARY KEY,
        counter INT DEFAULT 0
    )
""")
db.commit()

# Initialisiere den Bot
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Event, wenn der Bot bereit ist
@bot.event
async def on_ready():
    print(f'Bot {bot.user} ist online!')
    channel = bot.get_channel(int(config['channel_id']))  # Channel abrufen
    print(f'Listening to messages in: {channel.name}')

# Event, wenn eine Nachricht gesendet wird
@bot.event
async def on_message(message):
    if message.channel.id == int(config['channel_id']):
        # Inkrementiere den Zähler in der Datenbank
        cursor.execute("SELECT counter FROM message_counter WHERE id = 1")
        result = cursor.fetchone()
        
        if result:
            new_counter = result[0] + 1
            cursor.execute("UPDATE message_counter SET counter = %s WHERE id = 1", (new_counter,))
        else:
            cursor.execute("INSERT INTO message_counter (counter) VALUES (1)")

        db.commit()
        print(f"Nachricht empfangen! Zähler: {new_counter}")

    # Wichtig: Wenn du on_message überschreibst, rufe `await bot.process_commands(message)` auf, damit Befehle noch verarbeitet werden
    await bot.process_commands(message)

# Starte den Bot
bot.run(config["token"])
