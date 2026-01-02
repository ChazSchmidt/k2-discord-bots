import os

import discord
from discord.ext import commands
import json
from web3 import Web3

# PROVIDER_BASE_URL = os.environ['WEB3_PROVIDER_BASE_URL']
PROVIDER_BASE_URL = 'https://mainnet.base.org'


def get_base_web3():
    web3_base = Web3(Web3.HTTPProvider(PROVIDER_BASE_URL))

    assert web3_base.is_connected()

    return web3_base


def get_discord_client(members_intent=False, presences_intent=False, message_content_intent=False):
    intents = discord.Intents.default()
    intents.members = members_intent
    intents.presences = presences_intent
    intents.message_content = message_content_intent

    client = commands.Bot(intents=intents, help_command=None, command_prefix='&?')

    return client


def load_abi(filename):
    '''Load a single ABI from the `abis` folder under `src`'''
    script_dir = os.path.dirname(__file__)
    abi_dir = os.path.join(script_dir, 'abis')

    with open(os.path.join(abi_dir, filename), 'r') as f:
        abi = json.loads(f.read())

    return abi


async def update_nickname(client, nickname_text):
    for guild in client.guilds:
        guser = guild.get_member(client.user.id)
        try:
            await guser.edit(nick=nickname_text)
        except discord.errors.HTTPException:
            return False

    return True


async def update_presence(client, text, type='watching'):
    if type == 'watching':
        type = discord.ActivityType.watching
    elif type == 'playing':
        type = discord.ActivityType.playing
    else:
        raise ValueError(
            'Invalid value for type passed to update_presence! '
            'Must be either "watching" or "playing"'
        )

    try:
        await client.change_presence(
            activity=discord.Activity(
                type=type,
                name=text
            )
        )
        return True
    except discord.errors.HTTPException:
        return False


def prettify_number(number):
    num = float('{:.3g}'.format(number))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])