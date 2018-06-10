#!/usr/bin/python3
import sys
import requests

class IDfinder:
    ###the IDfinder uses the wikidata API to get ID
    ###Since those results are ordered based on frequency of usage, we return the first hit, assuming that is the one of interest
    def __init__(self, word, type, specs):
        self.specs = specs
        self.word = ''.join(word)
        #print("word is ")
        #print(self.word)
        #print("type is")
        #print(isinstance(self.word, str))
        self.url = 'https://www.wikidata.org/w/api.php'
        self.params = {'action' : 'wbsearchentities',
                       'language': 'en',
                       'format': 'json' ,
                       'search':self.word}
        if type == 'property':
            self.params.update({'type':'property'})

    def findIdentifier(self):
        if self.word in self.specs.common_IDs.keys():
            print(self.word + "has a common ID")
            return self.specs.common_IDs[self.word]
        try:
            json = requests.get(self.url,self.params).json()
        #print (json)
            return json['search'][0]['id']
        except:
            print("ID not found for '" + self.word + "'")
            return('')