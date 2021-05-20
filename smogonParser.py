import json, requests, os, re, collections, pickle, errno, jsonpickle, datetime, sys
import urllib.request
import numpy as np

import movesetParser as mvparser
from bs4 import BeautifulSoup
try:
    import readline
except ImportError:
    import pyreadline as readline

pokedex = []
movedex = []
modes = []
speciesLookup = {}
weaknesses_dict = {"Normal": np.array([1, 2, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]), "Fighting": np.array([1, 1, 2, 1, 1, 0.5, 0.5, 1, 1, 1, 1, 1, 1, 2, 1, 1, 0.5, 2]), "Flying": np.array([1, 0.5, 1, 1, 0, 2, 0.5, 1, 1, 1, 1, 0.5, 2, 1, 2, 1, 1, 1]), "Poison": np.array([1, 0.5, 1, 0.5, 2, 1, 0.5, 1, 1, 1, 1, 0.5, 1, 2, 1, 1, 1, 0.5]), "Ground": np.array([1, 1, 1, 0.5, 1, 0.5, 1, 1, 1, 1, 2, 2, 0, 1, 2, 1, 1, 1]), "Rock": np.array([0.5, 2, 0.5, 0.5, 2, 1, 1, 1, 2, 0.5, 2, 2, 1, 1, 1, 1, 1, 1]), "Bug": np.array([1, 0.5, 2, 1, 0.5, 2, 1, 1, 1, 2, 1, 0.5, 1, 1, 1, 1, 1, 1]), "Ghost": np.array([0, 0, 1, 0.5, 1, 1, 0.5, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1]), "Steel": np.array([0.5, 2, 0.5, 0, 2, 0.5, 0.5, 1, 0.5, 2, 1, 0.5, 1, 0.5, 0.5, 0.5, 1, 0.5]), "Fire": np.array([1, 1, 1, 1, 2, 2, 0.5, 1, 0.5, 0.5, 2, 0.5, 1, 1, 0.5, 1, 1, 0.5]), "Water": np.array([1, 1, 1, 1, 1, 1, 1, 1, 0.5, 0.5, 0.5, 2, 2, 1, 0.5, 1, 1, 1]), "Grass": np.array([1, 1, 2, 2, 0.5, 1, 2, 1, 1, 2, 0.5, 0.5, 0.5, 1, 2, 1, 1, 1]), "Electric": np.array([1, 1, 0.5, 1, 2, 1, 1, 1, 0.5, 1, 1, 1, 0.5, 1, 1, 1, 1, 1]), "Psychic": np.array([1, 0.5, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 0.5, 1, 1, 2, 1]), "Ice": np.array([1, 2, 1, 1, 1, 2, 1, 1, 2, 2, 1, 1, 1, 1, 0.5, 1, 1, 1]), "Dragon": np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 0.5, 0.5, 0.5, 1, 2, 2, 1, 2]), "Dark": np.array([1, 2, 1, 1, 1, 1, 2, 0.5, 1, 1, 1, 1, 1, 0, 1, 1, 0.5, 2]), "Fairy": np.array([1, 0.5, 1, 2, 1, 1, 0.5, 1, 2, 1, 1, 1, 1, 1, 1, 0, 0.5, 1])}

dexFolder = [ f.path for f in os.scandir(os.getcwd()) if ( f.is_dir() and f.name == "dex") ]
print(dexFolder)

with open(os.path.join(dexFolder[0], "moves-min.json"), 'r') as file:
    movedex = json.load(file)
with open(os.path.join(dexFolder[0], "pokedex.json"), 'r') as file:
    pokedex = json.load(file)
with open(os.path.join(dexFolder[0], "species-lookup.json"), 'r') as file:
    speciesLookup = json.load(file)

#Parser exclusive
pokemans_dict = {}
teammatesUsage = {}

resistances_dict = {}

#https://stackoverflow.com/questions/7821661/how-to-code-autocompletion-in-python
class AutoCompleter(object):  # Custom completer

    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options 
                                    if s and s.startswith(text)]
            else:  # no text entered, all matches possible
                self.matches = self.options[:]

        # return match indexed by state
        try: 
            return self.matches[state]
        except IndexError:
            return None

class usageStats:
    def __init__(self, data, mateUsage, dt):
        splitFilter = filter(None, re.split(r'(gen[0-9]+)', data["info"]["metagame"]))
        splitList = list(splitFilter)
        self.gen = splitList[0]
        self.metagame = splitList[1]
        self.date = dt
        self.metagame = splitList[0] + splitList[1] 
        self.data = data["data"]
        self.pokemons = {}
        self.weight_total = 0
        for pokemon in data["data"]:
            temp_pkm = pkm(data["data"][pokemon], pokemon, mateUsage)
            #pokemans_dict[temp_pkm.species] = temp_pkm
            self.pokemons[temp_pkm.species] = temp_pkm
        del self.data
    def exportJSON(self):
        pokes = json.dumps(self, default=lambda x: x.__dict__)
        with open("pokes.json", 'w') as f:
            f.write(pokes)


class pkm:
    def __init__(self, data, pokemon, mateUsage):
        #print(pokemon)
        self.usage      = float(data["usage"])*100
        self.rawcc      = data["Raw count"]
        self.moves      = getMoves(data["Moves"])
        self.abilities  = getItemAbilities(data["Abilities"], False)
        self.teammatesPre  = getTeammates(data["Teammates"])
        self.items      = getItemAbilities(data["Items"], True)
        self.spreads    = getSpreads(data["Spreads"])
        self.pokedex_entry    = dict(searchPokedex(pokemon))
        self.species    = self.pokedex_entry["name"]
        self.types      = self.pokedex_entry["types"]
        self.rawname    = pokemon
        self.teammates = []
        self.teammatesUsage = mateUsage
        #self.happiness  = data["Happiness"]
        
    def printInfo(self):
        self.printUsage()
        self.printAbilities()
        self.printSpreads()
        self.printTeammates()
        self.printItems()

    def printAbilities(self):
        print("\nAbilities\n")
        for ab in self.abilities:
            print("(" + str(ab[1]) + "% )" + ab[0])

    def printUsage(self):
        print(self.species + ": " + str(self.usage) + "%")

    def printSpreads(self):
        print("\nSpreads\n")
        spreadsSorted = sorted(self.spreads, key=lambda k: k[7][1], reverse=True) 
        for s in spreadsSorted:
            if s == None or s[7][1] < 1.0:
                continue
            print("(" + str(s[7][1]) + "%)" + s[0][0] + ": " + s[0][1] + " " 
            + s[1][0] + ":" + s[1][1] + " / " 
            + s[2][0] + ":" + s[2][1] + " / "
            + s[3][0] + ":" + s[3][1] + " / "
            + s[4][0] + ":" + s[4][1] + " / "
            + s[5][0] + ":" + s[5][1] + " / "
            + s[6][0] + ":" + s[6][1]) 
    def printItems(self):
        print("\nItems\n")
        itemsSorted = sorted(self.items, key=lambda k: k[1], reverse=True)
        for i in itemsSorted: 
            print("(" + str(i[1]) + "%) " + i[0])

    def fixTeammatesPer(self, pokemans_dict):
        for mate in self.teammatesPre:
            if (mate[0] in self.teammatesUsage[self.rawname].keys() ) and (mate[0] in pokemans_dict or searchPokedex(mate[0])["key"] in pokemans_dict):
                tmpMateUsage = float(pokemans_dict[mate[0]].usage)
                tmpMate = self.teammatesUsage[self.rawname][mate[0]]
                self.teammates.append((mate[0], float(tmpMate[0])))
                #if tmpMate[1] == '+':
                #    self.teammates.append((mate[0], tmpMateUsage+float(tmpMate[0])))
                #elif tmpMate[1] == '-':
                #    self.teammates.append((mate[0], tmpMateUsage-float(tmpMate[0])))
        del self.teammatesPre
        del self.teammatesUsage

    
    def printTeammates(self):
        print("\nTeammates\n")
        matesSorted = sorted(self.teammates, key=lambda k: k[1], reverse=True)
        for mate in matesSorted:
            print( "(" + str(mate[1]) + " %) " + mate[0])


def save_obj(obj, folder, name):
    dir = os.path.dirname(os.path.abspath(__file__))
    filename = name + '.pkl'
    objFolder = os.path.join(dir, 'obj', folder + "/")
    if not os.path.exists(os.path.dirname(objFolder)):
        try:
            os.makedirs(os.path.dirname(objFolder))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(os.path.join(objFolder, filename), 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    dir = os.path.dirname(os.path.abspath(__file__))
    filename = name + '.pkl'
    objFolder = os.path.join(dir, 'obj')
    print(os.path.join(objFolder, filename))
    try:
        with open(os.path.join(objFolder, filename), 'rb') as f:
            return pickle.load(f)
    except IOError:
        print("IOError")
    except EOFError:
        print("EOFError")

def getMoves(moves): 
    res_moves = []
    weight_total = sum(moves.values())
    for move in moves:
        
        tmp_move = searchMovedex(move)
        if(tmp_move == None):
            res_moves.append(("Other", "n/a", ((moves[move] / weight_total) * 100 ) * 4))
        else:
            #Transforma os weights em percentagem, weight dum move / weight sum * 100 = %, multiplica-se por 4 visto cada pkm ter 4 moves
            percentage = ((moves[move] / weight_total) * 100 ) * 4
            res_moves.append((tmp_move["name"], tmp_move["type"], percentage))
    return res_moves

def getItemAbilities(data, item):
    res = []
    weight_total = sum(data.values())
    for key in data:
        percentage = ((data[key] / weight_total) * 100 )
        if item and percentage < 1.0:
            continue
        
        res.append((key, percentage))
    return res

def getTeammates(mates):
    res_teammates = []
    for mate in mates:
        #temp_teammate = []
        percentage = mates[mate]#((mates[mate] / weight_total) * 100)
        res_teammates.append((mate, percentage))
        #res_teammates.append(collections.OrderedDict(temp_teammate))
    return res_teammates

def getSpreads(spreads):
    res_spreads = []
    weight_total = sum(spreads.values())
    for spread in spreads:
        temp_spread = []
        spreadSplit = spread.split(':')
        tmp = spreadSplit[1].split('/')
        percentage = ((spreads[spread] / weight_total) * 100)
        if percentage < 1.0:
            continue
        elif percentage >= 1.0:
            temp_spread.append(("Nature", spreadSplit[0]))
            temp_spread.append(("HP"    , tmp[0]))
            temp_spread.append(("ATK"   , tmp[1]))
            temp_spread.append(("DEF"   , tmp[2]))
            temp_spread.append(("SPATK" , tmp[3]))
            temp_spread.append(("SPDEF" , tmp[4]))
            temp_spread.append(("SPD"   , tmp[5]))
            temp_spread.append(("USAGE" , percentage))
            res_spreads.append(temp_spread)
    return(res_spreads)

def searchPokedex(pkm):
    if pkm in pokedex:
        pokedex[pkm]["key"] = pkm
        return pokedex[pkm]
    elif pkm.lower() in pokedex:
        pokedex[pkm.lower()]["key"] = pkm.lower()
        return pokedex[pkm.lower()]
    else:        
        for key in pokedex:
            if(pokedex[key]["name"] == pkm):
                pokedex[key]["key"] = key
                return pokedex[key]
        if pkm.lower() in speciesLookup:
            print(speciesLookup[pkm.lower()])
            pokedex[pkm.lower()]["key"] = pkm.lower()
            return pokedex[pkm.lower()]
        else:
            for p in speciesLookup:
                if speciesLookup[p] == pkm:
                    pokedex[p]["key"] = p
                    return pokedex[p]

def searchMovedex(move):
    if move in movedex:
        return movedex[move]
    else:
        for key in movedex:
            if(movedex[key]["name"] == move):
                return movedex[key]

def getUrlPaths(url, ext='', params={}):
    response = requests.get(url, params=params)
    if response.ok:
        response_text = response.text
    else:
        return response.raise_for_status()
    soup = BeautifulSoup(response_text, 'html.parser')
    parent = [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
    return parent[-1] if ext == '' else parent


def getJsonLocal():
    dir = os.path.dirname(os.path.abspath(__file__))
    statsFolder = os.path.join(dir, "stats")
    statsFolder = os.path.join(statsFolder, "chaos")
    res = []
    for file in os.listdir(statsFolder):
        if(file.endswith(".json")):
            res.append(os.path.join(statsFolder, file))
        else:
            continue
    return res

#result = getUrlPaths(url, ext)
#result = getJsonLocal()
def getUsageStats(path, local):
    if(bool(local)):
        with open(path, 'r') as file:
            return json.load(file)
    elif(not(bool(local))):
        with urllib.request.urlopen(path) as url:
            return json.loads(url.read().decode())

def calc_resistances(types_list):
    res_resistances = np.ones(18)
    for t in types_list:
        res_resistances *= weaknesses_dict[t]
    return res_resistances

def get_resistances(types_dict):
    resistances_dict = {}
    for pokemon in types_dict.keys():
        resistances_dict[pokemon] = calc_resistances(types_dict[pokemon])
    return resistances_dict


def savePickles(mode, dt, usage_dict, moves_dict, abilities_dict, teammates_dict, items_dict, spreads_dict, stats):
    print("Saving " + str(mode) + "pickles @" + str(datetime.datetime.now()))
    sep = "_"
    save_obj(usage_dict,        mode, "usage_dict"          + sep + mode + sep + str(dt))
    save_obj(moves_dict,        mode, "moves_dict"          + sep + mode + sep + str(dt))
    save_obj(teammates_dict,    mode, "teammates_dict"      + sep + mode + sep + str(dt))
    save_obj(items_dict,        mode, "items_dict"          + sep + mode + sep + str(dt))
    save_obj(abilities_dict,    mode, "abilities_dict"      + sep + mode + sep + str(dt))
    save_obj(spreads_dict,      mode, "spreads_dict"        + sep + mode + sep + str(dt))
    save_obj(types_dict,        mode, "types_dict"          + sep + mode + sep + str(dt))
    save_obj(resistances_dict,  mode, "resistances_dict"    + sep + mode + sep + str(dt))
    save_obj(stats,     mode, "pokemans_dict"       + sep + mode + sep + dt)

def getModes():
    tmpModes = []
    if os.path.exists("obj/modes.pkl") :
        print("Local")
        return load_obj("modes")
    elif not os.path.exists("obj/modes.pkl"):
        print("Web")
        baseUrl =  'https://www.smogon.com/stats/'
        latest = getUrlPaths(baseUrl)
        chaosUrl = latest + "chaos/"
        chaosList = getUrlPaths(chaosUrl, 'json')
        for i in chaosList:
                tmpModes.append(i.replace(chaosUrl, '').replace('.json', ''))

        save_obj(tmpModes, '.', 'modes')
        return tmpModes
def getUrlDict(local):

    dir = os.path.dirname(os.path.abspath(__file__))
    pathsDict = os.path.join(dir, 'obj' , "localPaths.pkl")
    webDict = os.path.join(dir, 'obj', "webPaths.pkl")
    if local and os.path.exists(pathsDict):
        return load_obj("localPaths")
    elif not local and os.path.exists(webDict):
        return load_obj("webPaths")
    else:
        baseUrl =  'https://www.smogon.com/stats/'
        latest = getUrlPaths(baseUrl)
        latestDate = latest.replace(baseUrl, '').replace("/", '')
        if not local:
            chaosUrl = latest + "chaos/"
            movesetUrl = latest + "moveset/"
        elif local:
            chaosUrl = os.path.join(dir, "stats", "chaos")
            movesetUrl = os.path.join(dir, "stats", "moveset")

        global modes 
        modes = getModes()
        urlsDict = {}
        extChaos = '.json'
        extMoveset = '.txt'
        for mode in modes:
            if not local:
                urlsDict[mode] = (chaosUrl + mode + extChaos, movesetUrl + mode + extMoveset, latestDate)
            elif local:
                urlsDict[mode] = (os.path.join(chaosUrl, mode) + extChaos, os.path.join(movesetUrl, mode) + extMoveset, latestDate)
        
        save_obj(urlsDict, ".", "localPaths" if local else "webPaths")
        return urlsDict

types_dict = {} 

def parserMain(local, urlsDict):
    print("Starting dataset gen @ [" + str(datetime.datetime.now()) + "]")
    global modes
    resistances_dict = get_resistances(types_dict)

    for mode in urlsDict:
        if(mode != "gen8vgc2021-1760"):
            continue
        print(mode) 
        #Armindo
        parserMode(urlsDict[mode], mode, local)
    print("Finished dataset gen @ [" + str(datetime.datetime.now()) + "]")

def parserMode(mode, m, local):
        usage_dict = {}
        moves_dict = {}
        abilities_dict = {}
        teammates_dict = {}
        items_dict = {}
        spreads_dict = {}
        teammatesUsage = mvparser.parseFormat(mode[1], local)
        tmp = getUsageStats(mode[0], local)
        stats = usageStats(tmp, teammatesUsage, mode[2])
        for pkm_key, poke in stats.pokemons.items():
            poke.fixTeammatesPer(stats.pokemons)
            usage_dict[poke.species] = poke.usage
            moves_dict[poke.species] = poke.moves
            teammates_dict[poke.species] = poke.teammates
            items_dict[poke.species] = poke.items
            spreads_dict[poke.species] = poke.spreads
            abilities_dict[poke.species] = poke.abilities
            types_dict[poke.species] = poke.types
        savePickles(m, mode[2], usage_dict, moves_dict, abilities_dict, teammates_dict, items_dict, spreads_dict, stats)

def exportJSON(mode, path):
    pokemans_dict   = load_obj(path)

    searchTerms = ["Tapu Fini", "Incineroar", "Tornadus", "Regieleki", "done"]
    pokes = "["
    for search in searchTerms:
        if search in pokemans_dict:
            if pokemans_dict[search].teammatesPre and pokemans_dict[search].teammatesUsage:
                del pokemans_dict[search].teammatesPre
                del pokemans_dict[search].teammatesUsage
            print("[ " + str(search) + " ]")
            if searchTerms.index(search) == 0:
                pokes += json.dumps(pokemans_dict[search].__dict__)
            else:
                pokes += ',' + json.dumps(pokemans_dict[search].__dict__)
        elif search == "done":
            pokes += "]"
            print(pokes[17])
            with open("pokes.json", 'w') as f:
                f.write(pokes)

#parser(True)

args = sys.argv[1:]
if args[0] == "-l" or args[0] == "--local":
    urlsDict = getUrlDict(True)
    for l, p in urlsDict.items():
        if not os.path.exists(p[0]) or not os.path.exists(p[1]):
            if not os.path.exists(p[0]):
                print("File " + p[0] + "missing (did you wget the chaos directory before starting the script?)")
                sys.exit("Run -h for help running the parser")
            elif not os.path.exists(p[1]):
                print("File " + p[1] + "missing (did you wget the moveset directory before starting the script?)")
                sys.exit("Run -h for help running the parser")
    parserMain(True, urlsDict)
elif args[0] == "-w" or args[0] == "--web":
    urlsDict = getUrlDict(False)
    parserMain(False, urlsDict)
elif args[0] == "-s" or args[0] == "--search":
    completer = AutoCompleter(modes)
    readline.set_completer_delims(' \t\n;')
    readline.set_completer(completer.complete)
    readline.parse_and_bind('tab: complete')
    pesquisa = ""
    while(pesquisa not in modes):
        pesquisa = input("Input: ")
        if pesquisa not in modes:
            print("Unknown mode, please try again(you can autocomplete with tab).") 
    url = getUrlDict(True)[pesquisa]
    dir = os.path.dirname(os.path.abspath(__file__))
    dir = os.path.join(dir, 'obj')
    pathObj = os.path.join(pesquisa, "pokemans_dict_" + pesquisa + "_" + url[2] )
    pathObjDict = os.path.join(dir, pathObj)
    if os.path.exists(pathObjDict + ".pkl"):
        pokemans = load_obj(pathObj)
        indexes = list(pokemans.pokemons.keys())
        completer = AutoCompleter(indexes)
        readline.set_completer_delims(' \t\n;')
        readline.set_completer(completer.complete)
        readline.parse_and_bind('tab: complete')
        pesquisa = ""
        while(pesquisa not in pokemans.pokemons):
            pesquisa = input("Input: ")
            print(pesquisa)
            if pesquisa not in pokemans.pokemons:
                print("Unknown mode, please try again(you can autocomplete with tab).")
        
        pokemans.pokemons[pesquisa].printInfo()

else:
    print("Unknown argument: [" + args[0] + "], use --local/-l or --web/-w")
    #print("wget -r -nc -np -nH --cut-dirs=2 -A txt -P ./stats https://www.smogon.com/stats/{year}-{month}/moveset/")
    #print("wget -r -nc -np -nH --cut-dirs=2 -A txt -P ./stats https://www.smogon.com/stats/{year}-{month}/chaos/")
print("Arg: " + str(args))

