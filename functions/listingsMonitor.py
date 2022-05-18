import requests, json, telegram, time
from config import *
from telegram.ext import Updater

class Item:
    name: str
    tokenID: str
    price: str
    price_usd: str
    url: str
    currency: str

    def __init__(self, name, tokenID, price, price_usd, url, currency):
        self.name = name
        self.tokenID = tokenID
        self.price = price
        self.price_usd = price_usd
        self.url = url
        self.currency = currency
    
    def __hash__(self):
        return self.tokenID.__hash__()
        
    def __eq__(self, other):
        return self.tokenID == other.tokenID

    def __str__(self):
        string = ''
        if(self.name != None):
            string += f'Name: {self.name}\n'
        string += f'\nToken ID: {self.tokenID}'
        return string

    def __repr__(self):
        return self.__str__()
    
    def getPrice(self):
        return self.price
    
    def getPriceUSD(self):
        return self.price_usd
    
    def getCurrency(self):
        return self.currency
    
    def getTokenID(self):
        return int(self.tokenID)



def get_items():
    items = []
    url = "https://api.opensea.io/api/v1/events"
    querystring = {"asset_contract_address":f"{COLLECTION_ADDRESS}","event_type":"created","only_opensea":"false","offset":"0","limit":"20"}
    headers = {
        "X-API-KEY": APIKEY,
        "Accept": "application/json"
    }    
    response = requests.request("GET", url, headers=headers, params=querystring)
    response = json.loads(response.text)

    for i in range(0, 11):
        try:
            asset = response['asset_events'][i]['asset']
            price = float(response['asset_events'][i]['ending_price'])/(10**int(response['asset_events'][i]['payment_token']['decimals']))
            tmpItem = Item(asset['name'], asset['token_id'], str(price), str(price*float(response['asset_events'][i]['payment_token']['usd_price'])), asset['permalink'], response['asset_events'][i]['payment_token']['symbol'])
            items.append(tmpItem)
        except:
            continue
    return items[:10]

def listingsMonitor(nfts):
    print('Starting...')
    items_already_sent = []
    updater = Updater(token=TOKENBOT, use_context=True)
    dispatcher = updater.dispatcher
    items = get_items()
    print('Started!\n\nMonitoring...')
    while True:
        try:
            if len(items_already_sent) > 5:
                items_already_sent = []
            temp_items = get_items()
            new_items = list(set(temp_items)-set(items))
            if new_items:
                for item in new_items:
                    if item not in items_already_sent:
                        for nft in nfts:
                            if item.getTokenID() == nft.getTokenID():
                                nft.setPrice(item.getPrice())
                                nft.setPriceUSD(item.getPriceUSD())
                                nft.setCurrency(item.getCurrency())
                                if float(item.getPrice()) <= float(MAX_PRICE):
                                    print(f'Price: {float(item.getPrice())}\tMAX_PRICE: {float(MAX_PRICE)}\tTokenID: {item.getTokenID()} Yes')
                                    string = f'<a href="{nft.getImage()}">&#8205;</a>{nft.__str__()}'
                                    updater.bot.send_message(chat_id='-1001178234728', text=string, parse_mode=telegram.ParseMode.HTML)
                                    items_already_sent.append(item)
                                else:
                                    print(f'Price: {float(item.getPrice())}\tMAX_PRICE: {float(MAX_PRICE)}\tTokenID: {item.getTokenID()} No')
                                    items_already_sent.append(item)
                items = get_items()
                new_items = []
            time.sleep(5)
        except Exception as e:
            print(e)
            continue

if __name__ == '__main__':
    print('The script must be launched from main file!')
