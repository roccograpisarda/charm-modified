from uttInputReader import *
from random import randint, choice, choices, sample
from string import printable, whitespace
from googletrans import Translator, LANGUAGES #pip install googletrans
#from translate import Translator  # PIP INSTALL TRANSLATE
import inflect
from word2number import w2n
#from yandex.Translater import Translater

# import stanfordnlp
#from pattern.en import *
#from PyDictionary import PyDictionary
import requests
from bs4 import BeautifulSoup
#import nltk
#from nltk.stem.wordnet import WordNetLemmatizer
#nltk.download('wordnet')
from operator import itemgetter
from os import remove
import configparser

import stanza

keyboardQWERTYSpanish = [[['1','!'],['2','"'],['3','·'],['4','$'],['5','%'],['6','&'],['7','/'],['8','('],['9',')'],['0','='],['\'','?'],['¡','¿']],
                        [['q','Q'],['w', 'W'],['e','E'],['r','R'],['t','T'],['y','Y'],['u','U'],['i','I'],['o','O'],['p','P'],['`','^'],['+','*']],
                        [['a','A'],['s','S'],['d','D'],['f','F'],['g','G'],['h','H'],['j','J'],['k','K'],['l','L'],['ñ','Ñ'],['\'','̈́'],['ç','Ç']],
                        [['<', '>'],['z','Z'],['x','X'],['c','C'],['v','V'],['b','B'],['n','N'],['m','M'],[',',';'],['.',':'],['-','_']]]

"""
This function will return the keys that are surrounding the key passed.
For doing this we have to search the index of the key, and return all the keys that surround it in the matrix
"""
def getNearbyKeys(key, keyboardConfig):

    nbkeys = []

    def getKeyIndex(key, keyboardConfig):
        for i, row in enumerate(keyboardConfig):
            for j, keys in enumerate(row):
                if key in keys:
                    return i, j

    i, j = getKeyIndex(key, keyboardConfig)

    if i == 0: # linea 0
        if j==0: #izquierda linea 0
            nbkeys = [keyboardConfig[i][j+1], keyboardConfig[i+1][j+1], keyboardConfig[i+1][j]]
#			for elem in [keyboardConfig[i][j-1], keyboardConfig[i+1][j-1]]:
#				nbkeys.remove(elem)
        elif j==len(keyboardConfig[i])-1: # derecha linea 0
            nbkeys = [keyboardConfig[i+1][j], keyboardConfig[i+1][j-1], keyboardConfig[i][j-1]]
#			for elem in [keyboardConfig[i][j+1], keyboardConfig[i+1][j+1]]:
#				nbkeys.remove(elem)
        else:
            nbkeys = [keyboardConfig[i][j+1], keyboardConfig[i+1][j+1], keyboardConfig[i+1][j], keyboardConfig[i+1][j-1], keyboardConfig[i][j-1]]

    elif (i > 0 and i < 3): # lineas 1 o 2
        if j==0: #izquierda linea 1 o 2
            nbkeys = [keyboardConfig[i-1][j], keyboardConfig[i-1][j+1], keyboardConfig[i][j+1],
                keyboardConfig[i+1][j+1], keyboardConfig[i+1][j]]
#			for elem in [keyboardConfig[i][j-1], keyboardConfig[i-1][j-1], keyboardConfig[i+1][j-1]]:
#				nbkeys.remove(elem)
        elif j==len(keyboardConfig[i])-1: # derecha linea 1 o 2
            nbkeys = [keyboardConfig[i-1][j-1], keyboardConfig[i-1][j], keyboardConfig[i+1][j-1], keyboardConfig[i][j-1]]
#			for elem in [keyboardConfig[i][j+1], keyboardConfig[i-1][j+1], keyboardConfig[i+1][j+1]]:
#				nbkeys.remove(elem)
        else:
            nbkeys = [keyboardConfig[i-1][j-1], keyboardConfig[i-1][j], keyboardConfig[i-1][j+1], keyboardConfig[i][j+1],
                        keyboardConfig[i+1][j+1], keyboardConfig[i+1][j], keyboardConfig[i+1][j-1], keyboardConfig[i][j-1]]
    else: # linea 3

        if j==0: #izquierda linea 3
            nbkeys = [keyboardConfig[i-1][j], keyboardConfig[i-1][j+1], keyboardConfig[i][j+1]]
#			for elem in [keyboardConfig[i][j-1], keyboardConfig[i-1][j-1]]:
#				nbkeys.remove(elem)
        elif j==len(keyboardConfig[i])-1: # derecha linea 3
            nbkeys = [keyboardConfig[i-1][j-1], keyboardConfig[i-1][j], keyboardConfig[i][j-1]]
#			for elem in [keyboardConfig[i][j+1], keyboardConfig[i-1][j+1]]:
#				nbkeys.remove(elem)
        else:

            nbkeys = [keyboardConfig[i-1][j-1], keyboardConfig[i-1][j], keyboardConfig[i-1][j+1], keyboardConfig[i][j+1], keyboardConfig[i][j-1]]


    return nbkeys

"""
    This function will mutate any of the letters of the utterance for any
    Other key which distance of the original letter is the correspondant to the variable 
    passed as an argument 

    To know the configuration of the keyboard, we will need the configuration of the keyboard aswell, 
    and a way to see the distances between keys (we could create a matrix)
"""

def mutateUtteranceWithDistances(utt, botDir, percentage=10, variability=0, keyboardConfig=keyboardQWERTYSpanish):
    config = configparser.RawConfigParser()
    config.read('./config.cfg')
    config_details = get_config_dict('project')
    counter = 0
    for pos, letter in enumerate(utt):
        if not(letter.isspace()):
            mutate = choices([True, False], [percentage/100, 1-percentage/100])[0]
            if mutate:
                uttAux = list(utt)
                i = randint(0, 1) # we choose between the shifted keyboard or normal one
                uttAux[pos] = choice(getNearbyKeys(letter, keyboardConfig))[i]
                utt = "".join(uttAux)
                if percentage+variability > 1:
                    percentage += variability
                counter += 1
    statsDir = (config_details['root_project_dir'] + "/proyecto/codigo/output/{}/").format(botDir)
    filename = "mutateUtteranceWithDistancesStats.txt"
    writeCounter(statsDir, filename, counter, len(utt))
    return utt

"""
    This function will mutate any of the letters of the utterance for any
    Other letter
    parameters: 
        utt: the utterance that is going to be muted
        percentage: the percentage of mutation
        variability: the value that the percentage will increase if there is a mutation
"""
def mutateUtterance(utt, botDir, percentage=10, variability=0):
    config = configparser.RawConfigParser()
    config.read('./config.cfg')
    config_details = get_config_dict('project')
    counter = 0
    keysAscii = list(printable.strip(whitespace))
    for position, letter in enumerate(utt):
        if not(letter.isspace()):
            mutate = choices([True, False], [percentage/100, 1-percentage/100])[0]
            if mutate:
                uttAux = list(utt)
                uttAux[position] = choice(keysAscii)
                utt = "".join(uttAux)
                if percentage > 1:
                    percentage += variability
                counter += 1
    statsDir = (config_details['root_project_dir'] + "/proyecto/codigo/output/{}/").format(botDir)
    filename = "mutateUtteranceStats.txt"
    writeCounter(statsDir, filename, counter, len(utt))
    return utt

"""
    This function will delete any of the letters of the utterance if choiced randomly
    parameters: 
        utt: the utterance that is going to be muted
        percentage: the percentage of mutation
        variability: the value that the percentage will increase if there is a mutation
"""
def deleteChars(utt, botDir, percentage=10, variability=0):
    config = configparser.RawConfigParser()
    config.read('./config.cfg')
    config_details = get_config_dict('project')
    position = 0
    counter = 0
    lengthUtt = len(utt)
    for i in range(lengthUtt):
        mutate = choices([True, False], [percentage/100, 1-percentage/100])[0]
        if mutate:
            uttAux = list(utt)
            if position==0:
                uttAux = uttAux[position+1:]
            elif position>=len(uttAux)-1:
                uttAux = uttAux[:position+1]
            else:
                uttAux = uttAux[:position]+uttAux[position+1:]
            utt = "".join(uttAux)

            if percentage > 1:
                percentage += variability
            counter += 1
        else:
            position += 1
    statsDir = (config_details['root_project_dir'] + "/proyecto/codigo/output/{}/").format(botDir)
    filename = "deleteCharsStats.txt"
    writeCounter(statsDir, filename, counter, lengthUtt)
    return utt

"""
    This method will change each number of the utterance to a word 
"""
def changeNumberToWord(utt):
    words = []
    p = inflect.engine()
    nums = [int(word) for word in utt.split() if word.isdigit()]
    if nums:
        for num in nums:
            words.append(p.number_to_words(num))
        i=0
        for word in utt.split():
            if word.isdigit():
                utt = utt.replace(word, words[i], 1)
                i+=1
    return utt

def changeWordToNumber(utt):
    def isNum(word):
        try:
            w2n.word_to_num(word)
            return True
        except ValueError:
            return False

    uttAux = utt.split()
    numbersDict = {}
    numJoin = 0
    numbers = []
    posDel = []

    for i, word in enumerate(uttAux):
        if isNum(word):
            if numJoin not in numbersDict:
                numbersDict[numJoin] = []

            numbersDict[numJoin].append((i, word))

            if i + 1 < len(uttAux):
                if uttAux[i + 1] == "and":
                    numbersDict[numJoin].append((i + 1, uttAux[i + 1]))
                if not isNum(uttAux[i + 1]) and uttAux[i + 1] != "and":
                    numJoin += 1

    for value in numbersDict.values():
        number = " ".join([elem[1] for elem in value])
        numbers.append((value[0][0], number))
        if len(value) > 1:
            posDel.extend([elem[0] for elem in value[1:]])

    if numbers:
        utt = utt.split()
        for i, num in enumerate(numbers):
            utt[num[0]] = str(w2n.word_to_num(num[1]))

        utt = [word for i, word in enumerate(utt) if i not in posDel]

        if isinstance(utt, list):
            return " ".join(utt)
    else:
        return utt

"""
    .
"""

# Function: traductionChained
# Purpose: This function will submit the utterance to a traduction chain that will change the structure
#          of the utterance and will simplify it normally.
# Input:
# - utt: The input utterance to be translated.
# - languages: A list of languages to translate 'utt' through.
# Output:
# - Returns the final translated text after going through the language chain.

def traductionChained(utt, languages):

    # Initialize the Google Translate API
    translator = Translator()  

    # Detect the original language
    originLang = translator.detect(utt).lang
    print("The original language is:",originLang)
  
    # Translate the input text through the chain of languages
    for language in languages:
        translation = translator.translate(utt, src=originLang, dest=language)
        print("the translation is: ", translation)
        utt = translation.text
        originLang = language

    # Translate back to the original language
    translation = translator.translate(utt, src=originLang, dest=originLang)
    utt = translation.text

    # Return the final translated text
    return utt



""" 
    THE OLD VERSION OF traductionChained which used the Yandex Translater
def traductionChained(utt, languages):
    config = configparser.RawConfigParser()
    config.read('./config.cfg')
    config_details = get_config_dict('project')

    tr = Translater()
    tr.set_key(config_details['yandex_api_key'])
    tr.set_text(utt)
    originLang = tr.detect_lang()
    print(originLang)
    tr.set_from_lang(originLang)
    tr.set_to_lang(languages[0])
    tr.set_text(utt)
    utt = tr.translate()

    for i, lan in enumerate(languages):
        tr.set_from_lang(lan)
        if i < len(languages)-1:
            tr.set_to_lang(languages[i+1])
        else:
            tr.set_to_lang(originLang)

        utt = tr.translate()
        tr.set_text(utt)

    #print(utt)
    return utt
#	translator = Translator()
#	oriLang = translator.detect(utt)
#	return

#	lanAux = originLang
#
#	for language in languages:
#		translator= Translator(from_lang=lanAux, to_lang=language)
#		utt = translator.translate(utt)
#		lanAux = language
#
#	translator = Translator(from_lang=lanAux, to_lang=originLang) # We convert it to the original language	
#	utt = translator.translate(utt)
#
#	return utt.replace("&#39;", "'") """



# Function: randomTraductionChained
# Purpose: Generate a random translation chain for an input utterance.
# Input:
# - utt: The input utterance to be translated.
# - numLanguages: The number of random languages to include in the translation chain (default is 2).
# Output:
# - Returns the final translated text after passing it through the random language chain.

def randomTraductionChained(utt, numLanguages=2):
    # List of languages supported for translation
    languagesSupported = ['af', 'sq', 'hy', 'az', 'it', 'eu', 'be', 'bg', 'ca', 'hr', 'cs', 'da', 'nl', 'et', 'fi', 'fr', 'zh-cn']

    # Randomly sample 'numLanguages' from the supported languages
    languages = sample(languagesSupported, numLanguages)
    
    # Use the 'traductionChained' function to perform translations through the random language chain
    return traductionChained(utt, languages)


#	languages = sample(LANGUAGES.keys(), numLanguages)
#	translator = Translator()
#	oriLang = translator.detect(utt).lang
#
#	languages.insert(0, oriLang)
#	languages.append(oriLang)
#
#	print(languages)
#	print(utt)
#
#	for ind, language in enumerate(languages):
#		if not(ind == len(languages)-1):
#			print(language, languages[ind+1])
#			utt = translator.translate(utt, src=language, dest=languages[ind+1]).text
#			print(utt)
#	print("\n______________________________________\n")
#
#	return


"""
This function will convert a passive voice sentence into an active voice one.
To do that
EXAMPLE:   can I get three bedroom apartments please

1) Make the object of the active sentence into the subject of the passive sentence.
    three bedroom apartments (everything related with the object appartments will be part of the subject aswell)

2) Use the verb “to be” in the same tense as the main verb of the active sentence.
    three bedroom appartments can be 

3) Use the past participle of the main verb of the active sentence.
    three bedroom appartments can be taken (by me)

example:
    Active voice: I will take a quesarito with extra cheese to eat please.
            Subject(I), Verb(will take), object(quesarito), 		
    Passive voice: the quesarito with extra cheese will be taken to eat (by me).
"""

"""
['[<Token index=1;words=[<Word index=1;text=can;lemma=can;upos=AUX;xpos=MD;feats=VerbForm=Fin;governor=3;dependency_relation=aux>]>, 
   <Token index=2;words=[<Word index=2;text=I;lemma=I;upos=PRON;xpos=PRP;feats=Case=Nom|Number=Sing|Person=1|PronType=Prs;governor=3;dependency_relation=nsubj>]>, 
   <Token index=3;words=[<Word index=3;text=get;lemma=get;upos=VERB;xpos=VB;feats=VerbForm=Inf;governor=0;dependency_relation=root>]>, 
   <Token index=4;words=[<Word index=4;text=three;lemma=three;upos=NUM;xpos=CD;feats=NumType=Card;governor=6;dependency_relation=nummod>]>, 
   <Token index=5;words=[<Word index=5;text=bedroom;lemma=bedroom;upos=NOUN;xpos=NN;feats=Number=Sing;governor=6;dependency_relation=compound>]>, 
   <Token index=6;words=[<Word index=6;text=apartments;lemma=apartment;upos=NOUN;xpos=NNS;feats=Number=Plur;governor=3;dependency_relation=obj>]>, 
   <Token index=7;words=[<Word index=7;text=please;lemma=please;upos=INTJ;xpos=UH;feats=_;governor=3;dependency_relation=discourse>]>]'

[
<Word index=1;text=I;		lemma=I;		upos=PRON;	xpos=PRP;	feats=Case=Nom|Number=Sing|Person=1|PronType=Prs;	governor=2;	dependency_relation=nsubj>, 
<Word index=2;text=want;	lemma=want;		upos=VERB;	xpos=VBP;	feats=Mood=Ind|Tense=Pres|VerbForm=Fin;				governor=0;	dependency_relation=root>, 
<Word index=3;text=to;		lemma=to;		upos=PART;	xpos=TO;	feats=_;											governor=4;	dependency_relation=mark>, 
<Word index=4;text=order;	lemma=order;	upos=VERB;	xpos=VB;	feats=VerbForm=Inf;									governor=2;	dependency_relation=xcomp>, 

<Word index=5;text=a;		lemma=a;		upos=DET;	xpos=DT;	feats=Definite=Ind|PronType=Art;					governor=6;	dependency_relation=det>, 
<Word index=6;text=flight;	lemma=flight;	upos=NOUN;	xpos=NN;	feats=Number=Sing;									governor=4;	dependency_relation=obj>, 
<Word index=7;text=to;		lemma=to;		upos=ADP;	xpos=IN;	feats=_;											governor=9;	dependency_relation=case>, 
<Word index=8;text=New;		lemma=New;		upos=PROPN;	xpos=NNP;	feats=Number=Sing;									governor=9;	dependency_relation=compound>,
<Word index=9;text=York;	lemma=York;		upos=PROPN;	xpos=NNP;	feats=Number=Sing;									governor=6;	dependency_relation=nmod>
]

[<Word index=1;text=I;		lemma=I;		upos=PRON;	xpos=PRP;	feats=Case=Nom|Number=Sing|Person=1|PronType=Prs;	governor=4;	dependency_relation=nsubj>, 

<Word index=2;text=do;		lemma=do;		upos=AUX;	xpos=VBP;	feats=Mood=Ind|Tense=Pres|VerbForm=Fin;				governor=4;	dependency_relation=aux>, 
<Word index=3;text=n't;		lemma=not;		upos=PART;	xpos=RB;	feats=_;											governor=4;	dependency_relation=advmod>, 
<Word index=4;text=want;	lemma=want;		upos=VERB;	xpos=VB;	feats=VerbForm=Inf;									governor=0;	dependency_relation=root>, 
<Word index=5;text=to;		lemma=to;		upos=PART;	xpos=TO;	feats=_;											governor=6;	dependency_relation=mark>,

<Word index=6;text=order;	lemma=order;	upos=VERB;	xpos=VB;	feats=VerbForm=Inf;									governor=4;	dependency_relation=xcomp>, 

<Word index=7;text=the;		lemma=the;		upos=DET;	xpos=DT;	feats=Definite=Def|PronType=Art;					governor=8;	dependency_relation=det>, 
<Word index=8;text=same;	lemma=same;		upos=ADJ;	xpos=JJ;	feats=Degree=Pos;									governor=6;	dependency_relation=obj>]


ITS IMPORTANT TO FILTER THE PREFIXES AND SUFIXES THAT MAY BE INTRODUCED IN THE UTT,
FOR THAT WE CAN CHECK IF THERE ARE SEVERAL SENTENCES. (IT MAY NOT BE NECCESARY IF WE JUST USE OBJECT + TO BE + VERB)

Algorythim:
    1. Find the token with dependency_relation = obj
    2. Find the words (if there are) which governor number is the index of the object
    3. Those words in the exact same order will be the subject of our phrase
    
    4. place the verb 'to be' with the tense of the verb (root) in the active voice
    5. Use the


ES un poco más dificil de lo imaginado porque no siempre es así, hay veces que hay verbos auxiliares 
como dont o want

i dont want to eat an orange
an orange dont want to be eaten

i eat an orange
an orange is eaten

i dont eat an orange 
an orange is not eaten

i dont want to order the same
the same dont want to be ordered

"""
# Cuarentena SERIA---------------------------------------------------------------------------------------------------------------------------




def activeToPassive(utt, nlp):

    def findDependencyBtWords(index, indexWordsDict, doc, listAux):

        for key in indexWordsDict.keys():
            print("-------------------------------------")
            print(key == index, key, index)
            print("-------------------------------------")
            if str(key) == str(index):
                for value in indexWordsDict[key]:
                    listAux.append(doc.sentences[0].words[int(value)-1])
                    findDependencyBtWords(doc.sentences[0].words[int(value)-1].id, indexWordsDict, doc, listAux)
    #				print("-------------------------------------")
    #				print(key, index, doc.sentences[0].words[int(value)-1])
    #				print("-------------------------------------")
        return []

    def findDirectGovernors(index, indexWordsDict, doc, listAux=None):

        for key in indexWordsDict.keys():
            if str(key) == str(index):
                for value in indexWordsDict[key]:
                    listAux.append(doc.sentences[0].words[int(value)-1])


    prueba = False
    indexObj = -1
    indexRoot = -1
    negative = False
    indexWordsDict = {}


    doc = nlp(utt)
    if prueba == True:
        return str(doc.sentences[0].words) # For examples

    # this par corresponds to the first 3 steps
        # get the index of the object
        # also de dependencies of each word
    # Look at this example (https://github.com/stanfordnlp/stanza/blob/011b6c4831a614439c599fd163a9b40b7c225566/stanza/pipeline/demo/demo_server.py#L46-L48)
    # for mapping stanfordnlp parameters with stanza parameters
    # Properties of a Word in Stanza: https://stanfordnlp.github.io/stanza/data_objects.html#word
    for word in doc.sentences[0].words:
        print(word)
        if not word.head in indexWordsDict.keys():
            indexWordsDict[word.head] = []
        indexWordsDict[word.head].append(word.id) # De esta manera nos quedamos con las palabras relacionadas con el objeto
        if word.deprel == 'obj':
            indexObj = word.id
        elif word.deprel == 'root':
            indexRoot = word.id
        elif word.lemma	== 'not':
            negative = True
    # Collect all the words that depends on the object and sort them
    if not (indexObj == -1 or indexRoot == -1):
        for key in indexWordsDict.keys():
            if str(key) == indexObj:
                wordsRelatedWithObj = []
                for value in indexWordsDict[key]:
                    wordsRelatedWithObj.append(doc.sentences[0].words[int(value)-1])
                    findDependencyBtWords(doc.sentences[0].words[int(value)-1].index, indexWordsDict, doc, wordsRelatedWithObj)
                wordsRelatedWithObj.append(doc.sentences[0].words[int(indexObj)-1])
                uttPassive = [word.text for word in sorted(wordsRelatedWithObj, key=lambda tup: tup.index)]
                print("uttPassive: "+ str(uttPassive))

        # This part correspond to the 4th step
        # get the verb in active voice and the auxiliars of the verb that may have information about the tense of it


        negative = False
        thereIsAux = False
        wordsRelatedWithVerb = []
        isThereTense = doc.sentences[0].words[int(indexRoot)-1].feats.find('Tense')
        findDependencyBtWords(indexRoot, indexWordsDict, doc, wordsRelatedWithVerb)
        if isThereTense != -1:
            feats = doc.sentences[0].words[int(indexRoot)-1].feats
            if [word.feats for word in wordsRelatedWithVerb if (word.lemma).find('not')]:
                negative = True
        else:
            feats = "".join([word.feats for word in wordsRelatedWithVerb if word.feats and word.feats.find('Tense') != -1])
            thereIsAux = True
        print(feats)
        tenseVerb = "".join([feats[6:] for feats in feats.split('|') if feats.find('Tense')!=-1])
        print("\n__________________________________________\n", "tense: ", tenseVerb, "words related with the verb", str([word.lemma for word in wordsRelatedWithVerb]), "\n__________________________________________\n ")



        """
        Conjugations of the verb 'to be'

        Tense: Indicative
        Mood: Present, Preterite, Present Continuous, Present Perfect, Future, 
        Future Perfect, Past Continuous, Past Perfect, Future Continuous, Present 
        perfect continuous, Past perfect continuous, Future perfect continuous
        
        Tense: Imperative
        Tense: Participle Mood: Present, Past
        Tense: Infinitive
        Tense: Perfect Participle

        """
        if thereIsAux: # se pone todos los verbos auxiliares y después verbo to be en el tense que sea, si es infinitivo se añade 'to'
            return utt
        else: # si es negativo sería añadir detrás de la conjugación del verbo be añadir not
            if negative:
                return utt
            return utt

        print("\n*****************\n", conjugate(doc.sentences[0].words[int(indexRoot)-1], tense=PAST+PARTICIPLE, parse=True),"\n*****************\n ")



    # In this case we cannot convert the phrase into passive
    return utt
    #return str([str(doc.sentences[0].tokens), "\n", str(doc.sentences[0])])


def passiveToActive(utt):
    return

# FIN DE CUARENTENA

"""
This function will change all the adjectives of a utt to synonims.
First we have to get all the adjectives that the oration has.
Then we will find a synonim.
We can create as many orations as synonyms are for every adjectives and we can combine them.

"""

def synonyms(term):
    response = requests.get('http://www.thesaurus.com/browse/{}'.format(term))
    soup = BeautifulSoup(response.text, 'html')
    section = soup.findAll('ul')[5] ## I dont think this is such a great idea, i have to see this better
    return [span.text for span in section.findAll('span')]

def antonyms(term):
    response = requests.get('http://www.thesaurus.com/browse/{}'.format(term))
    soup = BeautifulSoup(response.text, 'html')
    section = soup.findAll('ul')[6]
    return [span.text for span in section.findAll('span')]

def convertAdjectivesToSynonyms(utt, percentage, entitiesIndex, nlp): 

    def isAmod(word):

        doc = nlp(str(word))
        for wordAux in doc.sentences[0].words:
#			print(wordAux.upos)
            if wordAux.upos == 'ADJ':
                return True
        return False

    synonymsList = []
    adjIndex = []
    #discountIndex = 1
    utt = utt.split(' ')

    for i, untknWord in enumerate(utt):
#		print(untknWord)
        if isAmod(untknWord) and not i in entitiesIndex:
            synonymsList.append(synonyms(untknWord))
            adjIndex.append(i)

#	print("synonymsList: ", synonymsList)

    if synonymsList:
        if synonymsList[0]:
#			print("adjIndex: ", adjIndex)
            for count, i in enumerate(adjIndex):
                if synonymsList[count]:
                    randomN = randint(0, len(synonymsList[count])-1)
                    changeSin = choices([True, False], [percentage/100, 1-percentage/100])[0]
#					print("randomN: ", randomN, "count: ", count)
#					print("utt: ", utt)
                    if changeSin:
                        utt[i] = synonymsList[count][randomN]

    return " ".join(utt)

def convertAdjectivesToAntonyms(utt, percentage, entitiesIndex, nlp): 

    def isAmod(word):

        doc = nlp(str(word))
        for wordAux in doc.sentences[0].words:
    #		print(wordAux.upos)
            if wordAux.upos == 'ADJ':
                return True
        return False

    antonymsList = []
    adjIndex = []
    #discountIndex = 1
    utt = utt.split(' ')

    for i, untknWord in enumerate(utt):
#		print(untknWord)
        if isAmod(untknWord) and not i in entitiesIndex:
            antonymsList.append(antonyms(untknWord))
            adjIndex.append(i)

#	print("antonymsList: ", antonymsList)

    if antonymsList:
        if antonymsList[0]:
#			print("adjIndex: ", adjIndex)
            for count, i in enumerate(adjIndex):
                if antonymsList[count]:
                    randomN = randint(0, len(antonymsList[count])-1)
                    changeSin = choices([True, False], [percentage/100, 1-percentage/100])[0]
    #				print("randomN: ", randomN, "count: ", count)
    #				print("utt: ", utt)
                    if changeSin:
                        utt[i] = antonymsList[count][randomN] #HAY UN POSIBLE ERROR AQUÍ

    return " ".join(utt)

def convertObjectsToSynonyms(utt, percentage, entitiesIndex, nlp): 

    def isAmod(word):

        doc = nlp(str(word))
        for wordAux in doc.sentences[0].words:
#			print(wordAux.upos)
            if wordAux.upos == 'NOUN':
                return True
        return False

    synonymsList = []
    objIndex = []
    #discountIndex = 1
    utt = utt.split(' ')

    for i, untknWord in enumerate(utt):
        print(untknWord)
        if isAmod(untknWord) and not i in entitiesIndex:
            synonymsList.append(synonyms(untknWord))
            objIndex.append(i)

#	print("synonymsList: ", synonymsList)

    if synonymsList:
        if synonymsList[0]:
#			print("objIndex: ", objIndex)
            for count, i in enumerate(objIndex):
                if synonymsList[count]:
                    randomN = randint(0, len(synonymsList[count])-1)
                    changeSin = choices([True, False], [percentage/100, 1-percentage/100])[0]
    #				print("randomN: ", randomN, "count: ", count)
    #				print("utt: ", utt)
                    if changeSin:
                        utt[i] = synonymsList[count][randomN] #HAY UN POSIBLE ERROR AQUÍ

    return " ".join(utt)

#def convertAdjectivesToSynonyms(utt, entitiesIndex, nlp): #(falla con la frase: Can you pretty please offer me that incredible job, i want to buy a big red car")
#
#	print (dictionary.meaning("indentation"))
#	synonymsList = [] 
#	adjIndex = []
#	discountIndex = 1
#	doc = nlp(utt)
#	utt = utt.split(' ')
#	
#	
#		
#	
#
#	for word in doc.sentences[0].words:
#		print("word: ", word)
#		if '\'' in word.text: #caso de contracciones
#			discountIndex += 1
#
#		if word.dependency_relation == 'amod' and not (int(word.index) in entitiesIndex):
#			inWord = int(word.index) - discountIndex
#			synonymsList.append(synonyms(word.lemma))
#			adjIndex.append(inWord)
#
#	print("synonymsList: ", synonymsList)
#
#	if synonymsList:
#		if synonymsList[0]:
#			print("adjIndex: ", adjIndex)
#			for count, i in enumerate(adjIndex):
#				randomN = randint(0, len(synonymsList[count])-1)
#				print("randomN: ", randomN, "count: ", count)
#				print("utt: ", utt)
#				utt[i] = synonymsList[count][randomN] #HAY UN POSIBLE ERROR AQUÍ
#
#	return " ".join(utt)
#
#
#def convertAdjectivesToAntonyms(utt, entitiesIndex, nlp):
#	antonymsList = [] 
#	adjIndex = []
#	discountIndex = 1
#	doc = nlp(utt)
#	utt = utt.split(' ')
#	for word in doc.sentences[0].words:
#		if '\'' in word.text: #caso de contracciones
#			discountIndex += 1
#		if word.dependency_relation == 'amod' and not (int(word.index) in entitiesIndex):
#			inWord = int(word.index) - discountIndex
#			antonymsList.append(antonyms(word.lemma))
#			adjIndex.append(inWord)
#
#	if antonymsList:
#		if antonymsList[0]:
#			for count, i in enumerate(adjIndex):
#				randomN = randint(0, len(antonymsList[count])-1)
#				utt[i] = antonymsList[count][randomN]
#
#	return " ".join(utt)
#
##### VER AHORA
#def convertObjectsToSynonyms(utt, entitiesIndex, nlp):
#	synonymsList = [] 
#	objIndex = []
#	discountIndex = 1
#	doc = nlp(utt)
#	utt = utt.split(' ')
#	for word in doc.sentences[0].words:
#		if '\'' in word.text: #caso de contracciones
#			discountIndex += 1
#
#		if word.dependency_relation == 'obj' and not (int(word.index) in entitiesIndex):
#			inWord = int(word.index) - discountIndex
#			synonymsList.append(synonyms(word.lemma))
#			objIndex.append(inWord)
#
#	if synonymsList:
#		if synonymsList[0]:
#			for count, i in enumerate(objIndex):
#				randomN = randint(0, len(synonymsList[count])-1)
#				utt[i] = synonymsList[count][randomN]
#
#	return " ".join(utt)



#### futura implementación
#### futura implementación
def convertAdverbsToSynonyms(utt, percentage, entitiesIndex, nlp): 

    def isAmod(word):

        doc = nlp(str(word))
        for wordAux in doc.sentences[0].words:
#			print(wordAux.upos)
            if wordAux.upos == 'ADV':
                return True
        return False

    synonymsList = []
    adjIndex = []
    #discountIndex = 1
    utt = utt.split(' ')

    for i, untknWord in enumerate(utt):
#		print(untknWord)
        if isAmod(untknWord) and not i in entitiesIndex:
            synonymsList.append(synonyms(untknWord))
            adjIndex.append(i)

#	print("synonymsList: ", synonymsList)

    if synonymsList:
        if synonymsList[0]:
#			print("adjIndex: ", adjIndex)
            for count, i in enumerate(adjIndex):
                if synonymsList[count]:
                    randomN = randint(0, len(synonymsList[count])-1)
                    changeSin = choices([True, False], [percentage/100, 1-percentage/100])[0]
#					print("randomN: ", randomN, "count: ", count)
#					print("utt: ", utt)
                    if changeSin:
                        utt[i] = synonymsList[count][randomN] #HAY UN POSIBLE ERROR AQUÍ

    return " ".join(utt)

def convertAdverbsToAntonyms(utt, percentage, entitiesIndex, nlp): 

    def isAmod(word):

        doc = nlp(str(word))
        for wordAux in doc.sentences[0].words:
    #		print(wordAux.upos)
            if wordAux.upos == 'ADV':
                return True
        return False

    antonymsList = []
    adjIndex = []
    #discountIndex = 1
    utt = utt.split(' ')

    for i, untknWord in enumerate(utt):
#		print(untknWord)
        if isAmod(untknWord) and not i in entitiesIndex:
            antonymsList.append(antonyms(untknWord))
            adjIndex.append(i)

#	print("antonymsList: ", antonymsList)

    if antonymsList:
        if antonymsList[0]:
#			print("adjIndex: ", adjIndex)
            for count, i in enumerate(adjIndex):
                if antonymsList[count]:
                    randomN = randint(0, len(antonymsList[count])-1)
                    changeSin = choices([True, False], [percentage/100, 1-percentage/100])[0]
    #				print("randomN: ", randomN, "count: ", count)
    #				print("utt: ", utt)
                    if changeSin:
                        utt[i] = antonymsList[count][randomN] #HAY UN POSIBLE ERROR AQUÍ

    return " ".join(utt)




"""
    We can convert the utterances in many different ways:
        1. Use all the generative functions over the utterance
        2. Use randomly one function over the utterance
        3. We could also give some priority to some phrases
        4. Set a parameter with the functions to use, and another for the probability of using one or another
"""
"""
    changeNumberToWord, changeWordToNumber: We could use both methods in every utt with a probability associated 
    We can upgrade mutateUtterance so it gets the distances of the nearby keys in the keyboard depending on the 
    configuration of the keyboard.

    An interesting thing to do would be to check the effectivity of each method and balance the parameters
WE CAN ACTUALLY CHECK IF THE UTTERANCE CAN BE SYNTACTICALLY MODIFIED:
    IF IT HAS 2 SENTENCES IN THE SAME UTT...

"""

def generateUtterances(functions, chatbot, dirFunction, distribution, parameters=[keyboardQWERTYSpanish, 3, 0, ["de", "pl", "pt"], 2, [0], 50], extension="utterance.txt"):


    def useFunction(utt, function, botDir, parameters, nlp):

        if function == "mutateUtterance":
            return mutateUtterance(utt, botDir, parameters[1], parameters[2])
        elif function == "mutateUtteranceWithDistances":
            return mutateUtteranceWithDistances(utt, botDir, parameters[1], parameters[2], parameters[0])
        elif function == "deleteChars":
            return deleteChars(utt, botDir, parameters[1], parameters[2])
        elif function == "traductionChained":
            return traductionChained(utt, parameters[3])
        elif function == "randomTraductionChained":
            return randomTraductionChained(utt, parameters[4])
        elif function == "changeNumberToWord":
            return changeNumberToWord(utt)
        elif function == "changeWordToNumber":
            return changeWordToNumber(utt)
        elif function == "activeToPassive":
            return activeToPassive(utt, nlp)
        elif function == "convertAdjectivesToSynonyms":
            return convertAdjectivesToSynonyms(utt, parameters[6], parameters[5], nlp)
        elif function == "convertAdjectivesToAntonyms":
            return convertAdjectivesToAntonyms(utt, parameters[6], parameters[5], nlp)
        elif function == "convertObjectsToSynonyms":
            return convertObjectsToSynonyms(utt, parameters[6], parameters[5], nlp)
        elif function == "convertAdverbsToSynonyms":
            return convertAdverbsToSynonyms(utt, parameters[6], parameters[5], nlp)
        elif function == "convertAdverbsToAntonyms":
            return convertAdverbsToAntonyms(utt, parameters[6], parameters[5], nlp)
        else:
            return utt

    botDir = chatbot
    #print("chatbot: ", chatbot)

    inputsAux = getAllUtterancesFromInput(botDir)
    #entityDict = getEntityDict("/home/sergio/Desktop/proyecto/codigo/convosGen/{}/entities/entities.txt".format(chatbot))

    #print("inputsAux: ", inputsAux)
    #stanfordnlp.download('en') ejecutar en la consola para instalar el idioma inglés
    #nlp = stanfordnlp.Pipeline()

    stanza.download('en')
    nlp = stanza.Pipeline('en')

    for inAux in inputsAux:
        generatedUtterances = []
        if inAux:
            print("inAux:", inAux[0], "utts: ", inAux[1:])
            inputFilename = inAux[0] + extension
            firstLine = inAux[0]
            inputUtts = inAux[1:]
            for utt in inputUtts:
                function = choices(functions, distribution)[0]
                generatedUtterances.append(useFunction(utt, function, botDir, parameters, nlp))
            print("Generated Utterances:")
            print(generatedUtterances)
            writeGeneratedUttFile(inputFilename, botDir, dirFunction, firstLine, generatedUtterances)


def get_config_dict(section_name):
    config = configparser.RawConfigParser()
    config.read('./config.cfg')
    if not hasattr(get_config_dict, 'config_dict'):
        get_config_dict.config_dict = dict(config.items(section_name))
    return get_config_dict.config_dict

#	for utt in inputUtts:
#		print(utt)
#		print(mutateUtterance(utt, 2, 10), "\n______________________________________\n")

if __name__ == "__main__":

    config = configparser.RawConfigParser()
    config.read('./config.cfg')
    config_details = get_config_dict('project')

    # RuntimeError: index_select(): Expected dtype int32 or int64 for index
    # convertObjectsToSynonyms, convertAdjectivesToAntonyms, "activeToPassive", convertAdjectivesToSynonyms
    # Issue on GitHub: https://github.com/stanfordnlp/stanfordnlp/issues/6 (They say that
    # stanfordnlp is out of date, and to use stanza (https://github.com/stanfordnlp/stanza)

    # generateUtterances(["mutateUtterance", "mutateUtteranceWithDistances", "deleteChars", "changeNumberToWord", "changeWordToNumber",
	# 			"activeToPassive", "convertAdjectivesToSynonyms", "convertAdjectivesToAntonyms", "convertObjectsToSynonyms", "convertAdverbsToSynonyms", "convertAdverbsToAntonyms", "noMutation"],
	# 				    config_details['chatbot_to_test'],
    #                     "",
    #                     [1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1, 1])

    generateUtterances(["mutateUtterance", "mutateUtteranceWithDistances", "deleteChars", "traductionChained", "randomTraductionChained", "changeNumberToWord", "changeWordToNumber",
	 			"activeToPassive", "convertAdjectivesToSynonyms", "convertAdjectivesToAntonyms", "convertObjectsToSynonyms", "convertAdverbsToSynonyms", "convertAdverbsToAntonyms", "noMutation"],
	 				    config_details['chatbot_to_test'],
                         "",
                         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])