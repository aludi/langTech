import spacy
##import nltk

class NLP:
    def __init__(self, text, specs):
        self.specs = specs
        self.text = text
        self.nlp = spacy.load('en')
        self.tokens = self.nlp(text)
        #self.printDep()

    def lemmas(self):
        ret = []
        for word in self.tokens:
            ret.add(word.lemma_)
        return ret

    def returnDep(self, dep):
        ret = []
        ##print(type(self.tokens))
        for w in range(0,len(self.tokens)):
            print("word is " + str(self.tokens[w]) + " dep is " + str(self.tokens[w].dep_) + " tag is " + str(self.tokens[w].tag_))
            print(w)
            if self.tokens[w].dep_ == dep and not self.tokens[w].text in list(self.specs.question_words.keys()) and not self.tokens[w].text.lower() in self.specs.ignored_words and str(self.tokens[w].tag_) in self.specs.tags_of_interest:
                instance = []
                instance.append(self.tokens[w].lemma_) #text to lemma
                i = w-1
                while self.tokens[i].dep_ == "compound" or self.tokens[i].dep_ == "amod": #added amod
                    if self.tokens[i].dep_ == 'amod':
                        instance.append(self.tokens[i].text)  # add text, since lemma of amod is not a property
                    else:
                        instance.append(self.tokens[i].lemma_) #text to lemma
                    #print("adding " + str(self.tokens[i].text))
                    i = i-1
                ret.append(" ".join(reversed(instance)))
		
        if ret != []:
            print(ret)
            return ret

    def printDep(self):
        for w in self.tokens:
            print(w)
            print(w.dep_)




# text = "Who is the president of the United States?"
# nlp = NLP(text)
# nlp.printDep()
# dep = "pobj"
# print("The " + dep + " is:")
# print(nlp.returnDep(dep))