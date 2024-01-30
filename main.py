import json

class Location:
    def __init__(self, name, desc, aliases=[]):
        self.name = name
        self.description = desc
        self.aliases = aliases

        self.adjLocations = []
        self.interactables = []

    def showPlayer(self):
        print(self.name + " " + self.description)
        if len(self.interactables) != 0:
            print("Objects nearby:")
            for inter in self.interactables:
                if not inter.hidden:
                    print("    - " + inter.name)
        if len(self.adjLocations) > 0:
            print("Nearby locations: ")
            for loc in self.adjLocations:
                print(f"    - {loc.name}")

    def isName(self, name: str) -> bool:
        return name == self.name or name in self.aliases

    def getInteractable(self, interName: str):
        if type(interName) != str:
            raise ValueError("getInteractable must be given a string")

        for i in self.interactables:
            if i.isName(interName):
                return i
        return None

    def getAdjLocation(self, other):
        if type(other) == str:
            searchVal = other
        elif type(other) == Location:
            searchVal = other.name
        else:
            raise ValueError("getLocation must be given a Location or string")

        for loc in self.adjLocations:
            if loc.name == searchVal:
                return loc
        return None

    def isConnected(self, other):
        if type(other) == str:
            searchVal = other
        elif type(other) == Location:
            searchVal = other.name
        else:
            raise ValueError("isConnected must be given a Location or string")

        return searchVal in list(map(lambda loc: loc.name, self.adjLocations))


class Player:
    currentLocation: Location = Location("null", "")
    alive: bool = True
    inventory = []


class Item:
    def __init__(self, name, desc, aliases=[]):
        self.name = name
        self.desc = desc
        self.aliases = aliases

    def __init__(self, inter):
        self.name = inter.name
        self.desc = inter.desc
        self.aliases = inter.aliases


class Interactable:
    def __init__(self, name, desc, aliases=[], hidden=False, gettable=False):
        self.name = name
        self.desc = desc
        self.aliases = aliases
        self.hidden = hidden
        self.gettable = gettable

        self.actions = {"use": self.onUse, "examine": self.onExamine, "get": self.onGet}

        self.actionAliases = {
            "look": "examine",
            "lookat": "examine",
            "inspect": "examine",
            "pickup": "get",
            "take": "get",
        }

    def isName(self, name: str) -> bool:
        return name == self.name or name in self.aliases

    def doInteraction(self, player: Player, command: str) -> bool:
        inter = self.getInteraction(command)
        if inter:
            inter(self, player)
            return True
        return False

    def getInteraction(self, command: str):
        command = command.lower()
        alias = self.actionAliases.get(command)
        if alias:
            command = alias
        return self.actions.get(command)

    def newInteraction(self, name, func, aliases=[]):
        self.actions[name] = func
        for alias in aliases:
            self.actionAliases[alias] = name

    @staticmethod
    def onUse(interactable, player):
        print("This object cannot be used.")

    @staticmethod
    def onExamine(interactable, player):
        print(interactable.desc)

    @staticmethod
    def onGet(interactable, player, item=None):
        if interactable.gettable:
            if item == None:
                item = Item(interactable)

            print(f"You pick up {item.name}.")

            player.inventory.append(item)
            interactable.hidden = True

        else:
            print("You cannot pick up this object.")


def buildWorld():
    data = json.load(open("world.json"))
    locations = data["locations"]
    # convert top-level values to locations
    for key in locations.keys():
        adj = locations[key]["nearbyLocations"]
        aliases = locations[key]["aliases"]
        interactables = locations[key]["interactables"]
        locations[key] = Location(key, locations[key]["description"])
        locations[key].nearbyLocations = adj
        locations[key].aliases = aliases
        for i in interactables:
            interactable = data["interactables"][i]
            locations[key].interactables.append(
                Interactable(
                    i,
                    interactable["description"],
                    interactable["aliases"],
                    interactable["hidden"],
                    interactable["gettable"],
                )
            )

    # reconstruct adj-locaations
    for key in locations.keys():
        nearbyLocs = []
        for i in range(len(locations[key].nearbyLocations)):
            nearbyLocs.append(locations[locations[key].nearbyLocations[i]])
        locations[key].adjLocations = nearbyLocs

    # convert adj-locations into real references
    you = Player
    you.currentLocation = locations["mars"]

    return you


def main():
    actionAliases = {
        "goto": "go",
        "enter": "go",
        "g": "go",
        "grab": "get",
        "pickup": "get",
        "inv": "inventory",
        "items": "inventory",
        "i": "inventory",
        "h": "help",
    }
    helpActionList = ["g(o)/enter", "i(nventory)/items", "get/grab/pickup"]

    you = buildWorld()
    print("You are on", you.currentLocation.name)
    prevLoc = None
    you.currentLocation.showPlayer()
    while you.alive:
        userText = input()
        print()  # add space
        userWords = userText.split(" ")
        verb = userWords[0]
        target = userText[len(verb) + 1 :]

        lookedUpAction = actionAliases.get(verb.lower())
        if lookedUpAction:
            verb = lookedUpAction

        if verb.lower() == "go":
            foundLoc = False
            if target.lower() == "back" and prevLoc:
                if you.currentLocation.isConnected(prevLoc):
                    foundLoc = True
                    you.currentLocation, prevLoc = prevLoc, you.currentLocation

            for loc in you.currentLocation.adjLocations:
                if loc.isName(target):
                    foundLoc = True
                    prevLoc = you.currentLocation
                    you.currentLocation = loc
                    break

            if not foundLoc:
                print(f'"{target}" is not a valid location.')
            else:
                you.currentLocation.showPlayer()
        elif verb.lower() == "inventory":
            if len(you.inventory) > 0:
                print("You have the following items in your inventory:")
                for item in you.inventory:
                    print(f"   - {item.name}")
            else:
                print("You have no items in your inventory.")
        elif verb.lower() == "help":
            for action in helpActionList:
                print(action)
        else:
            if target.lower().strip() == "":
                print("unknown command... try: h or help")
                # print(f'What would you like to "{verb.lower()}"?')
            else:
                tInter = you.currentLocation.getInteractable(target.lower())

                if tInter:
                    if not tInter.doInteraction(you, verb.lower()):
                        print(f'"{verb}" is not a valid action.')
                else:
                    print(f'"{target}" is not a valid object.')


if __name__ == "__main__":
    main()
