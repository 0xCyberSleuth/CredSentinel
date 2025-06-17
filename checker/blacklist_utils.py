import os
import sys
from colorama import Fore

def load_blacklist(limit=None):
    """
    Load common passwords from common_passwords.txt
    Returns both a set and a list for fast lookup and indexing.
    If limit is provided, trims the list to that many entries.
    """
    path = os.path.join(os.path.dirname(__file__), "../common_passwords.txt")

    if not os.path.exists(path):
        print(Fore.RED + "❌ Error: 'common_passwords.txt' not found.")
        sys.exit(1)

    with open(path, "r", encoding="latin-1") as f:
        passwords = [line.strip() for line in f if line.strip()]
    
    if limit:
        passwords = passwords[:limit]

    return set(passwords), passwords


def check_blacklist_level(password, blacklist_set, blacklist_list):
    """
    Checks if the password is in the blacklist and returns a risk level and associated color.
    """
    if password in blacklist_set:
        try:
            index = blacklist_list.index(password)
            if index < 10:
                return "Top 10 🔥", Fore.LIGHTRED_EX
            elif index < 100:
                return "Top 100 ⚠️", Fore.LIGHTRED_EX
            elif index < 500:
                return "Top 500 ⚠️", Fore.LIGHTRED_EX
            else:
                return f"In list (#{index})", Fore.CYAN
        except ValueError:
            return "In blacklist", Fore.CYAN
    else:
        return "✅ Not in common list", Fore.GREEN
