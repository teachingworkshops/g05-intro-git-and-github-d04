class Location:
    def __init__(self, name, desc, aliases = []):
        self.name = name
        self.description = desc
        self.aliases = aliases

    def showPlayer(self):
        print(self.name + " " + self.description)
        if len(self.interactables) != 0:
            print("Objects nearby:")
            for item in self.interactables:
                print("    - " + item.name)
        if (len(self.adjLocations) > 0):
            print("Nearby locations: ")
            for loc in self.adjLocations:
                print(f"    - {loc.name}")

    def isName(self, name: str) -> bool:
        return name == self.name or name in self.aliases

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

    name = ""
    description = ""
    adjLocations = []
    aliases = []
    interactables = []


class Interactable:
    def __init__(self, name):
        self.name = name

    name = "interactable"
    desc = "description of interactable"
    actions = ["use"]
    actionAliases = {}


class Item:
    name = "item"


class player:
    currentLocation: Location = Location("null", "")
    alive: bool = True



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

    lander.interactables = [Interactable("wrench")]

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
    
    you = player
    you.currentLocation = marsSurface
    
    return you


def main():
    actionAliases = {"goto": "go"}
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
        else:
            print(f"\"{verb}\" is not a valid action.")
            # print actions


if __name__ == "__main__":
    main()
