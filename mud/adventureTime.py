__author__ = 'samd'
import yaml, sys, os

MSG_FAILEDTRAVEL = '#####\nYou can not travel in that direction from here!\n##### Use help for command list.\n'
MSG_INVALIDCOMMAND = "That is not a valid command!  Use help for command list.\n"
MSG_INVALID_ITEMCOMMAND = "You can't do that to {}!.\n"
MSG_NOTHINGHERE = "There really is nothing to do or see here! Move along!"
MSG_HELP = "To move around the world, use N E S W. To open doors use opendoor or od. To look use look. I for inventory."
VALID_GET_ACTIONS = ['get', "grab", "snatch", 'take', 'steal']
GAMEACTIONS = ["help", 'i', 'exit', "opendoor", "od", 'look']
GAMEDIRECTIONS = ['n', 'e', 's', 'w']
HAVEITEM = "You um.. prob have that item already!"
SEP = "-----"
SEPNL = "-----\n"
INPUTQUERY = ">> What would you like to do?:   "
inventory = {} ## To move to a yaml write file! So we can continue where we left off.


class Location(object):
    def __init__(self, data):
        self.data = data
        self.processData(self.data)

    def processData(self, data):
        ## The key for the gameData dictionary
        self._locKey = data['locKey']
        # The name of the location!
        self.locName = data['locationName']

        ## Make our clean desciption with \n
        self.desc = ""
        for eachLine in data['description']:
            self.desc = "{} {}\n".format(self.desc, eachLine)

        # Do we have a valid direction from here?
        self.nrth = data['N'] or None
        self.est = data['E'] or None
        self.sth = data['S'] or None
        self.wst = data['W'] or None

        ## Does the location itself have any items? Or any items have items?
        self._locationItemData = self.getItems(data['validLocationItems'])

    def getItems(self, itemData):
        """
        Here we process the data for the items. If it's a root item etc. We're going to turn all of this data into a
        base class for each item so they have nice properties etc for us to use to get information back about the item.
        :param itemData: The dictionary for the items (from the yaml file)
        """
        locItems = []
        for key, value in itemData.items(): ##This is a standard dictionary iteration through the key, value items in a dict
            item = Item()
            item.itemName = value['itemName']
            item.itemDescription = value['itemDescription']
            item.isRootItem = value['isRootItem']
            item.canTakeItem = value['canTakeItem']
            item.isTaken = value['taken']
            item.takenDescription = value['takenDescription']
            item.validActions = value['validActions']
            item.failedTakeMsg = value['failedTakeMsg']

            children = value['children']
            ## Do we have a valid list of child items to process! If YES lets process these now and store them in the list!!
            if children:
                for eachChild in children:
                    childItem = Item()
                    childItem.isRootItem = False # It will never be a root item we don't need to look this up or have it in the yaml!
                    childItem.itemName = eachChild['itemName']
                    childItem.itemDescription = eachChild['itemDescription']
                    childItem.canTakeItem = eachChild['canTakeItem']
                    childItem.isTaken = eachChild['taken']
                    childItem.takenDescription = eachChild['takenDescription']
                    childItem.validActions = eachChild['validActions']
                    childItem.failedTakeMsg = eachChild['failedTakeMsg']

                    item.addChild(childItem)

            locItems.append(item)
        return locItems

    @property
    def locKey(self):
        return self._locKey

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
    def locationItems(self):
        return self._locationItemData or None

    def isValidDirection(self, dir):
        input = dir.lower()
        if input == "n" and self.north is not None:
            return True
        elif input == "s" and self.south is not None:
            return True
        elif input == "e" and self.east is not None:
            return True
        elif input == "w" and self.west is not None:
            return True
        else:
            return False

    def removeChildItem(self, locationItem, child):
        for x, item in enumerate(self.locationItems):
            locationItemName = locationItem.itemName.lower()
            if locationItemName == item.itemName.lower():
                locationItem.removeChild(child)
        self.updateItemData()

    def updateItemData(self):
        ## Clean the current data for items
        del self.data['validLocationItems']

        ## Now recreate the item data based off the current items in memory
        validLocationItems = {}
        for eachItem in self.locationItems:
            validLocationItems[eachItem.itemName] = {}
            validLocationItems[eachItem.itemName]["itemName"] = eachItem.itemName
            validLocationItems[eachItem.itemName]["itemDescription"] = eachItem.itemDescription
            validLocationItems[eachItem.itemName]["isRootItem"] = eachItem.isRootItem
            validLocationItems[eachItem.itemName]["canTakeItem"] = eachItem.canTakeItem
            validLocationItems[eachItem.itemName]["taken"] = eachItem.isTaken
            validLocationItems[eachItem.itemName]["takenDescription"] = eachItem.takenDescription
            validLocationItems[eachItem.itemName]["failedTakeMsg"] = eachItem.failedTakeMsg
            validLocationItems[eachItem.itemName]["validActions"] = eachItem.validActions
            ## Now get the item's children
            if not eachItem.children:
                validLocationItems[eachItem.itemName]["children"] = []
            else:
                children = []
                for eachChild in eachItem.children:
                    childData = {}
                    childData["isRootItem"] = False
                    childData["itemName"] = eachChild.itemName
                    childData["itemDescription"] = eachChild.itemDescription
                    childData["canTakeItem"] = eachChild.canTakeItem
                    childData["taken"] = eachChild.isTaken
                    childData["takenDescription"] = eachChild.takenDescription
                    childData["failedTakeMsg"] = eachChild.failedTakeMsg
                    childData["validActions"] = eachChild.validActions
                    children.append(childData)
                validLocationItems[eachItem.itemName]["children"] = children
        self.data['validLocationItems'] = validLocationItems

class Item(object):
    def __init__(self):
        self._isRootItem = False
        self._isTaken = False
        self._canTakeItem = False
        self._failedTakeMsg = ""
        self._takenDescription = ""
        self._itemName = ""
        self._itemDescription = ""
        self._validActions = []
        self._children = []

    @property
    def canTakeItem(self):
        return self._canTakeItem

    @canTakeItem.setter
    def canTakeItem(self, canTake):
        self._canTakeItem = canTake

    @property
    def failedTakeMsg(self):
        return self._failedTakeMsg

    @failedTakeMsg.setter
    def failedTakeMsg(self, msg):
        self._failedTakeMsg = msg

    @property
    def isRootItem(self):
        return self._isRootItem

    @isRootItem.setter
    def isRootItem(self, rootItem):
        self._isRootItem = rootItem

    @property
    def isTaken(self):
        return self._isTaken

    @isTaken.setter
    def isTaken(self, isTaken):
        self._isTaken = isTaken

    @property
    def takenDescription(self):
        return self._takenDescription

    @isTaken.setter
    def takenDescription(self, description):
        self._takenDescription = description

    @property
    def itemName(self):
        return self._itemName

    @itemName.setter
    def itemName(self, itemName):
        self._itemName = itemName

    @property
    def itemDescription(self):
        return self._itemDescription

    @itemDescription.setter
    def itemDescription(self, itemDescription):
        self._itemDescription = itemDescription

    @property
    def validActions(self):
        return self._validActions

    def validActions(self, validActions):
        self._validActions = validActions

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, children):
        return self._children

    def addChild(self, child):
        self._children.append(child)

    def removeChild(self, childName):
        self._children.remove(childName)

#####################################################################
## THE GAME #########################################################
def fetchData():
    basePath = os.path.dirname(__file__)
    locations = os.path.join(basePath, "locations")

    locationData = {}
    for eachFile in os.listdir(locations):
        data = yaml.load(open(os.path.join(locations, eachFile), "r"))
        locationData[eachFile.partition(".")[0]] = data

    return locationData

def startGame(locationData = None):
    ## this is a new game
    os.system("cls")
    if not locationData:
        raise Exception('THERE IS NO GAME DATA!')
    runGame(locationData['home'], locationData)

def locationDescription(curLocation):
    print("#################")
    print("Location: {}".format(curLocation.locationName))
    print(curLocation.description)
    directions = ""
    if curLocation.north is not None:
        directions += "n, "
    if curLocation.east is not None:
        directions += "e, "
    if curLocation.south is not None:
        directions += "s, "
    if curLocation.west is not None:
        directions += "w, "
    print("#################")
    print("You can travel {} from here.".format(directions))
    print("#################\n")

def runGame(locationData, gameData, repeatDescription=True):
    #####################################################################
    ## We are going to exit early if we have no valid game data!
    if not locationData:
        print("No gameData! Aborting!")

    #####################################################################
    ## We have some valid data so we're going to setup some easy variables to use.
    curLocation = Location(locationData)

    ## This is a hack to avoid the game running the intro description over and over.
    if repeatDescription:
        locationDescription(curLocation)
        print("To get help type help or h")

    #####################################################################
    ## Setup the input from the user now.
    userInput = input(INPUTQUERY).lower()

    #####################################################################
    ## Now we can check the returned data from the user typing something.
    ## We look in this order;
    # Is it a direction?
    # Is it a keyword? look, i, help, exit ?
    # Is it an action word? If so is it a location based action eg: on a Tree? or an action on a childItem? eg an Apple
    if userInput.lower() in GAMEDIRECTIONS:
        os.system("cls")

        def checkDirectionInput(locationData):
            if userInput.lower() == "n":
                if curLocation.north is not None:
                    locationData = gameData[curLocation.north]
                else:
                    print(MSG_FAILEDTRAVEL)
            elif userInput.lower() == "e":
                if curLocation.east is not None:
                    locationData = gameData[curLocation.east]
                else:
                    print(MSG_FAILEDTRAVEL)
            elif userInput.lower() == "s":
                if curLocation.south is not None:
                    locationData = gameData[curLocation.south]
                else:
                    print(MSG_FAILEDTRAVEL)
            elif userInput.lower() == "w":
                if curLocation.west is not None:
                    locationData = gameData[curLocation.west]
                else:
                    print(MSG_FAILEDTRAVEL)

            runGame(locationData, gameData, True)
        checkDirectionInput(locationData)
    elif userInput.lower() == "help" or userInput.lower() == 'h':
        os.system("cls")
        print(SEP)
        print(MSG_HELP)
        print(SEP)
        runGame(locationData, gameData, False)
    elif userInput.lower() == "i":
        def checkInventory():
            print(SEP)
            if len(inventory.items()) != 0 :
                print("YOUR INVENTORY:\n")
                for key, var in inventory.items():
                    print("\t{}".format(SEP))
                    print("\tItem Name:  {}\n\tDescription:  {}".format(key, var))
                print(SEP)
            else:
                print("Your inventory is EMPTY!\n")
            runGame(locationData, gameData, False)
        checkInventory()
    elif userInput.lower() == 'exit':
        print("You big fat chicken!")
        sys.exit("BARRRRKKKK!")
    elif userInput.lower() == 'look':
        def runLook():
            os.system("cls")
            locationDescription(curLocation)
            ## Check to see if we have some location items in the dictionary.
            if curLocation.locationItems is not None:
                print("You can also see here the following items:")
                for eachItem in curLocation.locationItems:
                    print("\t~| {}".format(eachItem.itemName))
                runGame(locationData, gameData, False)
            else:
                ## We have no location items so just say so!
                print("There is nothing else of note here!\n")
                runGame(locationData, gameData, False)
        runLook()

    #####################################################################
    ## ALL OTHER TYPING! WE WANT TO LOOK FOR KEY WORDS IN THE ITEMS AND ACTIONS!
    else:
        os.system("cls")
        ## Check the yaml for validLocationItems:
        ## If we have an empty list here eg: validLocationItems: [] it will return False
        if curLocation.locationItems:
            ## Create a variable to store if we found a root locationItem the action is being performed on.

            def checkLocationItems():
                ## Now check through ALL the location items. First we check through the rootItems
                for eachItem in curLocation.locationItems:
                    ## Store the location name into an easy to read variable name.
                    locationItemName = eachItem.itemName.lower()

                    ## Does the location name exist in the input?
                    if locationItemName in userInput:
                        ## Fetch all the validActions that can be performed on the location itself.
                        validLocationActions = eachItem.validActions ## <<< note this is property so we don't use ()
                        validActionFound = None
                        ####################
                        ## FIND VALID ACTION
                        ## Now we want to look through the validActions and see if one of those is in the input text
                        for actionName, actionDescrip in validLocationActions.items():
                            if actionName in userInput:
                                validActionFound = actionName

                        if validActionFound is not None:
                            actionDescrip = validLocationActions[validActionFound]

                            ## Look to see if the actionName is in the userInput or not but not a get action
                            if validActionFound not in VALID_GET_ACTIONS:
                                if validActionFound != 'look':
                                    print(actionDescrip)
                                else:
                                    print(actionDescrip)
                                    if eachItem.children:
                                        print("It contains:")
                                        for eachChild in eachItem.children:
                                            print("\t~|{} ".format(eachChild.itemName))

                            ## Now look to see if the actionName is in the userInput and is a get action
                            elif validActionFound in VALID_GET_ACTIONS:
                                ## We have found a valid get action!
                                ## Can the user take this item?
                                if not eachItem.canTakeItem:
                                    print(eachItem.failedTakeMsg)
                                    #print("You can not {} up the {}".format(actionName, locationItemName))
                                    runGame(locationData, gameData, False)

                                ## Is this item taken already??
                                if eachItem.isTaken:
                                    print(eachItem.takenDescription)
                                    runGame(locationData, gameData, False)

                                print(actionDescrip)
                                ## Add this item to the dictionary
                                inventory[eachItem.itemName] = eachItem.itemDescription

                                ## Remove this item from the game data
                                curLocation.locationItems.remove(eachItem.itemName)

                                ## Now update the games state in the gameData we are passing around.
                                gameData[curLocation.locationName] = curLocation

                                runGame(locationData, gameData, False)
                            else:
                                print(MSG_INVALID_ITEMCOMMAND.format(locationItemName))
                            runGame(locationData, gameData, False)

            def checkLocationItemChildren():
                for eachItem in curLocation.locationItems:
                    children = eachItem.children
                    ## Bail out early if we have no children. This removes a potention indent level
                    if not children:
                        return

                    ## We have valid children so lets check through these for a valid action
                    for child in children:
                        itemName = child.itemName.lower()
                        ## Check to see if we have typed a valid child item in the input text
                        if itemName in userInput:
                            ## Now fetch all the valid actions for this child item
                            validChildActions = child.validActions
                            validActionFound = None
                            ####################
                            ## FIND VALID ACTION
                            ## Now we want to look through the validActions and see if one of those is in the input text
                            for actionName, actionDescrip in validChildActions.items():
                                if actionName in userInput:
                                    validActionFound = actionName

                            ## Did we find one?
                            if validActionFound is not None:
                                actionDescrip = validChildActions[validActionFound]

                                ## Look for anything that isn't in the valid actions and print it's descriptions
                                if validActionFound not in VALID_GET_ACTIONS:
                                    print(actionDescrip)
                                    runGame(locationData, gameData, False)

                                ## So we couldn't find something, lets check if the user typed a valid get action.
                                elif validActionFound in VALID_GET_ACTIONS:
                                    ## We have found a valid get action!
                                    ## Can the user take this item?
                                    if not child.canTakeItem:
                                        print(child.failedTakeMsg)
                                        #print("You can not {} the {}".format(actionName, itemName))
                                        runGame(locationData, gameData, False)

                                    ## Is this item taken already??
                                    if child.isTaken:
                                        print(child.takenDescription)
                                        runGame(locationData, gameData, False)

                                    print(actionDescrip)
                                    ## Add this item to the dictionary
                                    inventory[child.itemName] = child.itemDescription
                                    ## Remove this item from the game data
                                    curLocation.removeChildItem(eachItem, child)

                                    ## Now update the games state in the gameData we are passing around.
                                    gameData[curLocation.locKey] = curLocation
                                    runGame(gameData[curLocation.locKey].data, gameData, False) ## Here is where we have to pass back valid location data!

                            ## We can't find a valid action at all!
                            else:
                                print(MSG_INVALID_ITEMCOMMAND.format(itemName))
                                valid = [v for v in validChildActions.keys()]
                                print("Valid actions are {}".format(valid))
                                runGame(locationData, gameData, False)

            checkLocationItems()
            checkLocationItemChildren()

        print(MSG_INVALIDCOMMAND)
        runGame(locationData, gameData, False)

startGame(fetchData())

