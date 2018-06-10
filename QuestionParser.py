


from Triples import *
from Specs import *
from TextNormalizer import *
from NLP import *
from test_nounify import *
from word2number import w2n
import re
from nltk.stem import WordNetLemmatizer
from IDfinder import *
import requests
import spacy
nlp = spacy.load('en_core_web_sm')

class QuestionParser:
    ###takes a string and creates a sparql query

    def __init__(self, question, specs):
        self.url = 'https://query.wikidata.org//sparql'
        self.lemmatizer = WordNetLemmatizer()
        self.specs = specs                   ##patterns, keywords, anything important could will be added here
        self.question = question  ##question string
        self.nlp = NLP(self.question, self.specs)
        self.possible_words = self.parse_spacy()  ##dictionary that stores possible words in a triple by type (Object, Property, Result)
        self.sort = None
        self.type = self.determineQuestionType()            ##true_false, count or list (single answer is just a list with 1 element)
        self.variable = ''                                  ##the variable names that will be in the SELECT command
        self.targetVariable = ''                            ##the variable which will be printed in the end
        self.qWord = self.getQuestionWord()

        self.question_SQL = ''                              ##the Sparql query will be stored here (as string)
        self.possible_triples = self.tripleCombinations()   ##the possible query triples are here

        print("possible triples :")
        print(self.possible_triples)
        ##print(self.possible_triples)
        self.query_list = []                                ##the query statements (triples) are listed here

        ##self.parse_spacy()

    def determineQuestionType(self):

        #check if true/false question, and check if superlative or comparative::

        if self.nlp.tokens[0].text.lower() in self.specs.true_false_list['starters']:
            return 'true_false'
        prevText = ""
        for word in self.nlp.tokens:
            text = word.text.lower()            #converting to lowercase as the keywords in the specs are lowercase
            if text in self.specs.true_false_list['somewhereInText']:
                return 'true_false'
            if text in self.specs.count_list['singles'] or ( prevText + " " + text) in self.specs.count_list['doubles']:
                return 'count'
            if word.tag_ == 'JJS' and word.dep_!= 'amod':
                self.getSortID()
                return "superlative"
            if word.tag_ == 'JJR':
                if self.isListComparative():
                    return 'comparative_list'
                else:
                    return 'comparative_objects'
            prevText = text


        #check if count type:
            #TODO

        #rest is list type:
        return "list"

    def isListComparative(self):            ##in case a comparative adjective is found, determines if it compares objects (what is bigger, France or Germany), or wants us to list things (What is bigger than France)
        ##property should be found in the common list
        for word in self.nlp.tokens:
            if word.text in self.specs.common_IDs:
                self.possible_words['Property'] = [word.text]       ##if properrty found, we know that it is the property of interest, we can delete others
                break
        ##check if there are two objects, that are the instance of the same thing, e.g. Germany and France instance of country
        for i in range(0,len(self.possible_words["Object"])):
            for j in range(i + 1,len(self.possible_words["Object"])):
                try:
                    #print("starting try block for comparative instances")
                    #print("words are")
                    #print(self.possible_words["Object"][i])
                    #print(self.possible_words["Object"][j])

                    data1 = requests.get(self.url, params = {'query':self.constructQuery(self.queryStatementFromTriple(self.getTripleFromWordsAndFormat([self.possible_words["Object"][i], "instance of", ""], self.specs.basic_question_formats["Result"]))), 'format': 'json'}).json()
                    data2 = requests.get(self.url, params = {'query':self.constructQuery(self.queryStatementFromTriple(self.getTripleFromWordsAndFormat([self.possible_words["Object"][j], "instance of", ""], self.specs.basic_question_formats["Result"]))), 'format': 'json'}).json()
                    #print("both queries succeeded")
                    for answer1 in data1['results']['bindings']:
                        for answer2 in data2['results']['bindings']:
                            if (answer1[(self.targetVariable)[1:]]['value'] == answer2[(self.targetVariable)[1:]]['value']):
                                print("comparing" + str(answer1) + " and " + str(answer2))
                                self.possible_words['Object'] = [self.possible_words["Object"][i], self.possible_words["Object"][j]]              #if match found, we know that these are the objects of interest, no need for other possible objects
                                self.possible_words['Result'] = []
                                return False
                except:
                    print("an error occured while comparing the words")
                    print(self.possible_words["Object"][i])
                    print(self.possible_words["Object"][j])
                    pass

        return True


    def getSortID(self):
        if self.type == 'superlative':
            for token in self.nlp.tokens:
                if token.tag_ == 'JJS':
                    possible_sort_words = [token.lemma_] + nounify(token.lemma_)
                    for word in possible_sort_words:
                        ID = IDfinder(word, "property", self.specs).findIdentifier()
                        if ID != '':
                            print("ID found for word " + word + ", ID is " + str(ID))
                            return ID
        return None

    def getQuestionWord(self):
        for word in self.nlp.tokens:
            if word.text in list(self.specs.question_words.keys()):
                return word.text

    def parse_regex(self):
        for key in self.specs.patterns['triples']:              ##specs is a dict with regex pattern as key, and order of arguments as value
            #print(key)
            matchObj = re.search(key, self.question, re.M|re.I|re.U)
            if matchObj:
                #print("expression found")
                triple = [TextNormalizer(matchObj.group(1)).allowedTagKeeper('noun_adjective'), TextNormalizer(matchObj.group(2)).allowedTagKeeper('noun_adjective') , ""]          ##instead of complicated regex, i remove everything from a group that is not a noun, we know that only those are meaningful in wikidata IDs
                                                                                                                                                                ##an empty element is added in the end as a placeholder for the variable, that is obviously not in the text, for the sake of similar indexing with the order in specs
                #print(triple)
                T = Triple(triple, self.specs.patterns['triples'][key])
                self.variable = T.variable          ##set the question variables to be equal to the triple variables TODO: selection in multiple triples
                self.targetVariable = T.targetVariable
                self.query_list.append(T.SQL)

    def parse_spacy(self):
        possible_words = {"Object":[], "Property":[], "Result":[]}
        for key, val in self.specs.deps.items():
            for dep in val:
                ##print(dep)
                a = (self.nlp.returnDep(dep))
                if a != None:
                    possible_words[key]+= a
            #print ("the " + key + "s of this sentence are ")
            #print(possible_words[key])
        return possible_words

    def extended_parse_spacy(self):                 ### the words with deps in the extended list are not added to the possible words, just their nounified versions
        for key, val in self.specs.extended_deps.items():
            for dep in val:
                ##print(dep)
                a = (self.nlp.returnDep(dep))
                if a != None:
                    print("extending with dep " + str(dep) + ", list is " + str(a))
                    for word in a:
                        print("trying the word" + word)
                        self.possible_words[key] += nounify(word)
        self.possible_triples = self.tripleCombinations()
                    # print ("the " + key + "s of this sentence are ")
                    # print(possible_words[key])

    def getNumberOfAnswers(self):
        for token in self.nlp.tokens:
            if token.tag_ == "CD":
                #print("found token " + token.text + " as number")
                try:
                    return w2n.word_to_num(token.text)
                except:
                    return 0
        return 0

    def addNounSynonims(self):

        for key, wordList in self.possible_words.items():
            for word in list(wordList):
                print("word is ")
                print(word)
                if isinstance(word, str):
                    self.possible_words[key] += nounify(word)
            print("key is " + str(key) + " extended list is ")
            print(wordList)

        self.possible_triples = self.tripleCombinations()
        return

    def induceWordsFromQuestionWord(self):
	    if self.qWord != None:                      #fixed
        	self.possible_words["Property"] = self.possible_words["Property"] + (self.specs.question_words[self.qWord])
        	self.possible_triples = self.tripleCombinations()

    def generateCombinations(self, a, aIndex, b, bIndex, ret):          ##recursively generates each pair given two lists
        ret.append([a[aIndex], b[bIndex]])
        if aIndex<len(a)-1:
            self.generateCombinations(a, aIndex+1, b, bIndex, ret)
        if bIndex<len(b)-1:
            self.generateCombinations(a, aIndex, b, bIndex +1, ret)
        return ret


    def tripleCombinations(self):      ##this returns a triple with one position being "", placeholder for the variable
        print("construction triples with input")
        print(self.possible_words)

        possible_triples = {"Result":[],            ##first one is result, as the queries are constructed in this order, and most questions target the result
                            "Object":[],
                            "Property":[]}
        a = self.possible_words["Object"]
        b = self.possible_words["Property"]
        if a and b:
            for combination in self.generateCombinations(a,0,b ,0, []):
                if combination[0] != combination[1]:        ##same word should not appear in 2 positions
                    possible_triples["Result"].append([self.lemmatizer.lemmatize(combination[0]), self.lemmatizer.lemmatize(combination[1]), ""] )

        a = self.possible_words["Object"]
        b = self.possible_words["Result"]
        if a and b:
            for combination in self.generateCombinations(a, 0, b, 0, []):
                if combination[0] != combination[1]:  ##same word should not appear in 2 positions
                    possible_triples["Property"].append([self.lemmatizer.lemmatize(combination[0]), "", self.lemmatizer.lemmatize(combination[1])])

        a = self.possible_words["Property"]
        b = self.possible_words["Result"]
        if a and b:
            for combination in self.generateCombinations(a, 0, b, 0, []):
                if combination[0] != combination[1]:  ##same word should not appear in 2 positions
                    possible_triples["Object"].append(["",self.lemmatizer.lemmatize(combination[0]), self.lemmatizer.lemmatize(combination[1])])
        return possible_triples


    def queryBodyFromList(self, list):
        ret = ""
        for sentence in list:
            ret = ret + sentence + "\n"

        return ret

    def queryStatementFromTriple(self, triple):
        #print("triple query statement is ")
        #print(triple.SQL)
        return triple.SQL

    def getTripleFromWordsAndFormat(self, words, format):
        T = Triple(words, format, self.specs)
        self.getVariableNames(T)
        return T

    def getVariableNames(self, triple):
        print("Passing variable names, var is " + triple.variable + "targetvar is " + triple.targetVariable)
        self.variable = triple.variable
        self.targetVariable = triple.targetVariable

    def constructQuery(self, queryBody):
        #print("constructing query with " + queryBody)
        self.question_SQL = "SELECT " + self.variable + """ WHERE {
        """
        self.question_SQL = self.question_SQL + queryBody
        self.question_SQL = self.question_SQL + """
        SERVICE wikibase:label {
        bd:serviceParam wikibase:language "en" .                        
        }
}
        """                                                             ##last part: gets labels for wikidata IDs
        #print("checking for sort")
        if self.sort != None:
            self.question_SQL += "\nORDER BY DESC(?sort)"
        print(self.question_SQL)
        return self.question_SQL
