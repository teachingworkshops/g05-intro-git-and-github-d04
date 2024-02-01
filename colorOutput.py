from colorama import Fore, Style


def prRed(prt):
    print(Fore.RED + f"{prt}" + Style.RESET_ALL)


def prGreen(prt):
    print(Fore.GREEN + f"{prt}" + Style.RESET_ALL)


def prYellow(prt):
    print(Fore.YELLOW + f"{prt}" + Style.RESET_ALL)


def prBlue(prt):
    print(Fore.BLUE + f"{prt}" + Style.RESET_ALL)


def prPurple(prt):
    print(Fore.MAGENTA + f"{prt}" + Style.RESET_ALL)


def prCyan(prt):
    print(Fore.CYAN + f"{prt}" + Style.RESET_ALL)


def prLightGray(prt):
    print(Fore.LIGHTWHITE_EX + f"{prt}" + Style.RESET_ALL)


def prBlack(prt):
    print(Fore.BLACK + f"{prt}" + Style.RESET_ALL)
