import hashlib
import os
import sys
import getpass
import random
import time
import requests
import itertools
from threading import Thread
from checker.blacklist_utils import load_blacklist
from colorama import init, Fore, Style
from zxcvbn import zxcvbn
from datetime import datetime
from pyfiglet import Figlet

# Initialize colorama
init(autoreset=True)

# ----- Loading Animation -----
def show_loading_animation(message="🔐 Initializing CredSentinel...", delay=0.1):
    done_flag = {'stop': False}
    def animate():
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if done_flag['stop']:
                break
            print(f'\r{message} {c}', end='', flush=True)
            time.sleep(delay)
        print('\r' + ' ' * (len(message) + 5) + '\r', end='')
    t = Thread(target=animate)
    t.start()
    return t, done_flag

# ----- Password Evaluation Delay Animation -----
def show_checking_animation():
    done = {'stop': False}
    def animate():
        for c in itertools.cycle(['.', '..', '...']):
            if done['stop']:
                break
            print(f"\r🔎 Checking password{c}", end='', flush=True)
            time.sleep(0.4)
        print('\r' + ' ' * 30 + '\r', end='')
    t = Thread(target=animate)
    t.start()
    return t, done

# ----- Load Commom Passwords -----
def load_blacklist():
    path = os.path.join(os.path.dirname(__file__), "common_passwords.txt")
    if not os.path.exists(path):
        print(Fore.RED + "❌ common_passwords.txt not found.")
        sys.exit(1)
    with open(path, "r", encoding="latin-1") as f:
        passwords = [line.strip() for line in f if line.strip()]
        return set(passwords), passwords
        
blacklist_set, blacklist_list = load_blacklist()

# ----- Strength bar -----
def strength_meter(score):
    if score == -1:
        return Fore.RED + "[XXXX] BLACKLISTED" + Style.RESET_ALL

    levels = [
        (Fore.RED, "Very Weak"),
        (Fore.YELLOW, "Weak"),
        (Fore.LIGHTYELLOW_EX, "Average"),
        (Fore.CYAN, "Strong"),
        (Fore.GREEN, "Very Strong")
    ]

    color, label = levels[score]
    bars = "#" * score
    spaces = " " * (4 - score)
    return color + f"[{bars}{spaces}] {score}/4 → {label}" + Style.RESET_ALL

# ----- Blacklist level indicator -----
def check_blacklist_level(password, blacklist_set, blacklist_list):
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


# ---------- HIBP API (K-Anonymity) ----------
def check_pwned_api(password):
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        res = requests.get(url)
        hashes = (line.split(":") for line in res.text.splitlines())
        for h, count in hashes:
            if h == suffix:
                return int(count)
        return 0
    except:
        return -1  # Indicates API error


password_warnings = [
    # General tips
    "⚠️ Never reuse passwords across multiple accounts.",
    "🔒 Use a long, unpredictable passphrase instead of a short password.",
    "❗ Avoid names, birthdays, or dictionary words.",
    "🧠 Longer passwords are exponentially stronger!",
    "💡 Use a password manager to store complex passwords securely.",
    "🚫 '123456' and 'password' are hacker favorites!",
    "👻 Obfuscating simple passwords won't protect you — use real entropy.",
    "🛡️ Enable two-factor authentication wherever possible.",
    "📵 Don’t share your passwords — even with friends.",
    "🕵️‍♂️ Passwords leaked once are never safe again.",

    # OWASP Guidelines
    "📚 Use passwords that are at least 12 characters long.",
    "📚 Avoid password complexity rules that encourage predictable patterns.",
    "🔁 Avoid frequent forced password resets — they lead to weaker reuse.",
    "🧠 Encourage passphrases: a mix of unrelated words is strong and memorable.",
    "🧪 Always hash passwords securely using bcrypt, scrypt, or Argon2.",

    # NIST Guidelines
    "📖 Allow users to use any printable characters — don't restrict special symbols.",
    "📖 Don't require composition rules — let users choose length over complexity.",
    "📬 Check passwords against known breached lists like HaveIBeenPwned.",
    "📐 Use rate limiting to prevent brute-force attacks instead of user lockouts.",
    "🧩 Don't use password hints or knowledge-based questions — they're insecure."
]

# -------- Main Function --------
def main():
    # Load animation before blacklist
    anim, flag = show_loading_animation()
    time.sleep(1.5)
    flag['stop'] = True
    anim.join()

    # Banner
    user = getpass.getuser()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    figlet = Figlet(font='slant')
    print(Fore.GREEN + figlet.renderText('CredSentinel'))
    print(Fore.LIGHTGREEN_EX + "🔐 Welcome to Password Strength & Breach Analyzer!")
    print(Fore.LIGHTGREEN_EX + f"👤 Logged in as: {user}")
    print(Fore.LIGHTGREEN_EX + f"🕒 Session Started: {now}")
    print(Fore.YELLOW + "💡 Type 'exit' or 'quit' to end the session.\n")
    print(Fore.LIGHTBLUE_EX + "-" * 40)

    while True:
        password = input(Fore.LIGHTGREEN_EX + "Enter your password: ").strip()

        if not password:
            print(Fore.YELLOW + "⚠️ No password entered. Try again.\n")
            continue
        if password.lower() in ['exit', 'quit']:
            print(Fore.MAGENTA + "\n👋 Exiting CredSentinel. Stay secure!\n")
            break

        anim, flag = show_checking_animation()
       
        # Score and entropy
        result = zxcvbn(password)
        crack_time = result['crack_times_display']['offline_fast_hashing_1e10_per_second']
        score = result['score']

        # Blacklist check
        level, color = check_blacklist_level(password,blacklist_set,blacklist_list)

        # Breach check
        breach_count = check_pwned_api(password)

        # Force score to -1 if blacklisted
        if password in blacklist_set or breach_count > 0:
            score = -1

        
        flag['stop'] = True
        anim.join()

        # ----------Output----------------
        print(color + f"📛 Blacklist Check: {level}")

        # Handle blacklist override
        if password in blacklist_set:
            score = -1  # Force to blacklisted level

        print(Fore.GREEN + f"📊 Strength Meter: {strength_meter(score)}")

        print(Fore.GREEN + f"⏱️ Estimated Crack Time: {crack_time}")
        if breach_count == -1:
            print(Fore.YELLOW + "⚠️ HIBP check failed (network issue).")
        elif breach_count > 0:
            print(Fore.RED + f"❗ Found in breaches {breach_count} times on HaveIBeenPwned!")
        else:
            print(Fore.GREEN + "✅ Not found in public breaches (HIBP).")

        #print(Fore.LIGHTBLACK_EX + f"Example bcrypt hash: {hashed[:40]}...")
       
        # Tip of the Day
        tip = random.choice(password_warnings)
        print(Fore.LIGHTYELLOW_EX + f"\n💡 Tip: {tip}\n")

if __name__ == "__main__":
    main()
