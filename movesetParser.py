import re, json, urllib, os

pokedex = []

dexFolder = [ f.path for f in os.scandir(os.getcwd()) if ( f.is_dir() and f.name == "dex") ]
print(dexFolder)

with open(os.path.join(dexFolder[0], "pokedex.json"), 'r') as file:
    pokedex = json.load(file)
with open(os.path.join(dexFolder[0], "species-lookup.json"), 'r') as file:
    speciesLookup = json.load(file)


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
            pokedex[pkm.lower()] = pokedex[speciesLookup[pkm.lower()]]
            del pokedex[speciesLookup[pkm.lower()]]
            return pokedex[pkm.lower()]
        else:
            for p in speciesLookup:
                if speciesLookup[p] == pkm:
                    pokedex[p]["key"] = p
                    return pokedex[p]

name = '^ [|]{1} [a-zA-Z0-9]+[ ]+[|]{1} $'
sep_regex = "^[+][-]{1,}[+]$"

def firstParse(file_list):
    i = 0
    pkmsPre = []
    while i < len(file_list):
        try:
            if re.match(sep_regex, file_list[i]) and searchPokedex(file_list[i+1].strip()) != None:
                name = file_list[i+1].strip()
                k = i+2
                mates = 0
                teammates_list = []
                while k < len(file_list):
                    if re.match(".Teammates.", file_list[k]) and not mates:
                        mates = 1
                    elif mates and not re.match(sep_regex, file_list[k]):
                        teammates_list.append(file_list[k].strip())
                    elif mates and re.match(sep_regex, file_list[k]):
                        break
                    k += 1
                pkmsPre.append((name, teammates_list))
        except:
            break
        i += 1
    return pkmsPre

def parseFormat(movesetFile, local):
    file_list = []
    pkms = {}
    #with open(movesetFile, 'r') as file:
    if not local:
        for l in urllib.request.urlopen(movesetFile):
           tmp = l.decode('utf-8').strip()
           file_list.append(tmp.replace('|', ""))
    elif local:
        with open(movesetFile) as temp_file:
           for line in temp_file:
               #tmp = line.decode('utf-8').strip()
               tmp = line.strip()
               file_list.append(tmp.replace('|', ""))


    pkmsPre = firstParse(file_list)

    for poke in pkmsPre:
        tmp_mates = {}
        for mate in poke[1]:
            #old regex for the +% on teammates r'(([+]|[-])\d+([.,]\d+)?)'
            tmp = list(filter(None, re.split(r'(\d+([.,]\d+)?)', mate)))
            #tmp[1] = re.sub(r'[+]|[-]', '', tmp[0])
            tmp_mates[tmp[0].strip()] = tmp[1]
        pkms[poke[0]] = tmp_mates
    return pkms
