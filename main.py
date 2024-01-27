class Location:
    def __init__(self, name, desc, aliases = []):
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
        if (len(self.adjLocations) > 0):
            print("Nearby locations: ")
            for loc in self.adjLocations:
                print(f"    - {loc.name}")

    def isName(self, name: str) -> bool:
        return name == self.name or name in self.aliases

    def getInteractable(self, interName: str):
        if(type(interName) != str):
            raise ValueError("getInteractable must be given a string")

        for i in self.interactables:
            if i.isName(interName):
                return i
        return None

    def getAdjLocation(self, other):
        if(type(other) == str):
            searchVal = other
        elif (type(other) == Location):
            searchVal = other.name
        else:
            raise ValueError("getLocation must be given a Location or string")

        for loc in self.adjLocations:
            if loc.name == searchVal:
                return loc
        return None

    def isConnected(self, other):
        if (type(other) == str):
            searchVal = other
        elif (type(other) == Location):
            searchVal = other.name
        else:
            raise ValueError("isConnected must be given a Location or string")

        return searchVal in list(map(lambda loc: loc.name, self.adjLocations))


class Player:
    currentLocation: Location = Location("null", "")
    alive: bool = True
    inventory = []


class Item:
    def __init__(self, name, desc, aliases = []):
        self.name = name
        self.desc = desc
        self. aliases = aliases

    def __init__(self, inter):
        self.name = inter.name
        self.desc = inter.desc
        self.aliases = inter.aliases


class Interactable:
    def __init__(self, name, desc, aliases = [], hidden = False, gettable = False):
        self.name = name
        self.desc = desc
        self.aliases = aliases
        self.hidden = hidden
        self.gettable = gettable

        self.actions = {
            "use":      self.onUse,
            "examine":  self.onExamine,
            "get":      self.onGet
        }

        self.actionAliases = {
            "look":     "examine",
            "lookat":   "examine",
            "inspect":  "examine",
            "pickup":   "get",
            "take":     "get"
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
        if (alias):
            command = alias
        return self.actions.get(command)

    def newInteraction(self, name, func, aliases = []):
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
    def onGet(interactable, player, item = None):
        if interactable.gettable:

            if item == None:
                item = Item(interactable)

            print(f"You pick up {item.name}.")

            player.inventory.append(item)
            interactable.hidden = True

        else:
            print("You cannot pick up this object.")
            

def buildWorld():

    marsSurface = Location(
        "The surface",
        "the planet, outside of the base",
        ["mars", "surface", "outside"]
    )
    lander = Location(
        "Your lander",
        "your space ship (no fuel)",
        ["ship", "lander"]
    )
    baseEntrance = Location(
        "The Martian base",
        "the main chamber of the martian base",
        ["base", "mars base"]
    )
    baseHangar = Location(
        "The hangar",
        "the largest room in the base, there are some tools and a broken rover",
        ["hangar", "mars base hangar"]
    )

    lander.interactables = [
        Interactable(
            "A wrench",
            "A hefty steel wrench for removing bolts.",
            ["wrench", "spanner"],
            gettable = True
        ),
    ]

    control_panel = Interactable(
        "A control panel",
        "An panel covered in switches, dials, and lights.",
        ["control panel", "panel"],
    )
    control_panel.actions["use"] = lambda interactable, player: print("You try flipping a few switches, but nothing happens.")

    lander.interactables.append(control_panel)

    marsSurface.adjLocations = [
        lander,
        baseEntrance,
        baseHangar
    ]
    lander.adjLocations = [
        marsSurface
    ]
    baseEntrance.adjLocations = [
        marsSurface,
        baseHangar
    ]
    baseHangar.adjLocations = [
        baseEntrance,
        marsSurface
    ]
    
    you = Player
    you.currentLocation = marsSurface
    
    return you


def main():
    actionAliases = {
        "goto": "go",
        "enter": "go",
        "g": "go",
        "inv": "inventory",
        "items": "inventory",
        "i": "inventory"
    }

    you = buildWorld()
    print("You are on", you.currentLocation.name)
    prevLoc = None
    while you.alive:
        you.currentLocation.showPlayer()

        userText = input()
        userWords = userText.split(" ")
        verb = userWords[0]
        target = userText[len(verb) + 1 :]

        lookedUpAction = actionAliases.get(verb.lower())
        if lookedUpAction:
            verb = lookedUpAction

        if verb.lower() == "go":
            foundLoc = False
            if target.lower() == "back" and prevLoc:
                if (you.currentLocation.isConnected(prevLoc)):
                    foundLoc = True
                    you.currentLocation, prevLoc = prevLoc, you.currentLocation

            for loc in you.currentLocation.adjLocations:
                if loc.isName(target):
                    foundLoc = True
                    prevLoc = you.currentLocation
                    you.currentLocation = loc
                    break

            if not foundLoc:
                print(f"\"{target}\" is not a valid location.")
        elif verb.lower() == "inventory":
            if len(you.inventory) > 0:
                print("You have the following items in your inventory:")
                for item in you.inventory:
                    print(f"   - {item.name}")
            else:
                print("You have no items in your inventory.")
        else:
            if target.lower().strip() == "":
                print(f"What would you like to \"{verb.lower()}\"?")
            else:
                tInter = you.currentLocation.getInteractable(target.lower())

                if tInter:
                    if not tInter.doInteraction(you, verb.lower()):
                        print(f"\"{verb}\" is not a valid action.")
                else:
                    print(f"\"{target}\" is not a valid object.")

if __name__ == "__main__":
    main()
