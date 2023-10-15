from os import listdir, makedirs, remove
from os.path import isfile, join, exists, dirname, abspath
import json
from itertools import combinations, product
from random import choice, sample
from re import sub
from shutil import copy
from time import sleep
import configparser
import sys

"""
We are going to try to get all the convos of a chatbot in order to get botium results

In order to do that we have to generate 3 types of files:
    
    1. convo files

    2. Utterance input files

    3. Utterance output files

First, We need to get all the entities of the chatbot and store them into a dictionary

Second, we need to create a dependency dictionary with the context dependencies between all the intents.

With the dict created, we can create the convo file of each intent (First the ones that have no dependency, 
    later the ones that depend directly from the ones menctioned before and so on)

It is important to have into acc that some of the intents have required entities, if so, we will divide the convo 
into different files (one for each required entity), following the paths that the intent can have  
        P.D. if there are more than two req ent, then it will ask for the first and then the second, 
        we can respond with both entities required at the same time
We can create a list of required random items and place them in the convo so it continues the flow of the conversation.

Problem, if any systemunit is required we have to define what is systemUnits (there is probably a library for that) 
    we can set a default value for each sys.arg or try to get a random value of the library each time we need it


"""

"""
getEntities obtiene el nombre y los valores de todas las entidades de un chatbot, de esta manera, luego podemos saber 
los entities para no mutarlos en las frases
"""
def getEntities(dirPath):	

    entityDict = {}

    entInfoFiles = [join(dirPath,f) for f in listdir(dirPath) if isfile(join(dirPath, f)) and not f[-16:-5] == '_entries_en']
    entValFiles = [join(dirPath,f) for f in listdir(dirPath) if isfile(join(dirPath, f)) and f[-16:-5] == '_entries_en']

    for entInfo in entInfoFiles:
        with open(entInfo) as file:
            entInfoDict = json.load(file)

    for entVal in entValFiles:
        with open(entVal) as file:
            entValDict = json.load(file)
            entValName = entVal.split('/')[-1]
            entityDict[entValName[:-16]] = []
            for entValAux in entValDict:
                #print(entVal['synonyms'])
                entityDict[entValName[:-16]].append(entValAux['synonyms'])
            #for entVal in entValDict:
            #	entityDict[entInfoDict['name']].append(entVal['synonyms'])

    return entityDict

"""
getIntents obtiene la información de los intents de un chatbot, se pueden obtener los contextos, parámetros respuestas....
"""
def getIntents(dirPath):
    intentDict = {}
    intInfoFiles = [join(dirPath, f) for f in listdir(dirPath) if isfile(join(dirPath, f)) and not f[-17:-5] == '_usersays_en']

    for intInfo in intInfoFiles:
        with open(intInfo) as file:
            intInfoData = json.load(file)
            if isinstance(intInfoData, list):  # Check if the data is a list
                for intInfoDict in intInfoData:
                    if 'name' in intInfoDict:  # Check if 'name' is a key in the dictionary
                        intentDict[intInfoDict['name']] = intInfoDict
            elif isinstance(intInfoData, dict):  # Check if the data is a dictionary
                if 'name' in intInfoData:  # Check if 'name' is a key in the dictionary
                    intentDict[intInfoData['name']] = intInfoData

    return intentDict

def getIntentUtterances(dirPath, intent, nTrainingUtterances):

    utts = []
    intentUtteranceFiles = [join(dirPath,f) for f in listdir(dirPath) if isfile(join(dirPath, f)) and f[:-5] == intent+'_usersays_en']

    for intUtt in intentUtteranceFiles:
        with open(intUtt) as file:
            intUttsDict = json.load(file)
            #print(intInfoDict['name'].replace(' ', ''))
            for utt in intUttsDict:
                uttAux = []
                aliasList = []
                #print("\n*********************\n")
                for textInstance in utt['data']:
                #	print("\n\n________________________\n", textInstance)
                    if "alias" in textInstance.keys():
                #		print(textInstance['alias'])
                        aliasList.append(textInstance['alias'])
                    uttAux.append(textInstance['text'])
                #print(("".join(uttAux), aliasList))
                utts.append(("".join(uttAux), aliasList))

    if nTrainingUtterances < len(utts):
        return sample(utts, nTrainingUtterances)
    else:
        return utts

def getEntitiesCombWords(entityDict):
    entityCombDict = {}
    def getCombWords(entityDictEntry):
        combinations = []
        for word in entityDictEntry:
            for synonym in word:
                nWords = len(synonym.split())

                if not nWords in combinations:
                    combinations.append(nWords)
        return combinations
    for entityKey in entityDict.keys():
        entityCombDict[entityKey] = getCombWords(entityDict[entityKey])
    return entityCombDict

def writeEntityFile(directory, entityDict):
    print(directory)
    if not exists(directory):
        makedirs(directory)
    fileDir = join(directory, "entities.txt")
    entityDictJson = json.dumps(entityDict)
    f=open(fileDir, "w+")
    f.write(entityDictJson)
    f.close()

def getDependenciesRec(intentDict, intentKey, affectedContext, contextDependencyDict):
    if intentKey in contextDependencyDict:
        return contextDependencyDict  # Already processed this intent, return

    contextDependencyDict[intentKey] = []  # Initialize the intent's dependency list

    for nextIntentKey in intentDict.keys():
        if 'parentId' in intentDict[nextIntentKey] and intentDict[nextIntentKey]['parentId'] == intentKey:
            if 'responses' in intentDict[nextIntentKey] and intentDict[nextIntentKey]['responses']:
                affectedContexts = intentDict[nextIntentKey]['responses'][0].get('affectedContexts', [])
                for affectedContextsAux in affectedContexts:
                    if affectedContextsAux['name'] == affectedContext:
                        contextDependencyDict[intentKey].append(nextIntentKey)
                        getDependenciesRec(intentDict, nextIntentKey, affectedContext, contextDependencyDict)

    return contextDependencyDict

def getDependencies(intentDict):
    contextDependencyDict = {}

    for intentKey in intentDict.keys():
        if 'parentId' not in intentDict[intentKey]:
            getDependenciesRec(intentDict, intentKey, '', contextDependencyDict)  # Start the recursion from top-level intents

    return contextDependencyDict



def walkOverDependencies(intentDict, dependenciesDict, entityDict, entityCombDict, chatbot, nTrainingUtterances=0): #CORREGIR



    for intentParent in dependenciesDict.keys():
        generateConvos(intentDict, intentParent, entityDict, chatbot, nTrainingUtterances)
        if dependenciesDict[intentParent]:
            for dependency in dependenciesDict[intentParent]:
                walkOverDependencies(intentDict, dependency, entityDict, entityCombDict, chatbot, nTrainingUtterances)


    return
# we have to check if there is any required parameter. If so, divide the training phrases into 2 sets, 
# and treat them as two diferent convo files.


# Function: generateConvos
# Purpose: Generate conversation files based on intent, required parameters, and utterances.
# Input:
# - intentDict: A dictionary containing information about intents.
# - intent: The specific intent to generate conversations for.
# - entityDict: A dictionary containing entity values.
# - chatbot: The chatbot identifier.
# - nTrainingUtterances: Number of training utterances to consider.
# Output:
# - Generates conversation files based on the provided input.
def generateConvos(intentDict, intent, entityDict, chatbot, nTrainingUtterances):

    # Define a function to check required entities and collect them
    def checkRequiredEntities(intentDict, intent):
        requiredParams = {}
        for parameter in intentDict[intent]['responses'][0]['parameters']:
            if parameter['required']:
                requiredParams[parameter['name']] = parameter
        return requiredParams

    # Define a function to check if an intent has a parent context
    def checkContext(intentDict, intent):
        if "parentId" in intentDict[intent].keys():
            return True
        return False

    #print("\n", intentDict[intent]["name"])
    # Get the name of the intent
    intentName = intentDict[intent]["name"]

    # Get training utterances for the intent
    #Estas uterances están en forma de listas de listas de tuplas
    utterances = getIntentUtterances(config_details['root_project_dir'] + "/chatbots/{}/intents".format(chatbot), intent, nTrainingUtterances)

    # Check and collect required parameters for the intent
    requiredParams = checkRequiredEntities(intentDict, intent)

    # Define the directory for conversation files
    dirAux="../convosGen/{}".format(chatbot)

    # Create the directory if it doesn't exist
    if not exists(dirAux):
        makedirs(dirAux)
    #uttOutputFile= dirAux+"/"+intentName.replace(' ', '')+"_output.utterances.txt"

    # Initialize variables
    splittedUtterances=[]
    i=0
    tokensRemoved = [' ', '_']

    # If there are required parameters
    if requiredParams:
        #Obtenemos las conversaciones parciales que nos servirán para aquellas frases que no cuenten con los parámetros requeridos.
        
        # Obtain partial conversations for missing parameters
        pconvosParams = getPConvosRequired(requiredParams, entityDict, intentName, dirAux)
        combConvos = getConvosCombinations(requiredParams)
        #print("\n*************************\n\n", combConvos)
        splittedUtterances = splitUtterances(combConvos, requiredParams, intentDict[intent], utterances, entityDict)
        #print(splittedUtterances)
        # para cada combinacion de parámetros que falten, haremos una conversación diferente en caso de que tengan utterances correspondientes.
        # Si no hay se salta el proceso para dicha combinación

        #En caso de tener contexto, debemos asegurarnos de que el contexto contenga frases de entrenamiento, sino, este caso de prueba puede fallar

        for comb in combConvos:
            uttInputFile= dirAux+"/"+''.join(i for i in intentName if not i in tokensRemoved)+"_"+str(i)+"_input.utterances.txt"
            convoFile= dirAux+"/"+''.join(i for i in intentName if not i in tokensRemoved)+"_"+str(i)+".convo.txt"
            if splittedUtterances[str(comb)]:
                writeHeader(convoFile, intentName, str(i)) #Escribimos la cabecera del fichero
                # Vemos si existe contexto en la conversación
                if checkContext(intentDict, intent):
                    #print("Tiene contexto")
                    print("Caso 2 soy casen:", caseN)

                    caseN = checkContextCase(intentDict, dirAux, intentDict[intent]["parentId"])
                    writeInclude(convoFile, includeConvoFromContext(intentDict, intentDict[intent]["parentId"], str(caseN), chatbot))
                writeUserSentence(convoFile, intentName, str(i))
                for paramRequired in comb:
                    writePConvos(convoFile, pconvosParams[paramRequired])
                writeBotResponse(convoFile, intentName)
                writeUttInputFile(uttInputFile, intentName, str(i), splittedUtterances[str(comb)])
                i += 1
                #print(comb, "\n")
                #print(pconvosParams[comb[0]], "\n")
                #print("\n",str(combConvos[0]))
            else:
                writeNoTrainingPhrases(convoFile, intentName, str(i))
                i += 1
    else:
        i=0

        uttInputFile= dirAux+"/"+''.join(i for i in intentName if not i in tokensRemoved)+"_"+str(i)+"_input.utterances.txt"
        convoFile= dirAux+"/"+''.join(i for i in intentName if not i in tokensRemoved)+"_"+str(i)+".convo.txt"
        if utterances:
            writeHeader(convoFile, intentName, str(i)) #Escribimos la cabecera del fichero
            # Vemos si existe contexto en la conversación
            if checkContext(intentDict, intent):
                #print("Tiene contexto")
                caseN = checkContextCase(intentDict, dirAux, intentDict[intent]["parentId"])
                writeInclude(convoFile, includeConvoFromContext(intentDict, intentDict[intent]["parentId"], str(caseN), chatbot))
            writeUserSentence(convoFile, intentName, str(i))
            writeBotResponse(convoFile, intentName)
            writeUttInputFile(uttInputFile, intentName, str(i), utterances)
        else:
            writeNoTrainingPhrases(convoFile, intentName, str(i))

    uttOutputFile= dirAux+"/"+''.join(i for i in intentName if not i in tokensRemoved)+"_output.utterances.txt"

    outputUtterances = getOutputUtterances(intentDict[intent], entityCombDict)
    writeOutputFile(uttOutputFile, intentName, outputUtterances)
    #print("________________________________________")
        #for reqParam in requiredParams:

        #	writeConvoFile(intentDict[intent]["name"], str(i))
        #	i += 1
    # output ya con todos los requirements
    # writeConvoFile(intentDict[intent]["name"], str(i))


    

# Function: splitUtterances
# Purpose: Split utterances into combinations based on required parameters and conditions.
# Input:
# - combConvos: List of combinations of required parameters.
# - requiredParams: A dictionary of required parameters and their associated prompts.
# - intentEntry: An entry related to the intent.
# - utterances: A list of utterances.
# - entityDict: A dictionary containing entity values.
# Output:
# - Returns a dictionary with combinations of utterances based on required parameters and conditions.

def splitUtterances(combConvos, requiredParams, intentEntry, utterances, entityDict):
    # Define a function to check if an utterance matches the conditions for a combination
    def checkUttInCombination(comb, utt, requiredParams):
        # Check that no parameter from the combination is included in the utterance
        for combParam in comb:
            if combParam in utt[1]:
                return False

        # Check that all required parameters (excluding those in the combination) are present in the utterance
        for combParam in comb:
            requiredParams.remove(combParam)
        for reqParam in requiredParams:
            if reqParam not in utt[1]:
                return False
        return True

    combinationsUtts = {}
    # Append an empty combination to handle cases without required parameters
    combConvos.append([])

    # Iterate through each combination of parameters
    for comb in combConvos:
        uttsComb = []
        for utt in utterances:
            # Check if the utterance matches the conditions for the combination
            if checkUttInCombination(comb, utt, list(requiredParams.keys())):
                uttsComb.append(utt)
        # Store the combination and its associated utterances in the dictionary
        combinationsUtts[str(comb)] = uttsComb

    return combinationsUtts


# Function: includeConvoFromContext
# Purpose: Include a conversation from a specified context in a chatbot project.
# Input:
# - intentDict: A dictionary containing information about intents.
# - parentId: The identifier of the parent intent.
# - i: A string identifier.
# - chatbot: The chatbot identifier.
# Output:
# - Returns the content of the conversation associated with the specified context.

def includeConvoFromContext(intentDict, parentId, i, chatbot):
    # Check if 'i' is less than 0, and if so, return to avoid unwanted cases
    if int(i) < 0:
        return

    # Define characters to be removed from intent names
    tokensRemoved = [' ', '_']
    print("HOLA soi i", i)

    # Loop through intentDict to find the intent with the matching parent identifier
    for intent in intentDict.keys():
        if intentDict[intent]['id'] == parentId:
            # Generate the file path based on chatbot, intent, and 'i'
            file = config_details['root_project_dir'] + "/proyecto/codigo/convosGen/{}".format(chatbot) + "/" + \
                ''.join(i for i in intent if not i in tokensRemoved) + "_" + i + ".convo.txt"
            print(file)
            
            # Open and read the content of the file
            f = open(file, "r")
            if f.mode == 'r':
                content = f.readlines()
            # Extract the conversation content, excluding the first line
            pconvo = content[1:]
            # Note: The 'pconvo' variable is overwritten in each loop iteration; consider appending if necessary
    return pconvo


def checkContextCase(intentDict, dirAux, parentId):
    i = 0
    for intent in intentDict.keys():
        if intentDict[intent]['id'] == parentId:
            parentIntentName = intent
    # print(parentIntentName)
    parentIntentConvos = [join(dirAux,f) for f in listdir(dirAux) if isfile(join(dirAux, f)) and f[:-12] == parentIntentName and f[-10:] == ".convo.txt"]
    parentIntentConvos.sort()
    for convoDir in parentIntentConvos:

        f=open(convoDir, "r")
        if f.mode == 'r':
            content=f.readlines()
        #If there is no convo in this file, we skip this one
        if content[0] == 'There are no training phrases for this case, please complete your training set':
            i+=1
        #Else, we return the numberr oof the case
        else:
            return i
    #if not utterances
    return -1
#	for case in splittedUtterances.keys():
#		
#		if splittedUtterances[case]:
#
#			print("Caso 000000")
#			print(i)
#			return i
#		print("\n\n\n\n\n\n\n\n", i)
#		i += 1
#	return -1


# Function: getParamValue
# Purpose: Extract a parameter value from the provided entity dictionary.
# Input:
# - reqParam: The parameter for which to retrieve a value.
# - entityDict: A dictionary containing entity values.
# Output:
# - Returns the extracted parameter value.

def getParamValue(reqParam, entityDict):
     # Check if the parameter exists in the entity dictionary
    if reqParam in entityDict: 
        paramValues = entityDict[reqParam]
        # Check if there are values associated with the parameter
        if paramValues: 
            if isinstance(paramValues[0], dict):
                # Extract the first prompt value from a dictionary structure (if present)
                firstPromptValue = paramValues[0]["prompts"][0]["value"] if paramValues[0].get("prompts") else ""
            # If not a dictionary, initialize it as an empty string
            else:
                firstPromptValue = "" 
            # If the first prompt value starts with '@', recursively extract its value
            if firstPromptValue and firstPromptValue[0] == "@":
                
                firstPromptValue = getParamValue(firstPromptValue[1:], entityDict)

            paramValue = firstPromptValue
        # If there are no values associated with the parameter
        else:
            paramValue = ""  
    # If the parameter doesn't exist in the entity dictionary
    else:
        paramValue = "!REQUIRED_PARAMETER"  
    return paramValue
    

# Function: getPConvosRequired
# Purpose: Generate conversation parameters by extracting values from an entity dictionary.
# Input:
# - requiredParams: A dictionary of required parameters and their associated prompts.
# - entityDict: A dictionary containing entity values.
# - intentName: The name of the intent related to the conversation.
# - dirAux: The directory where prompts files are to be created.
# Output:
# - Returns a dictionary of conversation parameters.

def getPConvosRequired(requiredParams, entityDict, intentName, dirAux):
    # Initialize a dictionary to store conversation parameters
    pconvosParams = {}
    # Define characters to be removed from the intentName
    tokensRemoved = [' ', '_']
    # Remove spaces and underscores from intentName
    intentNamecleared = ''.join(i for i in intentName if not i in tokensRemoved)
    
    # Loop through required parameters
    for reqParam in requiredParams.keys():
        # Get the value of the parameter from entityDict
        paramValue = getParamValue(reqParam, entityDict)
        # Construct a header for the parameter
        reqParamHeader = intentNamecleared + reqParam
        # Call the writeReqParamPrompts function to write prompts to a file
        writeReqParamPrompts(dirAux, reqParamHeader, requiredParams[reqParam].get("prompts", []))
        # Store the parameter and its value in the pconvosParams dictionary
        pconvosParams[reqParam] = "\n#bot\n"+reqParamHeader+"\nINTENT "+intentName+"\n\n#me\n"+paramValue+"\n"

    return pconvosParams



# Function: writeReqParamPrompts
# Purpose: Write prompts to a file associated with a specific parameter.
# Input:
# - dirAux: The directory where the prompts file should be created.
# - reqParamHeader: A unique header for the prompts file.
# - prompts: A list of prompts to be written to the file.
# Output:
# - Creates a prompts file with the specified prompts in the given directory.

def writeReqParamPrompts(dirAux, reqParamHeader, prompts):
    # Define characters to be removed from the parameter header
    tokensRemoved = [' ', '_']
    # Construct a header for the prompts file
    header = reqParamHeader + "\n"
    # Generate the filename for the prompts file
    reqParamFilename = join(dirAux, reqParamHeader)
    reqParamFilename = reqParamFilename + ".utterances.txt"

    # Open the prompts file and write prompts to it
    f = open(reqParamFilename, "w+")
    f.write(header)
    for prompt in prompts:
        f.write(prompt.get("value", "") + "\n")


# Function: getConvosCombinations
# Input:
# - requiredParams: A list of parameters for which combinations need to be generated.
# Output:
# - A list of parameter combinations.

def getConvosCombinations(requiredParams):
    # Initialize a list to store parameter combinations
    combConvos = []

    # Generate combinations of required parameters
    for L in range(0, len(requiredParams) + 1):
        for subset in combinations(requiredParams, L):
            combConvos.append([x for x in subset if x != ","])

    # Filter out empty lists and return the parameter combinations
    return [x for x in combConvos if x != []]


"""
[[['$size0']], [['$snack0'], ['$snack0', '$snack1'], ['$snack0', '$snack1', '$snack2']], [['$deliverypickup0', '$deliverypickup1'], ['$deliverypickup0']]]

Las combinaciones posibles son:


"""

def getOutputVariablesCombinations(variablesCombinations):

    combOutputVariables = []

    for L in range(0, len(variablesCombinations)+1):
        for subset in combinations(variablesCombinations, L):
            combOutputVariables.append([x for x in subset if x != ","])
    return [x for x in combOutputVariables if x != []]


# 1. Comprobamos cuantas combinaciones de numero de palabras tiene como máximo la entidad a ver
# 2. Tenemos que hacer tantas frases como combinaciones posible haya 
#    entidad $drink (coffee, hot chocolate)
#	 ejemplo de respuesta: do you want $drink? tenemos que separar en: do you want $drink1? do you want $drink1 $drink2?

def getOutputUtterances(intentDictEntry, entityCombDict):

    def checkWordIsVar(word):
        if word[0] == '$':
            return True
        return False

    def checkVariables(word):

        if word[0] == '$':
            lenEntry = [len(key) for key in entityCombDict.keys() if key in word[0:]] # this works if entities names are only letters of the dictionary
            if len(lenEntry) == 1:
                combs = entityCombDict[word[1:lenEntry[0]+1]]
                #print(word[1:lenEntry[0]+1], "\n", combs)

                combWords = []
                for comb in combs:
                    words = []
                    for i in range(0, comb):
                        words.append('$'+sub('[\W_]+', '', word)+str(i))
                    combWords.append(words)
                #print(combWords)
                return combWords
            else:
                #print(entityCombDict)
                print("hay diversas entradas que comparten la misma cadena para: ", word)
                return []
        else:
            return []

    # first we have to check all the combinations posibles


    outputUtterances = []
    for msg in intentDictEntry["responses"][0]["messages"]:
        if msg["type"] == 0:
            if isinstance(msg["speech"], list):
                for msgText in msg["speech"]:
                    variablesCombinations = []
                    msgText = msgText.split()
                    for i, word in enumerate(msgText):
                        listCombs = checkVariables(word)
                        #print(listCombs)
                        if listCombs:
                            variablesCombinations.append(listCombs)

                    # Now we have to make all possible combinations
                    #print("\n_____________________________________________________\n", variablesCombinations, "\n\n")


                    variablesCombinations = list(product(*variablesCombinations))
                    #if variablesCombinations:
                    #	variablesCombinations = getOutputVariablesCombinations(variablesCombinations)
                    if variablesCombinations:
                        for varComb in variablesCombinations:
                            nVar=0
                            #
                            (varComb)
                            for i, word in enumerate(msgText):
                                if checkWordIsVar(word):
                                    #
                                    (word, varComb[nVar])
                                    msgText[i] = ' '.join(varComb[nVar])
                                    nVar += 1
                            outputUtterances.append(' '.join(msgText))

            else:
                outputUtterances.append(msg["speech"])

    return outputUtterances

def writeNoTrainingPhrases(convoFile, intentName, i):
    f=open(convoFile, "w+")
    f.write("There are no training phrases for this case, please complete your training set")

def writeHeader(convoFile, intentName, i):

    tokensRemoved = [' ', '_']

    header=''.join(i for i in intentName if not i in tokensRemoved)+"_"+i+"\n"
    f=open(convoFile, "w+")
    f.write(header)

def writeInclude(convoFilename, include):
    with open(convoFilename, "a") as convoFile:  # Open the file in append mode
        if include is not None:
            for line in include:
                convoFile.write(line + '\n')


def writeUserSentence(convoFile, intentName, i):
    tokensRemoved = [' ', '_']
    convo="\n#me\n"+''.join(i for i in intentName if not i in tokensRemoved)+"_"+i+"_input\n"
    f=open(convoFile, "a")
    f.write(convo)

def writePConvos(convoFile, pcomb):
    f = open(convoFile, "a")
    f.write(pcomb)


def writeBotResponse(convoFile, intentName):
    tokensRemoved = [' ', '_']
    convo="\n#bot\n"+''.join(i for i in intentName if not i in tokensRemoved)+"_output\nINTENT "+intentName+"\n"
    f=open(convoFile, "a")
    f.write(convo)

def writeUttInputFile(uttFile, intentName, i, splittedUtterances):
    tokensRemoved = [' ', '_']
    header=''.join(i for i in intentName if not i in tokensRemoved)+"_"+i+"_input\n"
    f=open(uttFile, "w+")
    f.write(header)
    for utt in splittedUtterances:
        f.write(utt[0]+"\n")


def writeConvoFile(convoFile, intentName, i, header=False):

    tokensRemoved = [' ', '_']
    convo="\n#me\n"+''.join(i for i in intentName if not i in tokensRemoved)+"_"+i+"_input\n\n#bot\n"+''.join(i for i in intentName if not i in tokensRemoved)+"_output\n"
    f=open(convoFile, "a")
    f.write(convo)

def writeOutputFile(outputFile, intentName, outputUtterances):

    tokensRemoved = [' ', '_']
    header=''.join(i for i in intentName if not i in tokensRemoved)+"_output\n"
    f=open(outputFile, "w+")
    f.write(header)
    for utt in outputUtterances:

        f.write(utt+"\n")


def printDependencies(dependenciesDict):

    def printDependenciesRec(dependenciesDict, i):
        for dependency in dependenciesDict.keys():
            if i==0:
                print("i=0: ", dependency)
            elif i==1:
                print("\n\ti=1: ", dependency)
            elif i==2:
                print("\n\t\ti=2: ", dependency)
            elif i==3:
                print("\n\t\t\ti=3: ", dependency)
            else:
                print("\n\t\t\t\ti>3: ", dependency)
            for dependenciesDictAux in dependenciesDict[dependency]:
                printDependenciesRec(dependenciesDictAux, i+1)

    for dependency in dependenciesDict.keys():
        print("i=0: ", dependency)
        for dependenciesDictAux in dependenciesDict[dependency]:
            printDependenciesRec(dependenciesDictAux, 1)
        print("\n_____________________________________________________\n")



def separateConvosByIntents(dependenciesDict, convosDir, removeFiles):
    tokensRemoved = [' ', '_']

    def separateConvosByIntentsRec(dependenciesDict, intentDir, intentFiles):
        tokensRemoved = [' ', '_']

        for dependency in dependenciesDict.keys():
            newIntentDir=convosDir+"/"+''.join(i for i in dependency if not i in tokensRemoved)
            if not exists(newIntentDir):
                makedirs(newIntentDir)
            for f in intentFiles:
                copy(f, newIntentDir)
            removeFiles = [join(newIntentDir,f) for f in listdir(newIntentDir) if isfile(join(newIntentDir, f)) and f[-9:] == "convo.txt"]
            for f in removeFiles:
                remove(f)
 #			# 4. Copy all the input and output files into the intent Dir
            intentFiles = [join(convosDir,f) for f in listdir(convosDir) if isfile(join(convosDir, f)) and ''.join(i for i in dependency if not i in tokensRemoved)+"_" in f]
 #			#print(intentFiles, "\n")
            for f in intentFiles:
                copy(f, newIntentDir)
 #			# 5. keep running through the tree of dependencies
            # Get all the files in the directory and pass them
            intentFiles = [join(newIntentDir,f) for f in listdir(newIntentDir) if isfile(join(newIntentDir, f))]

            for dependenciesDictAux in dependenciesDict[dependency]:
                separateConvosByIntentsRec(dependenciesDictAux, newIntentDir, intentFiles)

    for dependency in dependenciesDict.keys():
        # 1. MAKE A DIRECTORY INSIDE WITH THE NAME OF THE INTENT
        intentDir = convosDir+"/"+''.join(i for i in dependency if not i in tokensRemoved)
        if not exists(intentDir):
            makedirs(intentDir)

        # 2. We copy the convos, inputs, and outputs starting with the same name to it
        intentFiles = [join(convosDir,f) for f in listdir(convosDir) if isfile(join(convosDir, f)) and ''.join(i for i in dependency if not i in tokensRemoved)+"_" in f]
        #print("\n________________________________________________________________\n\n", intentFiles)
        for f in intentFiles:
            copy(f, intentDir)
        # 3. We call the recursive with the kids of the root
        for dependenciesDictAux in dependenciesDict[dependency]:
            separateConvosByIntentsRec(dependenciesDictAux, intentDir, intentFiles)

    if removeFiles:
        intentFiles = [join(convosDir,f) for f in listdir(convosDir) if isfile(join(convosDir, f)) and f[-3:] == "txt"]
        for f in intentFiles:
            remove(f)

def get_config_dict(section_name):
    if not hasattr(get_config_dict, 'config_dict'):
        get_config_dict.config_dict = dict(config.items(section_name))
    return get_config_dict.config_dict

if __name__ == "__main__":

    chatbots = ["Currency-Converter","News","RoomReservation","ecommerce", "Weather-bot", "AppointmentScheduler-GoogleCalendar","Temperature-converter"]
    nTrainingUtterances = [10,10,10,10,10,10,10]
    i=0

    config = configparser.RawConfigParser()
    config.read('./config.cfg')
    config_details = get_config_dict('project')

    for chatbot in chatbots:

        if chatbot == "Coffee-Shop":
            separateConvosByIntentsFlag = 0
        else:
            separateConvosByIntentsFlag = 0

        entityDir = config_details['root_project_dir'] + "/chatbots/{}/entities".format(chatbot)
        if exists(entityDir):

            entityDict = getEntities(entityDir)
#			for key in entityDict.keys():
#				print(key, entityDict[key], "\n\n")
        else:
            entityDict = {}
            #getEntities("/home/sergio/Escritorio/chatbots/viberSampleNutrition/entities") fin de cuarentena
        #writeEntityFile("/home/sergio/Desktop/proyecto/codigo/convosGen/{}/entities".format(chatbot), entityDict)
        entityCombDict = getEntitiesCombWords(entityDict)
        #print(entityCombDict)

        intentDict = getIntents(config_details['root_project_dir'] + "/chatbots/{}/intents".format(chatbot))
        #getIntents("/home/sergio/Escritorio/chatbots/viberSampleNutrition/intents") fin de cuarentena
        #for intent in intentDict.keys():
        #	print("\n\n\n\n", intentDict[intent])
        dependenciesDict = getDependencies(intentDict)

        printDependencies(dependenciesDict)

        walkOverDependencies(intentDict, dependenciesDict, entityDict, entityCombDict, chatbot, nTrainingUtterances[i])
        i += 1

        if separateConvosByIntentsFlag == 1:
            separateConvosByIntents(dependenciesDict, config_details['root_project_dir'] + "/proyecto/codigo/convosGen/{}".format(chatbot), True)
