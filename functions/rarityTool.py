import concurrent.futures
import os
import time
from itertools import repeat

import PySimpleGUI as sg
import requests
import telegram
from config import *
from PIL import Image, ImageTk
from telegram.ext import Updater

from functions import nftsMonitor


def calculate_rarity(collection, logger):
    try:
        rarity_scores = {}
        nfts = collection.getNFTs()
        logger.info(msg='Calculating rarity...')
        for nft in nfts:
            nft_rarity_score = 0
            for trait in nft.getAttributes():
                trait_rarity = (1/(trait.getPercentage()*0.01))
                nft_rarity_score += trait_rarity
            rarity_scores[nft] = nft_rarity_score
        
        rarity_scores = {k: v for k, v in sorted(rarity_scores.items(), reverse=True, key=lambda item: item[1])}
        
        most_rare_nfts = list(rarity_scores.keys())[:ITEMS_TO_DISPLAY]
        logger.info(msg='Starting GUI...')
        rarity_GUI(most_rare_nfts, collection, logger)
    except Exception as e:
        logger.error(msg=e)


def get_nfts_images(nfts, logger):
    print('\nChecking if there are images to get...')
    if not os.path.exists(f'metadata/{COLLECTION_NAME}/Images'):
        os.makedirs(f'metadata/{COLLECTION_NAME}/Images')
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(get_nft_image, nfts, repeat(logger))


def get_nft_image(nft, logger):
    if not os.path.exists(f'metadata/{COLLECTION_NAME}/Images/{nft.getTokenID()}.png'):
        url = nft.getImage()
        if ('http://' not in url) and ('https://' not in url):
            try:
                response = requests.get(f'http://{url}', stream=True)
            except:
                try:
                    response = requests.get(f'https://{url}', stream=True)
                except Exception as e:
                    logger.info(msg=e)
                    print(e)
        else:
            response = requests.get(url, stream=True)
        if response.status_code == 200:
            print('>>')
        else:
            print(f'Not worked! Status Code: {response.status_code} and url: {url}')
        response.raw.decode = True
        im = Image.open(response.raw)
        im.thumbnail((130,130))
        im.save(f'metadata/{COLLECTION_NAME}/Images/{nft.getTokenID()}.png')



def rarity_GUI(nfts, collection, logger):
    start = time.time()
    logger.info(msg='Getting images...')
    get_nfts_images(nfts, logger)
    logger.info(msg=f'Time Taken for scraping images: {time.time()-start} s')
    print(f'Time Taken: {time.time()-start} s')
    updater = Updater(token=TOKENBOT, use_context=True)
    dispatcher = updater.dispatcher

    # nfts_dict = {}
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     future_dict = {executor.submit(thirdFunction.checkIfInSale, nft, repeat(logger)): nft for nft in nfts}
    
    # dict = {(nft for nft in nfts):(k for k in future_dict.keys())}
    
    sg.theme('Black')
    sg.set_options(auto_size_buttons=True)
    layout_body = []
    columns = []
    print('Checking if there are elements on sale and building GUI...')
    logger.info(msg='Checking if there are elements on sale and building GUI...')

    for nft in nfts:
        if len(columns)%12 == 0:
            if len(columns) != 0:
                layout_body.append(columns)
                layout_body.append([sg.HorizontalSeparator()])         
            columns = []
        on_sale, asset = nftsMonitor.check_nft_sale_status(nft, logger)

        layout = [
            [sg.Text(f'#{nfts.index(nft)+1}', justification='left', text_color='Red', font=('Arial', 15, 'bold'))],
            [sg.Image(size=(150,150), key=f'-IMAGE-{nft.getTokenID()}', enable_events=True)],
            [sg.Text(f'#{nft.getTokenID()}', justification='right', font=('Arial', 15, 'bold'), key=f'-TEXT-{nft.getTokenID()}', enable_events=True)],
        ]
                    
        if on_sale:
            if len(asset['sell_orders']) != 0:
                layout[0].append(sg.Text(f'ON SALE', justification='right', text_color='Blue', font=('Arial', 10, 'bold')))
                current_price = float(asset['sell_orders'][0]['current_price'])/(10**int(asset['sell_orders'][0]['payment_token_contract']['decimals']))
                currency = asset['sell_orders'][0]['payment_token_contract']['symbol']
                current_price_usd = current_price*float(asset['sell_orders'][0]['payment_token_contract']['usd_price'])
                nft.setPrice(current_price)
                nft.setPriceUSD(current_price_usd)
                nft.setCurrency(currency) 

        columns.append(
            sg.Column(
                layout 
            )
        )
        columns.append(sg.VerticalSeparator())

    if len(columns) != 0:
        layout_body.append(columns)

    layout_head = [sg.Text('Rarity Tool', font=('Arial', 24, 'bold'))], [sg.Text('Showing:', font=('Arial', 14, 'bold')),sg.Button('ID', key='-CHANGETEXT-', enable_events=True)]
    
    if len(nfts) > 15: layout = [layout_head, [sg.Column(layout_body, scrollable=True, size=(980, 500), expand_x=True, vertical_scroll_only=True)]]
    else: layout = [layout_head, layout_body]
    
    print('\nDone!')

    window = sg.Window("Rarity Tool", layout, finalize=True)

    for nft in nfts:
        filename = f'metadata/{COLLECTION_NAME}/Images/{nft.getTokenID()}.png'
        im = Image.open(filename)
        image = ImageTk.PhotoImage(image=im)
        window[f'-IMAGE-{nft.getTokenID()}'].update(data=image)
    
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == '-CHANGETEXT-':
            if window['-CHANGETEXT-'].get_text() == 'Name':
                window['-CHANGETEXT-'].Update('ID')
                for nft in nfts:
                    window[f'-TEXT-{nft.getTokenID()}'].Update(f'#{nft.getTokenID()}')
            else:
                window['-CHANGETEXT-'].Update('Name')
                for nft in nfts:
                    if len(nft.getName()) > 5:
                        window[f'-TEXT-{nft.getTokenID()}'].Update(f'{nft.getName()}', font=('Arial', 10, 'bold'))
                    else:
                        window[f'-TEXT-{nft.getTokenID()}'].Update(f'{nft.getName()}')
        elif event.startswith('-IMAGE-'):
            tokenID = str(event[7:])
            updater.bot.send_message(chat_id=CHAT_ID, text=f'<a href="{collection.getNftByTokenID(int(tokenID)).getImage()}">&#8205;</a>{collection.getNftByTokenID(int(tokenID)).__str__()}', parse_mode=telegram.ParseMode.HTML)

        elif event.startswith('-TEXT-'):
            tokenID = str(event[6:])
            updater.bot.send_message(chat_id=CHAT_ID, text=f'<a href="{collection.getNftByTokenID(int(tokenID)).getImage()}">&#8205;</a>{collection.getNftByTokenID(int(tokenID)).__str__()}', parse_mode=telegram.ParseMode.HTML)


    window.close()
