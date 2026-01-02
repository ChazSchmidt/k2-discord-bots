from .aerodrome_price import AerodromePrice
from .utils import load_abi
from .constants import USDC_DECIMALS, WETH_USDC_AERODROME_POOL, USDC_ADDRESS, WETH_ADDRESS, KVCM_USDC_AERODROME_POOL, KVCM_K2_AERODROME_POOL, KVCM_ADDRESS, KVCM_DECIMALS

uni_v2_abi = load_abi('uni_v2_pool.json')
uni_v3_abi = load_abi('uni_v3_pool.json')


def uni_v2_pool_price(web3, pool_address, decimals, base_price=1):
    '''
    Calculate the price of a SushiSwap liquidity pool, using the provided
    pool address, decimals of the first token, and multiplied by
    base_price if provided for computing multiple pool hops.
    '''
    pool_contract = web3.eth.contract(
        address=pool_address,
        abi=uni_v2_abi
    )

    try:
        reserves = pool_contract.functions.getReserves().call()
        token_price = reserves[0] * base_price * 10**decimals / reserves[1]

        return token_price
    except Exception:
        return None


def uni_v3_pool_price(web3, pool_address, decimals0=18, decimals1=18, base_price=1):
    '''
    Calculate the price of a UniV3 liquidity pool, using the provided
    pool address, decimals of the first token, and multiplied by
    base_price if provided for computing multiple pool hops.
    '''
    pool_contract = web3.eth.contract(
        address=pool_address,
        abi=uni_v3_abi
    )

    try:
        # Get slot0 data
        slot0_data = pool_contract.functions.slot0().call()
        sqrt_price_x96 = slot0_data[0]

        # Calculate price from sqrtPriceX96
        # Price = (sqrtPriceX96 / 2^96) ^ 2
        price_1_0 = (sqrt_price_x96 / (2**96)) ** 2

        # Adjust for decimals
        token_price = price_1_0 * (10 ** decimals0) / (10 ** decimals1)

        return token_price * base_price

    except Exception as e:
        print(e)
        return None


def aero_weth_usdc_price():
    # Initialize with Base RPC URL
    aero_price = AerodromePrice()

    return aero_price.get_spot_price(
        USDC_ADDRESS,
        WETH_USDC_AERODROME_POOL,
        token_in_decimals=USDC_DECIMALS
    )

def kvcm_usdc_aerodrome_price(web3):
    aero_price = AerodromePrice()
    kvcm_per_usdc = aero_price.get_spot_price(
        USDC_ADDRESS,
        KVCM_USDC_AERODROME_POOL,
        token_in_decimals=USDC_DECIMALS
    )
    # Convert from "KVCM per USDC" to "USDC per KVCM"
    return 1 / kvcm_per_usdc if kvcm_per_usdc != 0 else 0

## k2/kvcm price requires using kvcm_usdc_aerodrome_price to calculate the price of K2
def kvcm_k2_aerodrome_price(web3):
    aero_price = AerodromePrice()
    kvcm_usdc_price = kvcm_usdc_aerodrome_price(web3)
    k2_kvcm_price = aero_price.get_spot_price(
        KVCM_ADDRESS,
        KVCM_K2_AERODROME_POOL,
        token_in_decimals=KVCM_DECIMALS
    )
    ## multiply k2_kvcm_price by kvcm_usdc_price to get the price of K2
    return k2_kvcm_price * kvcm_usdc_price

def token_supply(web3, token_address, abi, decimals=None):
    '''
    Compute the total supply of the specified ERC-20 token at `token_address` with `abi` and the correct `decimals`
    '''
    contract = web3.eth.contract(
        address=token_address,
        abi=abi
    )

    try:
        if decimals is None:
            decimals = contract.functions.decimals().call()
        total_supply = contract.functions.totalSupply().call() / 10**decimals
        return total_supply
    except Exception:
        return None


def balance_of(web3, token_address, abi, decimals, address_to_check):
    '''
    Compute the balance for specific `address_to_check`
    of the specified ERC-20 token at `token_address`
    with `abi` and the correct `decimals`
    '''
    contract = web3.eth.contract(
        address=token_address,
        abi=abi
    )

    try:
        balance = contract.functions.balanceOf(
            address_to_check).call() / 10**decimals
        return balance
    except Exception:
        return None
