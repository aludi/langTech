from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
import spacy

nlp = spacy.load('en')

def nounify(word):
    result = []
    """ Transform a verb to the closest noun: die -> death """
    word = WordNetLemmatizer().lemmatize(word)

    #alternate, spacy method
    #newWord = nlp(word)
    #for w in newWord:
       # word = w.lemma_
      #  print(word)
    #word = newWord.lemma_
    ## end spacy method

    print('nounifying word ' + str(word))
    word_synsets = wn.synsets(word)

    # Word not found
    if not word_synsets:
        return []
    #print("synsets are ")
    #print(word_synsets)
    # Get all lemmas of the word
    word_lemmas = []
    for s in word_synsets:
        word_lemmas.append(s.lemmas())

    #print("lemmas are ")
    #print(word_lemmas)
    # Get related forms
    derivationally_related_forms =[]
    for lemmalist in word_lemmas:
        for l in lemmalist:
            derivationally_related_forms.append(l.derivationally_related_forms())
    #print("derivationally related forms are")
    #print(derivationally_related_forms)
    # filter only the nouns
    related_noun_lemmas = [l for drf in derivationally_related_forms \
                           for l in drf if l.synset().name().split('.')[1] == 'n']
    #print("noun lemmas are")
    #print(related_noun_lemmas)
    # Extract the words from the lemmas
    words = [l.name() for l in related_noun_lemmas]
    len_words = len(words)

    # Build the result in the form of a list containing tuples (word, probability)
    result = result + [(w, float(words.count(w))/len_words) for w in set(words)]
    result.sort(key=lambda w: -w[1])
    result = [res[0] for res in result]
    print("results are")
    print(result)

    # return all the possibilities sorted by probability
    return result
