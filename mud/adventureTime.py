__author__ = 'samd'
import yaml, sys, os
inventory = {}

class Location(object):
    def __init__(self, data):
        self.data = data
        self.items = {}

        self.processData(self.data)

    def processData(self, data):
        ## Make our clean desciption with \n
        self.desc = ""
        for eachLine in data['description']:
            self.desc = "{} {}\n".format(self.desc, eachLine)
        self.nrth = data['N'] or None
        self.est = data['E'] or None
        self.sth = data['S'] or None
        self.wst = data['W'] or None
        self.items = data['validLocationItems']
        self.locName = data['locationName']

    @property
    def locationName(self):
        return self.locName

    @property
    def north(self):
        return self.nrth

    @property
    def east(self):
        return self.est

    @property
    def south(self):
        return self.sth

    @property
    def west(self):
        return self.wst

    @property
    def description(self):
        return self.desc

    @property
    def validItems(self):
        valid = self.items.keys()
        return valid

    def validActions(self, type):
        if self.items[type]["validActions"]:
            valid = self.items[type]["validActions"].keys()
            return valid
        else:
            return None

def fetchData():
    filePath = "C:/Users/samd/PycharmProjects/SamsCOdE/adventureData.yaml"
    data = yaml.load(open(filePath, "r"))
    return data

def startGame(gdata = None):
    ## this is a new game
    os.system("cls")
    if not gdata:
        raise Exception, 'THERE IS NO GAME DATA!'
    data = gdata['start']
    runGame(data, gdata)

def runGame(data, gameData):
    myLocation = Location(data)
    print "#################"
    print "You have arrived at {}".format(myLocation.locationName)
    print myLocation.description
    print "#################"
    inp = raw_input(">> What would you like to do?:  ")

    if inp.lower() == "look" or inp == 'l':
        runGame(data, gameData)

    elif inp.lower() == "n":
        if myLocation.north:
            os.system("cls")
            runGame(gameData[myLocation.north], gameData)
        else:
            os.system("cls")
            print '#####\nYou can not travel in that direction from here!\n#####\n'
            runGame(data, gameData)

    elif inp.lower() == "e":
        if myLocation.east:
            os.system("cls")
            runGame(gameData[myLocation.east], gameData)
        else:
            os.system("cls")
            print '#####\nYou can not travel in that direction from here!\n#####\n'
            runGame(data, gameData)

    elif inp.lower() == "s":
        if myLocation.south:
            os.system("cls")
            runGame(gameData[myLocation.south], gameData)
        else:
            os.system("cls")
            print '#####\nYou can not travel in that direction from here!\n#####\n'
            runGame(data, gameData)

    elif inp.lower() == "w":
        if myLocation.west:
            os.system("cls")
            runGame(gameData[myLocation.west], gameData)
        else:
            os.system("cls")
            print '#####\nYou can not travel in that direction from here!\n#####\n'
            runGame(data, gameData)

    elif inp.lower() == "help" or inp.lower() == 'h':
        os.system("cls")
        print "-----"
        print gameData['help']
        print "-----"
        runGame(data, gameData)

    elif inp.lower() == "i":
        os.system("cls")
        print "-----"
        for key, var in inventory.items():
            print "YOUR INVENTORY:\n"
            print "\tItem Name:  {}\n\tDescription:  {}".format(key, var)
        print "-----"
        runGame(data, gameData)

    elif inp.lower() == 'exit':
        print 'You are a chicken!'
        return -1

    else:
        os.system("cls")
        accepted = False
        if myLocation.validItems:
            for eachValidItem in myLocation.validItems:
                if eachValidItem.lower() in inp.lower():
                    if myLocation.validActions(eachValidItem): ## we have some valid actions in the locations validActions key
                        for eachAction in myLocation.validActions(eachValidItem):
                            if eachAction.lower() in inp.lower():
                                ## Test for item already existing in inventory.
                                if eachAction == 'get' :
                                    if 'item' in myLocation.items[eachValidItem].keys():
                                        itemName = myLocation.items[eachValidItem]['item']
                                        itemDescription = myLocation.items[eachValidItem]['itemDescription']
                                        if itemName in inventory.keys():
                                            print 'You already have that item.'
                                            runGame(data, gameData)

                                ## If we are not getting an item then just return the value for the action.
                                print "-----------------------"
                                print "-- {}".format(myLocation.items[eachValidItem]['validActions'][eachAction])
                                print "-----------------------"
                                accepted = True

                                ## If we get the item
                                if eachAction == 'get':
                                    if 'item' in myLocation.items[eachValidItem].keys():
                                        itemName = myLocation.items[eachValidItem]['item']
                                        itemDescription = myLocation.items[eachValidItem]['itemDescription']
                                        if itemName not in inventory.keys():
                                            inventory[itemName] = itemDescription
                                        else:
                                            print 'You already have that item.'
                                    else:
                                        print "There is nothing here to find."
                    else:
                        print "-----------------------"
                        print "-- {}".format(myLocation.items[eachValidItem]['description'])
                        print "-----------------------"
                        accepted = True
        else:
            print "There really is nothing to do here."
        print ""
        if not accepted:
            print 'That command is not understood. Please try again!'
        print ""
        runGame(data, gameData)

gameData = fetchData()
## GameData is formatted like so
## LCOATIONAME:
    # locationName: string
    # description: list of string

startGame(gameData)
