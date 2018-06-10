## Issues: Inconsistent use of tabs and spaces in indentation 184 QuestionParser


from QuestionParser import *
from QuestionAnswerer import *

import requests
import sys

###The system works as follows:
##reads an input -> finds groups of words of interest (regex) -> removes unimportant word types (POS) -> creates an ordered triple based on the patterns defined in specification -> Gets the ID for the words in the triple -> constructs a query using the IDs -> requests and prints answer for the quesry
##The system is very general, works on every domain, and new patterns can be added with only a definition in the specification, no need to change the code in ant way
##Example: pattern with Y's X is added besides X of Y, works perfectly

##############################################  define specification for the task here ###################################
spec1 = {
    'ignored_words':["is", "true", "false", "yes", "no", "list"],
    'question_words':{'What': ["instance of", "subclass of"],
                      'Who':["instance of"],
                      'Where': ['continent'],
		      'When': ['point in time','start time','end time']
                      },
    'basic_question_formats':{"Object":[{'variable':'Object'},'Property', 'Result'],
                        "Property":['Object', {'variable':'Property'}, 'Result'],
                        "Result": ['Object', 'Property', {'variable':'Result'}]},
    'patterns':{'triples':{
                r"(.*) of ([^\\?]+)":['Property', 'Object', {'variable':'Result'}],
                r"(.*)'s ([^\\?]+)":['Object', 'Property', {'variable':'Result'}]
                ###Throughout the code I call the elements of a wikidata triple Object - Property - Result
                ###This dictionary defines what order of these entities corresponds to a pattern (key), so the parser will know how to put the query together
                ##regex stopword removal (kept for potential use later): (?:the|a|an)?\s*
                },
    },
    'deps':{"Object": ["pobj", "poss", "nsubj", "conj", "dobj", "npadvmod", "appos"],                 ##we store here the possible deps (returned by spacy) for each element in a triple
            "Property" : ["attr", "nsubj", "acomp", "dobj","pcomp"],
            "Result": ["attr", "acomp", "advcl"]
            },
    'extended_deps':{"Object": ["dobj","compound"],                 ##The deps that should be considered when looking at the synonims and nounified words
                        "Property" : ["ROOT","acl"],
                        "Result": ["pobj"]
                    },
    'true_false_list':{"starters":['is', 'has', 'does', 'was', 'do'],
                       "somewhereInText": ['true', 'false', 'yes', 'no']},
    'count_list':{"singles":["count"],          #single words
                "doubles":["how many", "how much"]},         #two word expressions
    'tags_of_interest': ["JJ", "JJR", "JJS", "NN", "NNS", "NNP", "NNPS", "RB", "RBS", "RBR", "VB", "VBD", "VBG", "VBP", "VBZ"],
    'print':True,
    'common_IDs':{"highest": "P2044",
                  "high":"P2044",
                  "higher":"P2044",
                  "longest": "P2043",
                  "long":"P2043",
                  "longer":"P2043",
                  "length":"P2043",
                  "member":"P150",
                  "county":"P150",
                  "state":"P150",
                  "language":"P37",            #language -> official language
                  "bigger":"P2046",
                  "big":"P2046",
                  "size":"P2046",
    }
}
###the specs are passed to the outer class as an argument, several versions can be defined here separately
##########################################################################################################################
print('Exit by typing Bye')
question = ''
while question != 'Bye':
    question = input("Enter a question:")
    if question != 'Bye':                           ##no do while in python :(
        QuestionAnswerer(QuestionParser(question, Specification(spec1))).getAnswer()
