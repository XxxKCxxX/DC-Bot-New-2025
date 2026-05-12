import discord, json
with open('token.json') as f:
    config = json.load(f)

token = config["token"]

@bot.event
async def on_ready():
    print(f'Bot ist eingeloggt als {bot.user}')
bot = discord.Client(intents=discord.Intents.default())
bot.run(token)