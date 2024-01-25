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
    you = player
    mars = location("Mars", "the planet")
    lander = location("lander", "your space ship (no fuel)")
    mars.adjLocations = [lander]
    you.currentLocation = mars
    return you


def main():
    you = buildWorld()
    print("You are on", you.currentLocation.name)
    while you.alive:
        you.currentLocation.showPlayer()
        action = input()


if __name__ == "__main__":
    main()
