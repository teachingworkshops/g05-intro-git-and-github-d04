import json
import toml
import os
import re

import interactions
import time
from colorOutput import *

# clear term
os.system("cls||clear")


def print_ascii(fn):
    f = open(fn, "r")
    prRed("".join([line for line in f]))

class Location:
    def __init__(self, name, desc, longDesc, aliases=[], hidden=False):
        self.name = name
        self.description = desc
        self.longDescription = longDesc
        self.aliases = aliases
        self.hidden = hidden
        self.visited = False

        self.adjLocations = []
        self.interactables = []

    def showPlayer(self):
        # clear term
        os.system("cls||clear")

        ascii_file = f"art/{self.name.lower().replace(' ', '')}.txt"
        print_ascii(ascii_file)

        prYellow("Location: " + self.name)
        if self.visited or len(self.longDescription) == 0:
            prPurple(self.description + "\n")
        else:
            prPurple(self.longDescription + "\n")

        if len(self.interactables) != 0:
            prCyan("Objects nearby:")
            for inter in self.interactables:
                if not inter.hidden:
                    prCyan("    - " + inter.name)
        if len(self.adjLocations) > 0:
            prBlue("Nearby locations: ")
            for loc in self.adjLocations:
                if not loc.hidden:
                    prBlue(f"    - {loc.name}")
        self.visited = True

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
    def __init__(self):
        self.currentLocation: Location = Location("null", "", "")
        self.alive: bool = True
        self.inventory = []

        self.usedRadio = False
        self.fixedTransmitter = False

    def getItem(self, itemName):
        for item in self.inventory:
            if item.isName(itemName):
                return item
        return None

class Item:
    def __init__(self, name, desc, aliases=[]):
        self.name = name
        self.desc = desc
        self.aliases = aliases

    def __init__(self, inter):
        self.name = inter.name
        self.desc = inter.desc
        self.aliases = inter.aliases

    def isName(self, name: str) -> bool:
        return self.name.lower() == name.lower() or name.lower() in self.aliases


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

    def doInteraction(self, player: Player, command: str, item=None) -> bool:
        inter = self.getInteraction(command)
        if inter:
            inter(self, player, item)
            return True
        return False

    def getInteraction(self, command: str):
        if not self.hidden:
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
    def onUse(interactable, player, item=None):
        prRed("This object cannot be used.")

    @staticmethod
    def onExamine(interactable, player, item=None):
        prYellow(interactable.desc)

    @staticmethod
    def onGet(interactable, player, item=None):
        if interactable.gettable:
            if item == None:
                item = Item(interactable)

            prGreen(f"You picked up the {item.name}.")

            player.inventory.append(item)
            interactable.hidden = True

        else:
            prRed("You cannot pick up this object.")


def startScreen():
    ascii_file = f"art/title.txt"
    print_ascii(ascii_file)
    prGreen(
        "during a research operation on mars, a catastrophic storm struck causing the need for emergency evacuation, your crew left you behind leaving you to find a way to escape"
    )
    prPurple("press any key to start")
    input()
    os.system("cls" if os.name == "nt" else "clear")


def endScreen():
    ascii_file = f"art/escapelander.txt"
    print_ascii(ascii_file)
    prGreen("congratulations you have been rescued from mars!")
    prPurple("press any key to view credits")
    input()
    os.system("cls" if os.name == "nt" else "clear")
    ascii_file = f"art/credits.txt"
    print_ascii(ascii_file)


def buildWorld():
    options_file = "options.toml"
    options = toml.load(options_file)
    language = options["language"]["language"]
    world_filename = options["languages"][language]["world_json"]
    with open("lang/"+world_filename, "r") as f:
        data = json.load(f)
    locations = data["locations"]

    for key in locations.keys():
        adj = locations[key]["nearbyLocations"]
        interactables = locations[key]["interactables"]
        locations[key] = Location(
            key,
            locations[key]["description"],
            locations[key]["longdescription"],
            locations[key]["aliases"],
            locations[key]["hidden"],
        )
        locations[key].adjLocations = adj
        for i in interactables:
            if i:  # Check if i is not an empty string
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

            if i == "control panel":
                locations[key].interactables[-1].actions[
                    "use"
                ] = interactions.controlPanelUse
            elif i == "radio":
                locations[key].interactables[-1].actions[
                    "use"
                ] = interactions.radioUseBeforeFixed
            elif i == "rover":
                locations[key].interactables[-1].actions["use"] = interactions.roverUse
            elif i == "transmitter":
                locations[key].interactables[-1].actions[
                    "use"
                ] = interactions.transmitterUse
            elif i == "hangardoor":
                locations[key].interactables[-1].actions[
                    "use"
                ] = interactions.hangarDoorUseBeforeUnlocked
                locations[key].interactables[-1].actions[
                    "examine"
                ] = interactions.hangarDoorExamine
                locations[key].interactables[-1].actionAliases["open"] = "use"
            elif i == "keypad":
                locations[key].interactables[-1].actions["use"] = interactions.keypadUse
            elif i == "radio tower":
                locations[key].interactables[-1].actions[
                    "use"
                ] = interactions.radioTowerUse
            elif i == "terminal":
                locations[key].interactables[-1].actions[
                    "use"
                ] = interactions.terminalUse

    # reconstruct adj-locaations
    for key in locations.keys():
        nearbyLocs = []
        for i in range(len(locations[key].adjLocations)):
            nearbyLocs.append(locations[locations[key].adjLocations[i]])
        locations[key].adjLocations = nearbyLocs

    # convert adj-locations into real references
    you = Player()
    you.currentLocation = locations["mars"]
    return you


def main():
    actionAliases = {
        "goto": "go",
        "enter": "go",
        "g": "go",
        "cd": "go",  # silly bash command
        "grab": "get",
        "pickup": "get",
        "pick": "get",
        "mv": "get",  # silly bash command
        "i": "inventory",
        "inv": "inventory",
        "items": "inventory",
        "ls": "inventory",  # silly bash command
        "h": "help",
        "l": "look",
        "pwd": "look",  # silly bash command
    }

    helpActionList = [
        "g(o)/enter",
        "i(nventory)/items",
        "get/grab/pickup",
        "l(ook)",
        "use <inventory item> on <object in room>",
        "use <object in room>",
    ]

    you = buildWorld()
    startScreen()
    prPurple("You are on " + you.currentLocation.name)
    prevLoc = None
    you.currentLocation.showPlayer()
    while you.alive:
        if you.currentLocation.isName("escape lander"):
            print("You climb inside the escape vehicle.")
            break


        userText = input().strip(" ")

        # default action is look
        if len(userText) == 0:
            userText = "look"

        print()  # add space
        userWords = userText.split(" ")
        verb = userWords[0]
        target = userText[len(verb) + 1 :]

        lookedUpAction = actionAliases.get(verb.lower())
        if lookedUpAction:
            verb = lookedUpAction

        if verb == "look" and len(userWords) == 1:
            you.currentLocation.showPlayer()
        elif verb.lower() == "go":
            foundLoc = False
            if target.lower() == "back" or target.lower() == ".." and prevLoc:
                if you.currentLocation.isConnected(prevLoc):
                    foundLoc = True
                    you.currentLocation, prevLoc = prevLoc, you.currentLocation

            for loc in you.currentLocation.adjLocations:
                if not loc.hidden and loc.isName(target):
                    foundLoc = True
                    prevLoc = you.currentLocation
                    you.currentLocation = loc
                    break

            if not foundLoc:
                prRed(f'     "{target}" is not a valid location.')
            else:
                you.currentLocation.showPlayer()
                if you.currentLocation.isName("escape lander"):

                    os.system("cls||clear")
                    endScreen()
                    break
            # use command should be of the form "use <item> on <interactable>
        elif verb.lower() == "inventory":
            if len(you.inventory) > 0:
                prYellow("     You have the following items in your inventory:")
                for item in you.inventory:
                    prYellow(f"   - {item.name}")
            else:
                prRed("     You have no items in your inventory.")
        elif verb.lower() == "help":
            for action in helpActionList:
                prGreen("    " + action)
        elif verb.lower() == "use":
            matches = re.match(r"use\s+(.+)\s+on\s+(.+)", userText)
            if matches:
                usedItem = you.getItem(matches[1].lower())
                interactable = you.currentLocation.getInteractable(matches[2].lower())
                if not usedItem:
                    prRed(f"    You do not have a {matches[1]} in your inventory.")
                elif not interactable:
                    prRed(f"     There is no {matches[2]} nearby.")
                else:
                    if not interactable.doInteraction(you, "use", usedItem):
                        prRed(
                            f"     You cannot use a {matches[1]} on the {matches[2]}."
                        )
            else:
                if you.currentLocation.getInteractable(target):
                    you.currentLocation.getInteractable(target).doInteraction(
                        you, "use"
                    )
                else:
                    prRed(f'    {target} not found. Try "h" for help')
        else:
            if target.lower().strip() == "":
                prRed("     unknown command... try: h or help")
                # print(f'What would you like to "{verb.lower()}"?')
            else:
                tInter = you.currentLocation.getInteractable(target.lower())

                if tInter:
                    if not tInter.doInteraction(you, verb.lower()):
                        prRed(f'    "{verb}" is not a valid action.')
                else:
                    prRed(f'    "{target}" is not a valid object.')

    if you.alive:
        prGreen("####You are win####")
    else:
        prRed("####You are die####")


if __name__ == "__main__":
    main()
