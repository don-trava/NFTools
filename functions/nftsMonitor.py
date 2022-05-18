import concurrent.futures
import json
import time
import requests
import telegram
from config import *
from telegram.ext import Updater

def ProcessMonitor(nfts, API_key, logger):
    logger.info(msg=f'Monitor Process started with PID: {os.getpid()}')
    with(open('metadata/tmpProcessesPID.txt', 'a')) as f:
        f.write(f'{os.getpid()}\n')
    while True:
        missing_messages = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for nft in nfts:
                future = executor.submit(check_nft, nft, API_key, logger)
                futures.append(future)
            missing_messages = [message.result() for message in futures if message.result() != None]
        if len(missing_messages) > 0:
            logger.info(msg=f'Check finished on process with PID: {os.getpid()}, sending remaning NFTs...')
            updater = Updater(token=TOKENBOT, use_context=True)
            dispatcher = updater.dispatcher
            while len(missing_messages) > 0:
                for mess in missing_messages:
                    try:
                        updater.bot.send_message(chat_id=CHAT_ID, text=mess, parse_mode=telegram.ParseMode.HTML)
                        missing_messages.remove(mess)
                    except:
                        time.sleep(1)
                        continue


def nftsMonitor(nfts, logger):
    if(os.path.exists('metadata/tmpProcessesPID.txt')):
        os.remove('metadata/tmpProcessesPID.txt')
    n = min(CPUCORE, len(nfts))
    nfts = [nfts[i::n] for i in range(CPUCORE)]
    apiKeys = [key for key in EXTRA_API_KEYS]
    apiKeys.append(APIKEY)
    process_per_key = CPUCORE//min(CPUCORE, len(apiKeys))
    apiKeys_formatted = []
    c = 0
    for i in range(CPUCORE):
        if(i%process_per_key == 0 and i != 0 and c < len(apiKeys)-1):
            c += 1
        apiKeys_formatted.append(apiKeys[c])
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for i in range(CPUCORE):
            executor.submit(ProcessMonitor, nfts[i], apiKeys_formatted[i], logger)


def check_nft_sale_status(nft, apiKey, logger):
    try:
        got_data = False
        for i in range(5):
            url =  f"https://api.opensea.io/api/v1/assets?token_ids={nft.getTokenID()}&asset_contract_address={COLLECTION_ADDRESS}&order_direction=desc&offset=0&limit=1"
            headers = {
                "X-API-KEY": apiKey,
                "Accept": "application/json"
            }
            # querystring = {"token_ids":f"{nft.getTokenID()}", "asset_contract_address":f"{COLLECTION_ADDRESS}", "order_direction":"desc", "offset":"0", "limit":"1"}
            # response = requests.request("GET", url, headers=headers, params=querystring, timeout=30)
            response = requests.request("GET", url, headers=headers, timeout=30)
            if response.status_code != 429:
                got_data = True
                break
            else:                
                time.sleep(5)
                continue
    except Exception as e:
        logger.error(msg=e)
    if got_data:
        
        response = json.loads(response.text)
        try:
            asset = response['assets'][0]
            try:
                buyable = asset['sell_orders'][0]['side']
                if buyable == 1:
                    return True, asset
            except:
                return False, asset
        except:
            return False, None
    else:
        check_nft_sale_status(nft, apiKey, logger)
    
def check_nft(nft, apiKey, logger):
    try:
        # print(f'>>')
        buyable, asset = check_nft_sale_status(nft, apiKey, logger)
        if buyable:
            if len(asset['sell_orders']) != 0:
                current_price = float(asset['sell_orders'][0]['current_price'])/(10**int(asset['sell_orders'][0]['payment_token_contract']['decimals']))
                currency = asset['sell_orders'][0]['payment_token_contract']['symbol']
                current_price_usd = current_price*float(asset['sell_orders'][0]['payment_token_contract']['usd_price'])
                nft.setPrice(current_price)
                nft.setPriceUSD(current_price_usd)
                nft.setCurrency(currency)  
                if float(current_price) < float(MAX_PRICE):
                    updater = Updater(token=TOKENBOT, use_context=True)
                    dispatcher = updater.dispatcher
                    link = asset['permalink']
                    # print(f'\n\nFound {nft.getTokenID()}!\t{current_price: .4f} {currency}\t{current_price_usd: .2f} $\n\t-->Link: {link}')
                    string = f'<a href="{nft.getImage()}">&#8205;</a>{nft.__str__()}'
                    try:
                        updater.bot.send_message(chat_id=CHAT_ID, text=string, parse_mode=telegram.ParseMode.HTML)
                    except:
                        return string
    except Exception as e:
        if str(e) != 'object of type \'NoneType\' has no len()':
            logger.error(msg=e)
        pass

if __name__ == '__main__':
    print('Monitor must be launched from main script!')
