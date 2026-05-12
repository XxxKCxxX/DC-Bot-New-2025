import discord
import json
from discord.ext import commands
from discord import app_commands
import discord.ui
import requests
import subprocess


Kaze: discord.Member = None



with open('config.json') as f:
    config = json.load(f)

with open('token.json') as f:
    token = json.load(f)

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="/", intents=intents)

role_options: list[discord.SelectOption] = [discord.SelectOption(label="placeholder", value="placeholder")]
channel_mc: discord.TextChannel = config["ch_mc_id"]
cat_games: discord.CategoryChannel = config["cat_games_id"]
channel_ids: list[discord.TextChannel] = config["ch_ip_ids"]
kaze_id = config["us_Kaze_id"]

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
    if interaction.channel.id not in channel_ids:
        await interaction.response.send_message(f"Dieser Command ist nur in den Kanälen {', '.join([f'<#{cid}>' for cid in channel_ids])} erlaubt.", ephemeral=True)
        return

    try:
        response = requests.get("https://api4.my-ip.io/v2/ip.json")
        response.raise_for_status()  
        data = response.json() 

        ip = data.get("ip", "Unbekannt") #Standartwert "Unbekannt" falls kein IP gefunden wird
        await interaction.response.send_message(f"Server IP:\n```\n{ip}\n```", ephemeral=True)
    except Exception as e:
         
        await interaction.response.send_message(f"Fehler beim Abrufen der IP-Adresse: {e}", ephemeral=False)


class RoleView(discord.ui.View):
    def __init__(self):
        super().__init__()


    @discord.ui.select(placeholder="Rolle auswählen", min_values=1, max_values=len(role_options), options=role_options)
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "Alle Spiele hinzufügen":
            #ALLE rollen die die anderen role options sind hinzufügen
                for option in role_options:
                    if option.value != "Alle Spiele":
                        role = discord.utils.get(interaction.guild.roles, name=option.value)
                        if role and role not in interaction.user.roles:
                            await interaction.user.add_roles(role)
                await interaction.response.send_message("Alle Spiel Rollen hinzugefügt.", ephemeral=True)
                return
        if select.values[0] == "Alle Spiele entfernen":
            #ALLE rollen die die anderen role options sind entfernen
                for option in role_options:
                    if option.value != "Alle Spiele":
                        role = discord.utils.get(interaction.guild.roles, name=option.value)
                        if role and role in interaction.user.roles:
                            await interaction.user.remove_roles(role)
                await interaction.response.send_message("Alle Spiel Rollen entfernt.", ephemeral=True)
                return

        selected_role = discord.utils.get(interaction.guild.roles, name=select.values[0])

        if selected_role in interaction.user.roles:
            print(f"Rolle {selected_role.name} für {interaction.user.name} entfernen")
            await interaction.user.remove_roles(selected_role)
            await interaction.response.send_message(f"Rolle {selected_role.name} entfernt.", ephemeral=True)
        else:
            print(f"Rolle {selected_role.name} für {interaction.user.name} hinzufügen")
            await interaction.user.add_roles(selected_role)
            await interaction.response.send_message(f"Rolle {selected_role.name} hinzugefügt.", ephemeral=True)


@bot.event
async def on_ready():
    global Kaze, channel_mc, cat_games
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
        await Kaze.send("Bot ist online!")
    except Exception as e:
        print(f"Fehler beim Abrufen der Kanäle: {e}")
        await Kaze.send("Fehler beim Abrufen der Kanäle: " + str(e))
    
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

bot.tree.add_command(get_ip)
bot.tree.add_command(get_plugins)


bot.run(token["token"])
