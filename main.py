import requests
import os
import threading
from queue import Queue
import random

# -------------- config --------------
THREADS = 25
TIMEOUT = 7
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/119.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15"
]
STATUS_OK = 200
STATUS_REDIRECT = [301, 302]
STATUS_FORBIDDEN = 403
DEFAULT_WORDLIST = os.path.join("db", "wordlist.txt")

# -------------- runtime config --------------
current_wordlist = DEFAULT_WORDLIST
word_queue = Queue()


# -------------- utils --------------
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"


def print_banner():
    clear_screen()
    banner = f"""
{Colors.RED}
 ██╗██████╗  █████╗ ███╗   ██╗
 ██║██╔══██╗██╔══██╗████╗  ██║
 ██║██████╔╝███████║██╔██╗ ██║
 ██║██╔══██╗██╔══██║██║╚██╗██║
 ██║██║  ██║██║  ██║██║ ╚████║
 ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
{Colors.GREEN}
    IRAN DIRECTORY SCANNER
    """
    print(banner)


# -------------- ui --------------
def show_menu():
    print_banner()
    print(f"{Colors.CYAN}================= MAIN MENU ================={Colors.RESET}\n")
    print(f"{Colors.YELLOW}Active wordlist:{Colors.RESET} {current_wordlist}\n")
    print(f"{Colors.GREEN}[1]{Colors.RESET} Start Scan")
    print(f"{Colors.YELLOW}[2]{Colors.RESET} Change Wordlist")
    print(f"{Colors.CYAN}[3]{Colors.RESET} Help")
    print(f"{Colors.RED}[0]{Colors.RESET} Exit\n")
    print(f"{Colors.CYAN}============================================{Colors.RESET}")
    choice = input(f"\nEnter your choice ({Colors.GREEN}0-3{Colors.RESET}): ")
    return choice


# -------------- core logic --------------
def scanner_worker(base_url):
    while not word_queue.empty():
        directory = word_queue.get()
        url = base_url + directory
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            response = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=False)

            if response.status_code == STATUS_OK:
                print(f"{Colors.GREEN}[200] {url}{Colors.RESET}")
            elif response.status_code == STATUS_FORBIDDEN:
                print(f"{Colors.YELLOW}[403] {url}{Colors.RESET}")
            elif response.status_code in STATUS_REDIRECT:
                print(f"{Colors.CYAN}[{response.status_code}] {url}{Colors.RESET}")
        except:
            pass
        finally:
            word_queue.task_done()


def scan_directories():
    clear_screen()
    print_banner()
    base_url = input(f"{Colors.CYAN}Enter target URL: {Colors.RESET}").strip()

    if not base_url.startswith("http"): base_url = "http://" + base_url
    if not base_url.endswith("/"): base_url += "/"

    if not os.path.exists(current_wordlist):
        print(f"{Colors.RED}Wordlist not found!{Colors.RESET}")
        input("Press Enter...")
        return

    with open(current_wordlist, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.strip(): word_queue.put(line.strip())

    print(f"\n{Colors.YELLOW}Starting fast scan with {THREADS} threads...{Colors.RESET}\n")

    for _ in range(THREADS):
        threading.Thread(target=scanner_worker, args=(base_url,), daemon=True).start()

    word_queue.join()
    print(f"\n{Colors.GREEN}Scan finished.{Colors.RESET}")
    input("Press Enter to return...")


def change_wordlist():
    global current_wordlist
    clear_screen()
    print_banner()
    new_path = input(f"{Colors.YELLOW}Enter new wordlist path: {Colors.RESET}").strip()
    if os.path.exists(new_path):
        current_wordlist = new_path
        print(f"{Colors.GREEN}Updated.{Colors.RESET}")
    else:
        print(f"{Colors.RED}Not found.{Colors.RESET}")
    input("Press Enter...")


def show_help():
    clear_screen()
    print_banner()
    print(f"{Colors.CYAN}Multi-threaded Directory Scanner Help{Colors.RESET}\n")
    print("This version uses concurrent threads to speed up the process.")
    input("\nPress Enter...")


# -------------- main loop --------------
def main():
    while True:
        choice = show_menu()
        if choice == "1":
            scan_directories()
        elif choice == "2":
            change_wordlist()
        elif choice == "3":
            show_help()
        elif choice == "0":
            break


if __name__ == "__main__":
    main()