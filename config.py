import re
import os
import multiprocessing

os.chdir(os.path.abspath(os.path.dirname(__file__)))

#count cpu core
CPUCORE=multiprocessing.cpu_count()

#Master link
MASTER_LINK = "ipfs://bafybeic26wp7ck2bsjhjm5pcdigxqebnthqrmugsygxj5fov2r2qwhxyqu/[X]"

#Use proxies? Set to 'True' for use it and to 'False' for not
USE_PROXIES = False

#Private ipfs gateway for more requests per second
PRIVATE_GATEWAY = "example.cloud.com"

#Proxy file list
PROXY_FILE='proxy.txt'

#Load ProxyFileList
if USE_PROXIES:
    #Load/Update PROXIES variable
    with open(PROXY_FILE,'r')as proxy:
        PROXIES=re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+\b",proxy.read())
    proxiesDicts = [{"http":idx} for idx in PROXIES]

#NFT Log file
NFTLOG='NFTs_scraper.log'

#Set to True to further increase the speed
INCREASE_SPEED = True

#TokenBot for Telegram Bot
# ex. TOKENBOT = '1994001:AAGy5yw4-fovhlynHD7_JwJ8xk'
TOKENBOT = ''
#Chat ID for Telegram Bot
# ex. CHAT_ID = '-1001375432437'
CHAT_ID = ''

#Max price in ETH or WETH for NFT
MAX_PRICE = 2

ITEMS_TO_DISPLAY = 25

#Opensea API KEY
# ex. APIKEY = "75233n39e65f47h2b79554c11ba94"
APIKEY = ""

#For better performance you can add more opensea api keys
EXTRA_API_KEYS = ["2f6f419a083c46de9d83ce3dbe7db601", "99532c5ba0b24b21aaf646d94e22de02"]

#Collection address
# ex. COLLECTION_ADDRESS = ''
COLLECTION_ADDRESS = '0x219b8ab790decc32444a6600971c7c3718252539'

#Collection name
COLLECTION_NAME = 'AsYouPrefer'

#Number of collection items'
ITEMS = 8888
