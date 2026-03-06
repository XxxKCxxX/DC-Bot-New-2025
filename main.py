import discord
import json
from discord.ext import commands
from discord import app_commands
import requests
import subprocess

Kaze: discord.Member = None

channel_mc: discord.TextChannel = 1168538940580561026
cat_games: discord.CategoryChannel = 1205449776439500820

with open('config.json') as f:
    config = json.load(f)

with open('token.json') as f:
    token = json.load(f)

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="/", intents=intents)


@app_commands.command(name="plugins", description="Zeigt alle Minecraft Plugins an")  
async def get_plugins(interaction: discord.Interaction, server: str = "ServerOkt2025"):
    global channel_mc
   
    
    if interaction.channel_id != channel_mc.id:
        await interaction.response.send_message("Dieser Command ist nur in <"+str(channel_mc)+"> nicht erlaubt.", ephemeral=True)
        return
    
    try:
        result = subprocess.run(["ls", "-1"], capture_output=True, text=True, cwd="/home/pi/"+server+"/plugins/", check=True)
        plugins = result.stdout.splitlines()
        plugins_list = "\n".join(plugins) if plugins else "Keine Plugins gefunden."
        await interaction.response.send_message(f"Plugins: \n```{plugins_list}```", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"{Kaze.mention} - Fehler beim Abrufen der Plugins: \n```{e}```", ephemeral=False)

@app_commands.command(name="ip", description="Zeigt die IP des Servers an")
async def get_ip(interaction: discord.Interaction):
    if interaction.channel.category_id != cat_games:
        await interaction.response.send_message("Dieser Command ist in diesem Channel nicht erlaubt.", ephemeral=True)
        return

    try:
        response = requests.get("https://api4.my-ip.io/v2/ip.json")
        response.raise_for_status()  
        data = response.json() 

        ip = data.get("ip", "Unbekannt") #Standartwert "Unbekannt" falls kein IP gefunden wird
        await interaction.response.send_message(f"Server IP:\n```\n{ip}\n```", ephemeral=True)
    except Exception as e:
         
        await interaction.response.send_message(f"Fehler beim Abrufen der IP-Adresse: {e}", ephemeral=False)

@bot.event
async def on_ready():
    global Kaze, channel_mc, cat_games
    print(f'Bot {bot.user} ist online!')
    Kaze = await bot.guilds[0].fetch_member(493564038953828363)

    if config["sync"]:
        try:
            synced = await bot.tree.sync()
            print(f"Slash-Commands synchronisiert: {len(synced)}")
            pass
        except Exception as e:
            print(f"Fehler beim Synchronisieren der Slash-Commands: {e}")
    try:
        channel_mc = bot.guilds[0].get_channel(channel_mc)
        cat_games = bot.guilds[0].get_channel(cat_games)
        await Kaze.send("Bot ist online!")
    except Exception as e:
        print(f"Fehler beim Abrufen der Kanäle: {e}")
        await Kaze.send("Fehler beim Abrufen der Kanäle: " + str(e))

bot.tree.add_command(get_ip)
bot.tree.add_command(get_plugins)


bot.run(token["token"])
