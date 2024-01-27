class location:
    def __init__(self, name, desc):
        self.name = name
        self.description = desc

    def showPlayer(self):
        print(self.name + " " + self.description)
        if len(self.interactables) != 0:
            print("Objects nearby:")
            for item in self.interactables:
                print("    " + item.name)

    name = ""
    description = ""
    adjLocations = []
    interactables = []


class interactable:
    def __init__(self, name):
        self.name = name

    name = "interactable"
    desc = "description of interactable"
    actions = ["use"]
    actionAliases = {}


class item:
    name = "item"


class player:
    currentLocation: location = location("null", "")
    alive: bool = True



def buildWorld():

    marsSurface = location("mars", "the planet, outside of the base")
    lander = location("lander", "your space ship (no fuel)")
    baseEntrance = location("martian base", "the main chamber of the martian base")
    baseHangar = location("base hangar", "the largest room in the base, there are some tools and a broken rover")

    lander.interactables = [interactable("wrench")]

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
            for l in you.currentLocation.adjLocations:
                if l.name.lower() == target:
                    you.currentLocation = l
                    break
        else:
            print("Invalid action")
            # print actions


if __name__ == "__main__":
    main()
