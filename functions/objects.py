import json, time
from config import *

#NFT class
class NFT:
    tokenID: int
    name = None
    description = None
    attributes: list
    price = None
    currency = None
    price_USD = None
    image: str
    opensea_url: str

    def __init__(self, image, tokenID, attributes):
        if 'ipfs://' in image:
            self.image = image.replace('ipfs://', 'ipfs.io/ipfs/')
        elif 'gateway.pinata.cloud' in image:
            self.image = image.replace('gateway.pinata.cloud', PRIVATE_GATEWAY)
        elif 'ipfs.io' in image:
            self.image = image.replace('ipfs.io', PRIVATE_GATEWAY)
        else:
            self.image = image
        self.tokenID = tokenID
        self.attributes = attributes
        self.url =  f'https://opensea.io/assets/{COLLECTION_ADDRESS}/{tokenID}'
 
    def __str__(self):
        string = ''
        if(self.name != None):
            string += f'Name: {self.name}\n'
        if(self.description != None):
            string += f'Description: {self.description}\n'
        string += f'\nToken ID: {self.tokenID}'
        string += f'\n\nAttributes: '
        for attribute in self.attributes:
            string += f'\n{attribute}'
        if(self.price != None and self.currency != None and self.price_USD != None):
            string += f'\n\nPrice:\n\t- {float(self.price): .4f} {self.currency}\n\t- {float(self.price_USD): .2f} $'
        string += f'\n\nLink: {self.url}\n'
        return string
    
    def __hash__(self):
        return self.tokenID.__hash__()
    
    def __repr__(self):
        return self.__str__()

    def getTokenID(self):
        return self.tokenID
    def setTokenID(self, tokenID):
        self.tokenID = tokenID
    
    def getName(self):
        return self.name
    def setName(self, name):
        self.name = name

    def getDescription(self):
        return self.description
    def setDescription(self, description):
        self.description = description.replace('\n', '')
    
    def getAttributes(self):
        return self.attributes
    def setAttributes(self, attributes):
        self.attributes = attributes
    
    def getPrice(self):
        return self.price
    def setPrice(self, price):
        self.price = price
    
    def getCurrency(self):
        return self.currency
    def setCurrency(self, currency):
        self.currency = currency

    def getPriceUSD(self):
        return self.price_USD
    def setPriceUSD(self, price_USD):
        self.price_USD = price_USD
    
    def getImage(self):
        return self.image
    def setImage(self, image):
        if 'ipfs://' in image:
            self.image = image.replace('ipfs://', 'ipfs.io/ipfs/')
        elif 'gateway.pinata.cloud' in image:
            self.image = image.replace('gateway.pinata.cloud', 'alvproject.mypinata.cloud')
        elif 'ipfs.io' in image:
            self.image = image.replace('ipfs.io', 'alvproject.mypinata.cloud')
        else:
            self.image = image

    def getOpenseaUrl(self):
        return self.opensea_url
    def setOpenseaUrl(self, url):
        self.opensea_url = url    

    def getTraitsNumber(self):
        return len(self.attributes)


#Trait class
class Trait:
    trait_type: str
    value: str
    percentage = None

    def __init__(self, trait_type, value):
        self.trait_type = trait_type
        self.value = value
    
    def __str__(self):
        string = f'- {self.trait_type} : {self.value}'
        if self.percentage != None:
            string += f' : {self.percentage: .2f} %'
        return string
    
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if self.trait_type == other.trait_type and self.value == other.value:
            return True
        else:
            return False

    def setPercentage(self, p):
        self.percentage = p

    def getTraitType(self):
        return self.trait_type
    
    def getPercentage(self):
        return self.percentage

    def getValue(self):
        return self.value

#Collection class
class Collection:
    nfts: list
    nfts_dict = {}
    traits_amount = {}
    traitTypes = {}

    #Collection's contructor, takes the NFTs
    def __init__(self, nfts):
        self.nfts = nfts
        self.CalculateTraitsAmount()
        self.nfts_dict = {nft.getTokenID():nft for nft in nfts}
    
    def getNftByTokenID(self, tokenID):
        return self.nfts_dict[tokenID]
    
    # Store in a dict {key:value}, as 'key' a number that indicate a trait number and as 'value' 
    # how much NFTs have that much traits
    # Salva in un dizionario key:value, come key il numero di tratti del NFT e come value quanti 
    # NFT hanno quel numero di tratti
    def CalculateTraitsAmount(self):
        for nft in self.nfts:
            nft_traits_number = nft.getTraitsNumber()
            if nft_traits_number not in self.traits_amount.keys():
                self.traits_amount[nft_traits_number] = 1
            else:
                self.traits_amount[nft_traits_number] += 1

    def CalculateTraitTypes(self):
        for nft in self.nfts:
            tmp_traits = nft.getAttributes()
            for trait in tmp_traits:
                if trait.getTraitType() not in self.traitTypes.keys():
                    self.traitTypes[trait.getTraitType()] = {}
                if trait.getValue() not in self.traitTypes[trait.getTraitType()].keys():
                    self.traitTypes[trait.getTraitType()][trait.getValue()] = 1
                elif trait.getValue() in self.traitTypes[trait.getTraitType()].keys():
                    self.traitTypes[trait.getTraitType()][trait.getValue()] += 1

    def getNFTs(self):
        return self.nfts
    
    def getAmountOfTraits(self):
        return self.traits_amount
    
    def getTraitTypes(self):     
        return self.traitTypes


def create_nfts_objects(data):
    objects = []
    #For nft('raw json data') in NFTs
    for nft in data:
        try:
            traits = []
            #For each attribute
            for attribute in nft['attributes']:
                tmp_trait = Trait(attribute['trait_type'], attribute['value'])
                if tmp_trait not in traits:
                   traits.append(tmp_trait)
            #Create the NFT with base data
            tmp_NFT = NFT(nft['image'], int(nft['xtokenID']), traits)
            try:
                #If there's a name in json parameter set it
                if(nft['name']):
                    tmp_NFT.setName(str(nft['name']))
            except:
                pass
            try:
                #If there's a description in json parameter set it
                if(nft['description']):
                    tmp_NFT.setDescription(str(nft['description']))
            except:
                pass

            #Append the NFT to the list objects
            objects.append(tmp_NFT)
        except:
            continue
    #Return the objects list
    return objects



def createCollection():
    json_list = []
    #Open the file with all the NFTs' data and load them
    with open(f'metadata/{COLLECTION_NAME}/{COLLECTION_NAME}.txt', 'r') as f:
        for line in f.readlines():
            if line != '\n':
                json_list.append(json.loads(line))

    #Create a collection
    collection = Collection(create_nfts_objects(json_list))
    traits_number_with_value = collection.getAmountOfTraits()
    #Sort the list from the most aboundant traits to the least
    traits_number_with_value = {k: v for k, v in sorted(traits_number_with_value.items(), reverse=True, key=lambda item: item[1])}
    #For each NFT in the collection 
    for nft in collection.getNFTs():       
        #For each {key:value} with 'key' as a number that indicate a traits number and 'value' as the number of NFTs that 
        # have that much of traits
        for key, value in traits_number_with_value.items():
            #If NFT have that much trait 
            if int(nft.getTraitsNumber()) == int(key):
                tmp = nft.getAttributes()
                tmp.append(Trait('Trait Count', str(key)))
                nft.setAttributes(tmp)
                break
    collection.CalculateTraitTypes()
    start = time.time()
    print(f'\nAnalyzing... please wait')
    for trait_type, values in collection.getTraitTypes().items():
        values = {k: v for k, v in sorted(values.items(), reverse=True, key=lambda item: item[1])}
        for name, value in values.items():
            for nft in collection.getNFTs():
                for trait in nft.getAttributes():
                    if trait.getValue() == name and trait.getTraitType() == trait_type:
                        trait.setPercentage((value/(ITEMS/100)))
    print(f'Time taken: {time.time()-start:.2f} s')
    return collection
