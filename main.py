class location:
    def __init__(self, name):
        self.name = name

    name = []
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
    currentLocation: location = location("null")


def buildWorld():
    you = player
    mars = location("Mars")
    you.currentLocation = mars
    return you


def main():
    you = buildWorld()
    print("You are on", you.currentLocation.name)


if __name__ == "__main__":
    main()
