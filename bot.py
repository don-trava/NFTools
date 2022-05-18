import logging
import os
import threading
from logging.handlers import TimedRotatingFileHandler

from config import *
from functions import (listingsMonitor, metadataScraper, monitorTokenURI,
                       nftsMonitor, objects, rarityTool, traitsSelector)

Title='''
         NFTs Scraper
--------------------------------
Starting
--------------------------------
'''

Menu='''
    1) Get collection NFTS (1st function)
    2) Select traits and monitor NFTs (2nd and 3rd function)
    3) Get collection, select traits and monitor (1st, 2nd and 3rd function)
    4) Select traits and monitor listing page
    5) Rarity Tool (4th function)
    6) Proxy List Print
    7) Execute first, second and third function when tokenURI change
    
    8) Monitor NFTs in background (3rd function)
    9) Stop background monitoring (Stop monitoring before exit program!)

    0) Exit
'''    

if __name__ == '__main__':

    '''
    Si posiziona nella directory corrente a partire 
    dalla posizione del file config.py sia su windows che su linux
    '''
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    
    #Log file configuration
    logger = logging.getLogger('NFT_Scraper_log')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d-%y %H:%M:%S')
    fh = TimedRotatingFileHandler(NFTLOG, when='midnight', interval=5)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


    #Title printing
    print(Title)
    
    while True:
        #Menu printing
        print(Menu) 
        
        f = int(input(f'\nSelect the function: '))
        if(f == 1): metadataScraper.metadataScraper(logger)
        elif(f == 2):
            #Select the NFTs to monitor
            nftsToMonitor = traitsSelector.traitsSelector()
            #Write the TokenIDs of the NFTs to monitor on file
            with open(f'metadata/{COLLECTION_NAME}/{COLLECTION_NAME}_toMonitor.txt', 'w') as file:
                for nft in nftsToMonitor:
                    file.write(f'{nft.getTokenID()}\n')
            #Start the monitoring of the previous selected tokenIDs
            print(len(nftsToMonitor))
            nftsMonitor.nftsMonitor(nftsToMonitor, logger)
        elif(f == 3):
            #Execute automatically the first, second and third functions
            metadataScraper.metadataScraper(logger)
            nftsToMonitor = traitsSelector.traitsSelector()
            with open(f'metadata/{COLLECTION_NAME}/{COLLECTION_NAME}_toMonitor.txt', 'w') as f:
                for nft in nftsToMonitor:
                    f.write(f'{nft.getTokenID()}\n')
            nftsMonitor.nftsMonitor(nftsToMonitor, logger)
        elif(f == 4):
            #Select the NFTs to monitor
            nftsToMonitor = traitsSelector.traitsSelector()
            #Start monitoring the listing page of collection for previous selected NFTs
            listingsMonitor.listingsMonitor(nftsToMonitor)
        elif(f == 5):
            #Get the collection
            collection = objects.createCollection()
            #Calculate rarity of collection
            rarityTool.calculate_rarity(collection, logger)
        elif(f == 6):
            if USE_PROXIES:
                print(PROXIES)
            else:
                print('You have to set USE_PROXIES to True before.')
        elif(f == 7):
            changed, newMasterLink = monitorTokenURI.monitorTokenURI()
            if(changed):
                with open('config.py', 'r') as f:
                    text = f.read()    
                lines = [line if 'MASTER_LINK' not in line else f'MASTER_LINK = "{newMasterLink}"' for line in text.splitlines()]
                string = ''.join([str(line)+'\n' for line in lines])
                with open('config.py', 'w') as f:
                    f.write(string)
                metadataScraper.metadataScraper(logger)
                nftsToMonitor = traitsSelector.traitsSelector()
                with open(f'metadata/{COLLECTION_NAME}/{COLLECTION_NAME}_toMonitor.txt', 'w') as f:
                    for nft in nftsToMonitor:
                        f.write(f'{nft.getTokenID()}\n')
                nftsMonitor.nftsMonitor(nftsToMonitor, logger)
        elif(f == 8):
            #Select the NFTs to monitor
            nftsToMonitor = traitsSelector.traitsSelector()
            #Write the TokenIDs of the NFTs to monitor on file
            with open(f'metadata/{COLLECTION_NAME}/{COLLECTION_NAME}_toMonitor.txt', 'w') as file:
                for nft in nftsToMonitor:
                    file.write(f'{nft.getTokenID()}\n')
            #Start the monitoring of the previous selected tokenIDs
            t = threading.Thread(target=nftsMonitor.nftsMonitor, args=(nftsToMonitor, logger))
            t.daemon = True
            t.start()
        elif(f == 9):
            try:
                with(open('metadata/tmpProcessesPID.txt', 'r')) as f:
                    for line in f.readlines():
                        if(line != '\n'): os.kill(int(line), 9)
                os.remove('metadata/tmpProcessesPID.txt')
            except FileNotFoundError as e:
                print('Impossible to kill background monitoring processes!')
                logger.error(msg=e)
            except Exception as e:
                logger.error(msg=e)
        elif(f == 0):
            exit()



