import os

from discord.ext import tasks

from ..contract_info import kvcm_usdc_aerodrome_price, token_supply
from ..constants import KVCM_ADDRESS, KVCM_DECIMALS
from ..utils import get_discord_client, \
    get_base_web3, load_abi, \
    prettify_number, update_nickname, update_presence

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN_KVCM_PRICE"]

# Initialized Discord client
client = get_discord_client()

# Initialize web3
web3 = get_base_web3()

kvcm_abi = load_abi('erc20_token.json')


def get_info():
    kvcm_price = kvcm_usdc_aerodrome_price(web3)
    supply = token_supply(web3, KVCM_ADDRESS, kvcm_abi, KVCM_DECIMALS)

    return kvcm_price, supply


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

        success = await update_nickname(client, f'kVCM MCap: ${mcap_prettified}')
        if not success:
            return

        success = await update_presence(client, f'kVCM Price: ${price:,.4f}')
        if not success:
            return


client.run(BOT_TOKEN)
