import os

from discord.ext import tasks

from ..contract_info import kvcm_k2_aerodrome_price, token_supply
from ..constants import K2_ADDRESS, K2_DECIMALS
from ..utils import get_discord_client, \
    get_base_web3, load_abi, \
    prettify_number, update_nickname, update_presence

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN_K2_PRICE"]

# Initialized Discord client
client = get_discord_client()

# Initialize web3
web3 = get_base_web3()

k2_abi = load_abi('erc20_token.json')


def get_info():
    k2_price = kvcm_k2_aerodrome_price(web3)
    supply = token_supply(web3, K2_ADDRESS, k2_abi, K2_DECIMALS)

    return k2_price, supply


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=15)
async def update_info():
    price, supply = get_info()

    if price is not None and supply is not None:
        mcap = price*supply
        mcap_prettified = prettify_number(mcap)

        success = await update_nickname(client, f'K2 MCap: ${mcap_prettified}')
        if not success:
            return

        success = await update_presence(client, f'K2 Price: ${price:,.4f}')
        if not success:
            return


client.run(BOT_TOKEN)
