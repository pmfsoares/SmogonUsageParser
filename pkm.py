import string

class Move:
    Move: string
    Type: string 
    Usage: float 

    #move = result from the searchMovedex()         tmp_move = searchMovedex(moveName)
    def __innit__(self, move, moveUsage,  weight_total):
        self.Usage = ((moveUsage / weight_total) * 100 ) * 4
        
        if(move == None):
            self.Move = "Other"
            self.Type = "n/a"
        else:
            self.Move = move["move"]
            self.Type = move["type"]


class Ability:
    Ability: string
    Usage: float 

    #ab = searchAbilityDex(ability)["name"]
    def __innit__(self, ab, abUsage, weight_total):
        self.Usage = abUsage / weight_total * 100
        if ab == "noability":
            self.Ability = "No ability"
        else:
            self.Ability = ab
        
class Item:
    Item: string
    Usage: float

    #ab = searchItemdex(item)["name"]
    def __innit__(self, item, itemUsage, weight_total):
        self.Usage = itemUsage / weight_total * 100
        if item == "nothing":
            self.Ability = "Nothing"
        else:
            self.Ability = item



class EffortValues:
    HP: int
    ATK: int
    DEF: int
    SPATK: int
    SPDEF: int
    SPD: int

    def __innit__(self, spread):
        self.HP     = tmp[1]
        self.ATK    = tmp[2]
        self.DEF    = tmp[3]
        self.SPATK  = tmp[4]
        self.SPDEF  = tmp[5]
        self.SPD    = tmp[6]

class Spread:
    Nature: string
    EVs: EffortValues
    Usage: float

    def __innit__(self, Spread, sprUsage, weight_total):
        spreadSplit = Spread.split(':')
        tmp = spreadSplit[1].split('/')
        self.Nature = tmp[0]
        self.EVs = EffortValues(tmp)
        self.Usage = (sprUsage / weight_total) * 100
        
class Pokemon:
    Usage: float
    Moves: list[Move]
    Abilities: list[Ability]
    

