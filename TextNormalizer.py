from nltk import word_tokenize
from nltk import pos_tag


class TextNormalizer:
    def __init__(self, text):
        self.text = text
        self.tokenized_text = word_tokenize(text)
        self.nounTags = ["NN", "NNS", "NNP", "NNPS"]
        self.nouns_adjectiveTags = ["JJ", "JJR", "JJS", "NN", "NNS", "NNP", "NNPS"]         ###although we only need nouns, i found the pos tag to mistake nouns for adjectives
        ##ll relevant (for later use) #["JJ", "JJR", "JJS", "NN", "NNS", "NNP", "NNPS", "RB", "RBS", "RBR", "VB", "VBD", "VBG", "VBP", "VBZ"]
    def allowedTagKeeper(self, allowed):
        allowedTags = []
        if allowed == 'noun':                   ##for now only nouns are defined, later more can be added
            allowedTags = self.nounTags
        elif allowed =='noun_adjective':
            allowedTags = self.nouns_adjectiveTags

        keep = [tag for tag in (pos_tag(self.tokenized_text)) if tag[1] in allowedTags]            ##tokenizes and POS tags, removes all that is not allowed
        ret = ''
        for word in keep:
            ret = ret + ' ' + word[0]                                                                   ##creates a list of strings so the tags are not returned
        return ret
