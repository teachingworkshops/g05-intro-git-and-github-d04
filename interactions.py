import random

# generate the keypad code
random.seed()
keypadCode = str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9))

def controlPanelUse(panel, player, item):
    if item == None:
        print("You flip a few switches, but nothing happens.")
    elif item.isName("wrench"):
        print(
            "You loosen the bolts on the control panel and remove the faceplate, exposing the components beneath."
        )

        panel.name = "dismantled control panel"
        panel.desc = "Amidst the wires, you notice a capacitor."
        panel.actions["use"] = None
        panel.actions["examine"] = controlPanelExamineAfterOpened
        return True
    else:
        return False


def controlPanelExamineAfterOpened(panel, player, item):
    panel.onExamine(panel, player, item)
    player.currentLocation.getInteractable("capacitor").hidden = False


def radioUseBeforeFixed(radio, player, item):
    if item == None:
        print("The radio doesn't turn on. You open it up and examine the components. You notice that a capacitor has burnt out.")
        return True
    elif item.isName("capacitor"):
        print("You replace the capacitor.")

        player.fixedRadio = True
        radio.name = "radio (fixed)"
        radio.actions["use"] = radioUseAfterFixed
        player.inventory.remove(item)
        return True
    return False


def radioUseAfterFixed(radio, player, item):
    if not item == None:
        return False

    if player.fixedTransmitter:
        print("You use the radio to call for assistance. Shortly afterwards, a space craft lands outside!")

        mars = player.currentLocation.getAdjLocation("mars")
        lander = mars.getAdjLocation("lander")
        lander.hidden = True
        escape = mars.getAdjLocation("escape lander")
        escape.hidden = False
    else:
        print("All you hear is static.")

    return True


def roverUse(rover, player, item):
    if not item == None:
        return False

    hangar = player.currentLocation
    tower = hangar.getAdjLocation("antenna base")
    if tower:
        player.currentLocation = tower
        tower.hidden = False
        tower.showPlayer()
        print("You drove the rover over to the antenna base")
    else:
        print("You could use this rover to drive out to the radio tower.")

    return True


def transmitterUse(transmitter, player, item):
    if item == None and not player.fixedTransmitter:
        transmitter.onUse(
            player, item
        )  # prints default use message, which says "You can't use this object."
        return True
    if item.isName("wrench"):
        print("You repair the transmitter.")
        transmitter.name = "transmitter (fixed)"
        player.fixedTransmitter = True


        return True
    return False


def hangarDoorUseBeforeUnlocked(door, player, item):
    if not item == None:
        return False

    print("The door is securely shut.")
    return True


def hangarDoorUseAfterUnlocked(door, player, item):
    if not item == None:
        return False

    print("The door opens up, allowing entry to the hangar.")

    door.hidden = True
    player.currentLocation.getAdjLocation("base hangar").hidden = False
    return True


def hangarDoorExamine(door, player, item):
    door.onExamine(door, player, item)
    player.currentLocation.getInteractable("keypad").hidden = False


def keypadUse(keypad, player, item):
    if not item == None:
        return False

    correctCode = keypadCode
    numGuesses = 3

    print('Type "exit" to go back.')

    exit = False
    while not exit:
        userInput = input("Enter a 4-digit code: ").lower().strip()
        if userInput == "exit":
            exit = True
        elif userInput != correctCode:
            print("Incorrect!\n")
            numGuesses -= 1
            if numGuesses == 0:
                print(
                    "You have triggered the base's self-destruct mechanism. The entire facility instantly explodes."
                )
                player.alive = False
                exit = True
            else:
                print(
                    f"You have {numGuesses} {'attempts' if numGuesses > 1 else 'attempt'} remaining."
                )
        else:
            print("Success!\n")
            print("You hear the door leading to the hangar unlock.")
            keypad.hidden = True
            player.currentLocation.getInteractable("door").actions[
                "use"
            ] = hangarDoorUseAfterUnlocked
            exit = True

    return True


def radioTowerUse(tower, player, item):
    if item == None:
        return False

    if item.isName("ladder"):
        print("You prop the ladder up against the side of the tower.")
        print("climb to the top")

        player.inventory.remove(item)
        player.currentLocation.getAdjLocation("top of radio tower").hidden = False

        return True

def terminalUse(terminal, player, item):
    if item == None:
        print(f"Fortunately, whomever used this terminal last forgot to log out. There's an open text file that reads:\n\"Note to self: {keypadCode}\"")
    elif item.isName("wrench"):
        print("You smash up the terminal real good.")
        terminal.name = "terminal (broken)"
        terminal.desc = "It's damaged beyond repair. Maybe you shouldn't have done that..."
        terminal.actions["use"] = terminal.onUse

def smash(player, item):
    if item.name == "capacitor":
        item.name = "smashed capacitor"
        item.description = "The remains of what could have been a very useful and important component, reduced to a tiny pile of crushed ceramic, metal and plastic."
        print(f"For whatever reason, you decide to crush the capacitor beyond recognition. Are you happy now?")
        
    elif item.isName("ladder"):
        item.name = "smashed ladder"
        item.description = "The rungs that remain are too far apart to be remotely usable. Not much of a ladder anymore, really."
        print(f"You decide you've had enough of your ladder. After hammering away at the poor vertical convyance device for a few minutes, you come to your senses and cut it out.")
