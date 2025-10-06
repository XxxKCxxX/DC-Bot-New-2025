import discord
import json
from discord.ext import commands
from discord import app_commands
import requests
import subprocess

    

with open('config.json') as f:
    config = json.load(f)

with open('token.json') as f:
    token = json.load(f)

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="/", intents=intents)


@app_commands.command(name="plugins", description="Zeigt alle Plugins an")  
async def get_plugins(interaction: discord.Interaction):
    if interaction.channel_id != 1168538940580561026:
        await interaction.response.send_message("Dieser Command ist in diesem Channel nicht erlaubt.", ephemeral=True)
        return
    
    try:
        result = subprocess.run(["ls", "-1"], capture_output=True, text=True, cwd="/home/pi/ServerOkt2025/plugins/", check=True)
        plugins = result.stdout.splitlines()
        plugins_list = "\n".join(plugins) if plugins else "Keine Plugins gefunden."
        await interaction.response.send_message(f"Plugins: \n```{plugins_list}```", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Fehler beim Abrufen der Plugins: \n```{e}```", ephemeral=True)

@app_commands.command(name="ip", description="Zeigt die IP des Servers an")
async def get_ip(interaction: discord.Interaction):
    if interaction.channel_id != 1168538940580561026:
        await interaction.response.send_message("Dieser Command ist in diesem Channel nicht erlaubt.", ephemeral=True)
        return

    try:
        response = requests.get("https://myipv4.p1.opendns.com/get_my_ip")
        response.raise_for_status()  
        data = response.json() 

        ip = data.get("ip", "Unbekannt") #Standartwert "Unbekannt" falls kein IP gefunden wird
        await interaction.response.send_message(f"Server IP:\n```\n{ip}\n```", ephemeral=True)
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
bot.tree.add_command(get_plugins)


bot.run(token["token"])
