import asyncio
from sys import platform
import discord
import json
from discord.ext import commands
from discord import app_commands
import discord.ui
import requests
import subprocess
import yt_dlp


with open('config.json') as f:
    config = json.load(f)

with open('token.json') as f:
    token = json.load(f)

if platform == "win32":
    FFMPEG_EXE = "ffmpeg.exe" # Liegt in deinem Projektordner
else:
    FFMPEG_EXE = "ffmpeg"

YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': True}
FFMPEG_OPTIONS = {'options': '-vn'}
song_queue: list[dict] = []

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="/", intents=intents)

role_options: list[discord.SelectOption] = [discord.SelectOption(label="placeholder", value="placeholder")]
#Hier nur IDs - später conversion in on_ready
channel_mc: discord.TextChannel = config["ch_mc_id"]
cat_games: discord.CategoryChannel = config["cat_games_id"]
channel_ids: list[discord.TextChannel] = config["ch_ip_ids"]
channel_music: discord.TextChannel = config["ch_music_id"]
kaze_id = config["us_Kaze_id"]
current_song: dict = None
bool_loop = False

@app_commands.command(name="plugins", description="Zeigt alle Minecraft Plugins an")  
async def get_plugins(interaction: discord.Interaction, server: str = "ServerOkt2025"):
    global channel_mc
   
    
    if interaction.channel_id != channel_mc.id:
        await interaction.response.send_message("Dieser Command ist nur in <"+str(channel_mc)+"> nicht erlaubt.", ephemeral=True, delete_after=5)
        return
    
    try:
        result = subprocess.run(["ls", "-1"], capture_output=True, text=True, cwd="/home/pi/"+server+"/plugins/", check=True, delete_after=5)
        plugins = result.stdout.splitlines()
        plugins_list = "\n".join(plugins) if plugins else "Keine Plugins gefunden."
        await interaction.response.send_message(f"Plugins: \n```{plugins_list}```", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"{Kaze.mention} - Fehler beim Abrufen der Plugins: \n```{e}```", ephemeral=False, delete_after=5)


@app_commands.command(name="ip", description="Zeigt die IP des Servers an")
async def get_ip(interaction: discord.Interaction):
    if interaction.channel.id not in channel_ids:
        await interaction.response.send_message(f"Dieser Command ist nur in den Kanälen {', '.join([f'<#{cid}>' for cid in channel_ids])} erlaubt.", ephemeral=True, delete_after=5)
        return

    try:
        response = requests.get("https://api4.my-ip.io/v2/ip.json")
        response.raise_for_status()  
        data = response.json() 

        ip = data.get("ip", "Unbekannt") #Standartwert "Unbekannt" falls kein IP gefunden wird
        await interaction.response.send_message(f"Server IP:\n```\n{ip}\n```", ephemeral=True)
    except Exception as e:
         
        await interaction.response.send_message(f"Fehler beim Abrufen der IP-Adresse: {e}", ephemeral=False, delete_after=5)



@app_commands.command(name="restart", description="Startet den Bot neu")
async def restart(interaction: discord.Interaction):
    await interaction.response.send_message("Starte den Bot neu...", ephemeral=True)
    await Kaze.send("Bot wird neu gestartet von " + interaction.user.mention)
    await bot.close()  

@app_commands.command(name="loop", description="Schleife die aktuelle Warteschlange")
async def loop(interaction: discord.Interaction):
    global bool_loop
    bool_loop = not bool_loop
    if bool_loop:
        await interaction.response.send_message("Die Warteschlange wird nun in einer Schleife abgespielt!", ephemeral=True, delete_after=5)
    else:
        await interaction.response.send_message("Die Warteschlange wird nun nicht mehr in einer Schleife abgespielt!", ephemeral=True, delete_after=5)



@app_commands.command(name="join", description="Joint deinem Voice Channel")
async def join(interaction: discord.Interaction):

    await interaction.response.send_message("Joining...", ephemeral=True, delete_after=3)
    await connect(interaction)
   


@app_commands.command(name="leave", description="Verlässt den Voice Channel")
async def leave(interaction: discord.Interaction):
    await interaction.response.send_message("Leaving...", ephemeral=True, delete_after=3)
    if interaction.guild.voice_client and interaction.user.voice and interaction.user.voice.channel and interaction.guild.voice_client.channel == interaction.user.voice.channel:
        await interaction.guild.voice_client.disconnect()
    else:
        await interaction.response.edit_message("Du musst in einem Voice Channel sein, um den Bot zu verlassen!", ephemeral=True, delete_after=5)

@app_commands.command(name="play", description="Skippt die queue / Link oder Suche")
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer()

    await connect(interaction)
    information = get_info(query, interaction.user)
    oldq = song_queue.copy()
    song_queue.clear()
    song_queue.append(information)
    song_queue.extend(oldq) 

    
    interaction.guild.voice_client.resume()
    if not interaction.guild.voice_client.is_playing():
        await asyncio.sleep(0.5)
        play_next(interaction) 
        await asyncio.sleep(0.5)
    else:
        await asyncio.sleep(0.5)
        interaction.guild.voice_client.stop()
        await asyncio.sleep(0.5)
    
    if "http" in information['query']:
        link = information['query'] 
    else:
        link = information['url'] 
    await interaction.followup.send(f"Spiele [{information['title']}]({link}) ab!", ephemeral=False)
    

@app_commands.command(name="pause", description="Pausiert / Resumed die aktuelle Musik")
async def pause(interaction: discord.Interaction):
    await interaction.response.send_message(":thumbsup::skin-tone-3:", ephemeral=True, delete_after=1)
    if interaction.guild.voice_client is None: return
    if interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.pause()
    else:
        interaction.guild.voice_client.resume()

@app_commands.command(name="queue", description="Fügt ein Lied zur Warteschlange hinzu / Link oder Suche")
async def queue(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    information = get_info(query, interaction.user)
    await connect(interaction)
    
    if len(song_queue) > config["max_queue_length"]:
        await interaction.followup.send(f"Die Warteschlange ist voll! Maximal {config['max_queue_length']} Lieder erlaubt.", ephemeral=True)
        return
    song_queue.append(information)
    if "http" in information['query']:
        link = information['query'] 
    else:
        link = information['url'] 
    await interaction.followup.send(f"Das Lied [{information['title']}]({link}) wurde zur Warteschlange hinzugefügt!", ephemeral=False)

@app_commands.command(name="skip", description="Überspringt das aktuelle Lied")
async def skip(interaction: discord.Interaction):
    await interaction.response.defer()
    if interaction.guild.voice_client is None: return
    await interaction.followup.send(f"Lied {current_song['title']} wird von {interaction.user.mention} übersprungen!", ephemeral=False)
    interaction.guild.voice_client.stop()
    await asyncio.sleep(0.5)

@app_commands.command(name="info", description="Zeigt Informationen über das aktuelle Lied an")
async def info(interaction: discord.Interaction):
    await interaction.response.defer()

    
    if current_song == None: 
        await interaction.followup.send("Es wird gerade kein Lied abgespielt!", ephemeral=True)
        return
    if "http" in current_song['query']:
        link = current_song['query'] 
    else:
        link = current_song['url'] 

    await interaction.followup.send(f"Das Lied [{current_song['title']}]({link}) wurde von {current_song['user'].mention} unter {current_song['query']} gefunden!")



@app_commands.command(name="warteschlange", description="Zeigt die aktuelle Warteschlange an")
async def warteschlange(interaction: discord.Interaction):
    if len(song_queue) == 0:
        await interaction.response.send_message("Die Warteschlange ist leer!", ephemeral=True, delete_after=5)
        return
    
    queue_list = "\n".join([f"{idx+1}. {song['title']}" for idx, song in enumerate(song_queue)])
    await interaction.response.send_message(f"Aktuelle Warteschlange:\n```\n{queue_list}\n```", ephemeral=False, delete_after=30)


async def connect(interaction):
    if interaction.guild.voice_client is None: 
        await interaction.user.voice.channel.connect()
        return
    if interaction.guild.voice_client.is_connected():
        if interaction.user.voice and interaction.user.voice.channel:
            channel = interaction.user.voice.channel
            if channel != interaction.user.voice.channel:
                await channel.connect()


def play_next(interaction):
    global current_song, song_queue
    vc: discord.VoiceClient = interaction.guild.voice_client
    if bool_loop and current_song is not None:
        source = discord.FFmpegPCMAudio(current_song['url'], executable=FFMPEG_EXE, **FFMPEG_OPTIONS)
        vc.play(source, after=lambda e: play_next(interaction))
        return
    if vc and len(song_queue) > 0:
        song = song_queue.pop(0) # Nimm das erste Lied aus der Liste
        current_song = song.copy()
        source = discord.FFmpegPCMAudio(song['url'], executable=FFMPEG_EXE, **FFMPEG_OPTIONS)

        vc.play(source, after=lambda e: play_next(interaction))
    else:
        current_song = None

def get_info(url, user):
    if "http" not in url:
        #Wenn es kein Link ist, sondern eine Suche, dann suche nach dem ersten Ergebnis mit url als query
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            information = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]

    
    else: 
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            information = ydl.extract_info(url, download=False)

    information["query"] = url
    information["user"] = user
    return information










class RoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.select(placeholder="Rolle auswählen", min_values=1, max_values=len(role_options), options=role_options, custom_id="role_select")
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "Alle Spiele hinzufügen":
            #ALLE rollen die die anderen role options sind hinzufügen
                for option in role_options:
                    if option.value != "Alle Spiele":
                        role = discord.utils.get(interaction.guild.roles, name=option.value)
                        if role and role not in interaction.user.roles:
                            await interaction.user.add_roles(role)
                await interaction.response.send_message("Alle Spiel Rollen hinzugefügt.", ephemeral=True, delete_after=5)
                return
        if select.values[0] == "Alle Spiele entfernen":
            #ALLE rollen die die anderen role options sind entfernen
                for option in role_options:
                    if option.value != "Alle Spiele":
                        role = discord.utils.get(interaction.guild.roles, name=option.value)
                        if role and role in interaction.user.roles:
                            await interaction.user.remove_roles(role)
                await interaction.response.send_message("Alle Spiel Rollen entfernt.", ephemeral=True, delete_after=5)
                return

        selected_role = discord.utils.get(interaction.guild.roles, name=select.values[0])

        if selected_role in interaction.user.roles:
            print(f"Rolle {selected_role.name} für {interaction.user.name} entfernen")
            await interaction.user.remove_roles(selected_role)
            await interaction.response.send_message(f"Rolle {selected_role.name} entfernt.", ephemeral=True, delete_after=5)
        else:
            print(f"Rolle {selected_role.name} für {interaction.user.name} hinzufügen")
            await interaction.user.add_roles(selected_role)
            await interaction.response.send_message(f"Rolle {selected_role.name} hinzugefügt.", ephemeral=True, delete_after=5)


@bot.event
async def on_ready():
    global Kaze, channel_mc, cat_games, channel_music
    print(f'Bot {bot.user} ist online!')
    Kaze = await bot.guilds[0].fetch_member(kaze_id)

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
        channel_music = bot.guilds[0].get_channel(channel_music)
        await Kaze.send("Bot ist online!")
    except Exception as e:
        print(f"Fehler beim Abrufen der Kanäle: {e}")
        await Kaze.send("Fehler beim Abrufen der Kanäle: " + str(e))
    
    for vc in bot.voice_clients:
        await vc.disconnect(force=True)

    if config["setup"]:
        category_games = bot.guilds[0].get_channel(config["cat_games_id"])
        role_options.clear()
        role_options.append(discord.SelectOption(label="Alle Spiele hinzufügen", value="Alle Spiele hinzufügen"))
        role_options.append(discord.SelectOption(label="Alle Spiele entfernen", value="Alle Spiele entfernen"))
        for channel in category_games.channels:
            if channel.id == config["ch_games-roles_id"]:
                continue
            role_options.append(discord.SelectOption(label=channel.name, value=str(channel.topic)))
        ch_gamesroles = category_games.channels[0]
        if ch_gamesroles != None: await ch_gamesroles.purge()
        if ch_gamesroles != None: await ch_gamesroles.send("Wähle Game Rollen ab oder an, um den jeweiligen Channel zu sehen", view=RoleView())
    else:
        bot.add_view(RoleView())

bot.tree.add_command(get_ip)
bot.tree.add_command(get_plugins)
bot.tree.add_command(join)
bot.tree.add_command(leave)
bot.tree.add_command(play)
bot.tree.add_command(pause)
bot.tree.add_command(queue)
bot.tree.add_command(skip)
bot.tree.add_command(warteschlange)
bot.tree.add_command(restart)
bot.tree.add_command(info)
bot.tree.add_command(loop)

bot.run(token["token"])
