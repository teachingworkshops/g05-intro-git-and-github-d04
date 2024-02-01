def controlPanelUse(panel, player, item):
    if item == None:
        print("You flip a few switches, but nothing happens.")
    elif item.isName("wrench"):
        print(
            "You loosen the bolts on the control panel and remove the faceplate, exposing the components beneath."
        )

        panel.name = "dismantled control panel"
        # panel.desc = new description
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
        print("the radio needs a capacitor")
        return True
    elif item.isName("capacitor"):
        print("you fix the radio")

        radio.name = "radio (fixed)"
        radio.actions["use"] = radioUseAfterFixed
        player.inventory.remove(item)
        return True
    return False


def radioUseAfterFixed(radio, player, item):
    if not item == None:
        return False

    print("You use the radio to call for help.")
    player.fixedRadio = True
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
    if item == None:
        transmitter.onUse  # prints default use message, which says "You can't use this object."
        return True

    if item.isName("wrench"):
        print("You use the wrench to fix the transmitter.")

        transmitter.name = "transmitter (fixed)"
        player.fixedTransmitter = True
        # trandmitter.desc = new description
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

    correctCode = "1234"
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

        player.inventory.remove(item)
        player.currentLocation.getAdjLocation(
            "top of radio tower").hidden = False

        return True
