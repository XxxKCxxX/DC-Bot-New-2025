import discord
import json
from discord.ext import commands
from discord import app_commands
import requests

with open('config.json') as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="/", intents=intents)



@app_commands.command(name="ip", description="Get IP")
async def get_ip(interaction: discord.Interaction):
    if interaction.channel_id != 1168538940580561026:
        await interaction.response.send_message("Dieser Command ist in diesem Channel nicht erlaubt.", ephemeral=True)
        return

    try:
        response = requests.get("https://myipv4.p1.opendns.com/get_my_ip")
        response.raise_for_status()  
        data = response.json() 

        ip = data.get("ip", "Unbekannt") #Standartwert "Unbekannt" falls kein IP gefunden wird
        await interaction.response.send_message(f"Server-IP:\n```\n{ip}\n```")
    except Exception as e:
        await interaction.response.send_message(f"Fehler beim Abrufen der IP-Adresse: {e}", ephemeral=True)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} ist online!')
    if config["sync"]:
        try:
            synced = await bot.tree.sync()
            print(f"Slash-Commands synchronisiert: {len(synced)}")
            pass
        except Exception as e:
            print(f"Fehler beim Synchronisieren der Slash-Commands: {e}")

bot.tree.add_command(get_ip)


bot.run(config["token"])
