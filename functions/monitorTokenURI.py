import json
import telegram
from web3 import Web3
from etherscan.contracts import Contract as CT
from telegram.ext import Updater

from config import *

def getTokenURI(address, api):
        abi = api.get_abi()
        abi = json.loads(abi)
        infura_url = 'https://mainnet.infura.io/v3/ceed0f4ad2024d15b7e935d42e55826e'
        web3 = Web3(Web3.HTTPProvider(infura_url))
        address2 = Web3.toChecksumAddress(address)
        contract = web3.eth.contract(address=address2, abi = abi)

        try:
            tokenURI = contract.functions.tokenURI(222).call()
        except:
            tokenURI = contract.functions.uri(222).call()

        try:
            tokenURI = tokenURI.replace('222', '[X]')
        except:
            print('There are problems with this contract, check the page on etherscan')
        
        return tokenURI

def monitorTokenURI():
    key = '3I7X8X4SS7IEYE85QUPUZTSYA6APJRXU7Y'

    address = f'{COLLECTION_ADDRESS}'
    api = CT(address=address, api_key=key)

    tokenURI = getTokenURI(address, api)
    print('\nMonitor started...')
    while True:

        tmpTokenURI = getTokenURI(address, api)

        if(tmpTokenURI != tokenURI):
            print(f'Previous tokenURI: {tokenURI}\nNew tokenURI: {tmpTokenURI}')
            tokenURI = tmpTokenURI
            updater = Updater(token=TOKENBOT, use_context=True)
            dispatcher = updater.dispatcher
            updater.bot.send_message(chat_id=CHAT_ID, text=f'Found new tokenURI for collection: {COLLECTION_NAME}\nNew tokenURI: {tokenURI}', parse_mode=telegram.ParseMode.HTML)
            return True, tokenURI

    
    