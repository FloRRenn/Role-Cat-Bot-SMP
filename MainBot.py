import discord, os
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='smp.', intents = intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.playing, name = "server: minexyzvn.tk"))
    
    bot.load_extension('cogs.BotEvent')
    bot.load_extension('cogs.CommandsGuild')
    bot.load_extension('cogs.AdminCommands')
    bot.load_extension('cogs.Runtime')
    
    print(f'{bot.user.name} đã trổi dậy!!!')

TOKEN = os.environ.get('TOKEN')
bot.run(TOKEN)