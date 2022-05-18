from importlib import reload 
import config
from config import *
import time, requests, json, os, concurrent.futures

reload(config)


# Check if masterlink's gateway need to be changed to the private one
if 'gateway.pinata.cloud' in MASTER_LINK:
    M_LINK = MASTER_LINK.replace('gateway.pinata.cloud', PRIVATE_GATEWAY)
elif 'ipfs.io' in MASTER_LINK:
    M_LINK = MASTER_LINK.replace('ipfs.io', PRIVATE_GATEWAY)
elif 'ipfs:/' in MASTER_LINK:
    try:
        M_LINK = MASTER_LINK.replace('ipfs:/', f'https://{PRIVATE_GATEWAY}/ipfs')
    except:
        M_LINK = MASTER_LINK.replace('ipfs:/', f'https://{PRIVATE_GATEWAY}/ipfs/')
else:
    M_LINK = MASTER_LINK


def check_missing_files(start, stop):
    #Check if there're all NFTs' files trying to open them
    with concurrent.futures.ThreadPoolExecutor(max_workers=CPUCORE) as executor:
        futures = []
        for i in range(start, stop):
            future = executor.submit(check_file, i)
            futures.append(future)
    missing_links = [future.result() for future in futures]
    missing_links = [v for k, v in missing_links if not k]
    return missing_links

def check_file(n):
    try:
        filename = f'metadata/{COLLECTION_NAME}/'+str(n)+'.txt'
        f = open(filename, 'r')
    except:
        return (False, M_LINK.replace('[X]', str(n)))
    return (True, None)

def create_threads(urls, proxies):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        #If INCREASE_SPEED is set to true map all the urls of process
        if INCREASE_SPEED:
            executor.map(url_requester_single, urls)
        else:
            #Split the urls list in 2 list (integer division)
            url_index = len(urls)//2
            url_1, url_2 = urls[:url_index], urls[url_index:]
            if proxies != None:   #qui dovrebbe essere (if not USE_PROXIES) proxies da dove arriva? è PROXIES? (no)
                proxy_1, proxy_2 = proxies[0], proxies[1]
                executor.submit(urls_requester, url_1, proxy_1)
                executor.submit(urls_requester, url_2, proxy_2)
            else:
                executor.submit(urls_requester, url_1, None)
                executor.submit(urls_requester, url_2, None)


def create_processes(urls, logger):
    #Obtain the number of requests to execute per process, CPUCORE processes
    totUrls=len(urls)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        #For each process execute the function 'create_threads' and pass the urls to use
        for i in range(0, CPUCORE): #da 0 al numero di core CPU
            try:
                logger.info(msg='Opening process...'+str(i+1)+'/'+str(CPUCORE))
                print('->Opening process...'+str(((i+1)*totUrls)//CPUCORE))
                executor.submit(create_threads, urls[(i*totUrls)//CPUCORE:((i+1)*totUrls)//CPUCORE], None)
            except Exception as e:
                logger.info(msg=e)

def create_processes_proxy(urls, proxiesFormatted, requestsPerProxy, logger):
    start = 0
    #Execute the requests using 2 proxies per process, every process execute
    #  the requests for 2 proxies
    with concurrent.futures.ProcessPoolExecutor(max_workers=CPUCORE) as executor:
        for i in range(0, len(proxiesFormatted), 2):
            try:
                logger.info(msg='Opening process with proxy...')
                stop = start+(int(requestsPerProxy)*2)
                proxies = [proxiesFormatted[i], proxiesFormatted[i+1]]
                executor.submit(create_threads, urls[start:stop], proxies)
                start = stop
            except Exception as e:
                #print(e)
                logger.info(msg=e)
            time.sleep(0.1)
        #If the proxies number is not even, start a new process that execute
        #  the lasts requestsPerProxy but with local IP
        if(len(proxiesFormatted)%2 != 0):
            stop = start+int(requestsPerProxy)
            executor.submit(create_threads, urls[start:stop], None)
        #Check if there're remaning requests to execute
        missing_requests = len(urls)%len(proxiesFormatted)
        if(missing_requests != 0):
            executor.submit(create_threads, urls[-missing_requests:], None)


def get_tokenID_from_url(url):
    if '.json' in M_LINK:
        tokenID = url.replace(M_LINK.replace('[X].json', ''), '')
        tokenID = tokenID.replace('.json', '')
    else:
        tokenID = url.replace(M_LINK.replace('[X]', ''), '')
    return tokenID


def url_requester_single(url):
    #Bool parameter to check if NFT's been scraped
    done = False
    # get tokenID from url
    tokenID = get_tokenID_from_url(url)
    #Try max 20 times to get NFT's data
    for i in range(0, 20):
        #request
        response = requests.get(url=url, timeout=10)
        #If request worked and returned data
        if response.status_code == 200 and 'error' not in response.text:
            done = True
            print('>>')
            with  open(f'metadata/{COLLECTION_NAME}/'+tokenID+'.txt', 'w') as nft:
                nft.write(response.text)    
            break
        else:
            time.sleep(0.2)
            continue
    #If NFT requests not worked
    if not done:
        #Open a file named checkID.txt with TokenID as ID with all the info of the last request
        with  open(f'metadata/{COLLECTION_NAME}/check'+tokenID+'.txt', 'w') as nft_fail:
            nft_fail.write(f'Token ID: {tokenID}\nResponse code: {response.status_code}\nResponse: {response.text}')
        print(f'\t\tProblem with: {tokenID}')


def urls_requester(urls, proxy):
    idx=0
    for url in urls:
        #Bool parameter to check if a NFT is been scraped 
        done = False
        # get tokenID from url
        tokenID = get_tokenID_from_url(url)
        #Try max 20 times to get NFTs' data
        for i in range(0, 20):
            #Request
            if USE_PROXIES and proxy != None:
                #response = requests.get(url=url, proxies=proxy)
                response = requests.get(url=url, proxies=proxiesDicts[idx])
                idx=(idx+1)%len(PROXIES)
                #ogni volta che c'è un errore switch su un proxy diverso (mod len_proxy)
            else:
                #response = requests.get(url=url, proxies=proxy)
                response = requests.get(url=url)
            #If request worked and returned data
            if response.status_code == 200 and 'error' not in response.text:
                done = True
                if USE_PROXIES and proxy != None:
                    #print(f'Got token ID: {tokenID}\tfrom proxy\t{proxy}') #
                    print(f'Got token ID: {tokenID}\tfrom proxy\t{proxiesDicts[idx]}') #
                    #print('*>')
                else:
                    print(f'Got token ID: {tokenID}')
                    #print('>')
                #Open the NFT's file and write the data
                with  open(f'metadata/{COLLECTION_NAME}/'+tokenID+'.txt', 'w') as nft:
                    nft.write(response.text)    
                break
            else:
                time.sleep(0.2)
                continue
        #If NFT requests not worked
        if not done:
            #Open a file named checkID.txt with TokenID as ID with all the info of the last request
            with  open(f'metadata/{COLLECTION_NAME}/check'+tokenID+'.txt', 'w') as nft_fail:
                nft_fail.write(f'Token ID: {tokenID}\nResponse code: {response.status_code}\nResponse: {response.text}')
            print(f'\t\tProblem with: {tokenID}')

def metadataScraper(logger):
    #Get the start time 
    maxValue = ITEMS
    listJsons = []
    start = 0
    stop = maxValue

    #Test if collection start with tokenID 0 or tokenID 1 
    test_response = requests.get(url=M_LINK.replace('[X]', '0'))
    if test_response.status_code != 200 or 'error' in test_response.text: 
        start = 1
        stop = maxValue+1
    
    #Create the urls list
    urlList = [M_LINK.replace('[X]', str(i)) for i in range(start, stop)]

    #If not exist create the metadata collection's folder
    if not os.path.exists(f'metadata/{COLLECTION_NAME}'):
        os.makedirs(f'metadata/{COLLECTION_NAME}')
    elif os.path.exists(f'metadata/{COLLECTION_NAME}/1.txt'):
        urlList = check_missing_files(start, stop)

    #Get the start time 
    startTime = time.time()

    #If it's enabled the proxy use, configure the proxies and start scraping with proxies
    if USE_PROXIES:    
        avaibleProxies = len(proxiesDicts)
        nProxies = len(urlList)//20
        proxiesFormatted = [proxiesDicts[i] for i in range(0, avaibleProxies) if i < nProxies]
        requestsPerProxy = len(urlList)/len(proxiesFormatted)
        create_processes_proxy(urlList, proxiesFormatted, requestsPerProxy, logger)
    else:
        #Else start scraping without proxies
        create_processes(urlList, logger)
    
    print(f'\n{maxValue} NFTs scraped in: {time.time() - startTime}')
    logger.info(msg=f'Scraped {maxValue} NFTs in {time.time() - startTime}\nfrom collection: {MASTER_LINK}')
    
    print('Checking if there are all the NFTs...')
    logger.info(msg=f'Checking if there are all the NFTs...')
    missing_links = check_missing_files(start, stop)
    
    #If some NFTs is missing re-scrape them
    if len(missing_links) != 0:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(url_requester_single, missing_links)
    
    logger.info(msg='Scraping done! Deleting temp files...')
    #For each NFT file
    for i in range(start, stop):
        filename = f'metadata/{COLLECTION_NAME}/'+str(i)+'.txt'
        try:
            #Open the file and load the metadatas
            with open(filename, 'r') as f:
                nft = json.loads(f.read())
                #Append a new parameter named "xtokenID" and set the value with the TokenID in case the tokenID
                #  is not specified in the metadata parameters
                nft["xtokenID"] = f'{i}'
                listJsons.append(nft)
            #Remove the file
            os.remove(filename)
        except:
            link = M_LINK.replace('[X]', str(i))
            print(f'Problem with TokenID: {i}\nCheck: {link}')

    #Write all the NFTs' data in a single file
    with open(f'metadata/{COLLECTION_NAME}/{COLLECTION_NAME}.txt', 'w') as f:
        for item in listJsons:
            f.write(f'{json.dumps(item)}\n')

    logger.info(msg='NFTs successfully scraped!')
    print('Finished!')

if __name__ == '__main__':
    print('The script must be launched from bot file!')
