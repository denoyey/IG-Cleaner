#  GITHUB: https://github.com/denoyey/IG-Cleaner

# -*- coding: utf-8 -*-
# This file is part of IG-Cleaner.
# It is released under the MIT License.
# See the LICENSE file for more details.

import os, sys, platform, subprocess, logging, random, itertools, time, math, json, pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from rich.text import Text
from rich.console import Console


class LogoPrinter:
    def __init__(self, console: Console):
        self.console = console
        self.colors = [
            "bold bright_cyan",
            "bold bright_green",
            "bold bright_blue",
            "bold bright_magenta",
            "bold bright_yellow",
        ]
        random.shuffle(self.colors)

    def print_logo(self):
        logo = r"""
    .___  ________          _________ .__                                     
    |   |/  _____/          \_   ___ \|  |   ____ _____    ____   ___________ 
    |   /   \  ___   ______ /    \  \/|  | _/ __ \\__  \  /    \_/ __ \_  __ \
    |   \    \_\  \ /_____/ \     \___|  |_\  ___/ / __ \|   |  \  ___/|  | \/
    |___|\______  /          \______  /____/\___  >____  /___|  /\___  >__|   
                \/                  \/          \/     \/     \/     \/       
            Version: 1.0.0 || Github: github.com/denoyey/IG-Cleaner
        IG-Cleaner - A tool to unfollow users on Instagram automatically.
        """
        lines = logo.strip("\n").split("\n")
        color_cycle = itertools.cycle(self.colors)
        for line in lines:
            style = next(color_cycle)
            self.console.print(Text(line, style=style))


class LoggerManager:
    class DayChangeHandler(logging.FileHandler):
        def __init__(self, filename, encoding=None):
            super().__init__(filename, encoding=encoding)
            self.last_date = self._get_last_log_date(filename)

        def _get_last_log_date(self, filename):
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, encoding="utf-8") as f:
                    for line in reversed(f.readlines()):
                        try:
                            date_str = line.split(" - ")[0]
                            return datetime.strptime(
                                date_str, "%Y-%m-%d %H:%M:%S"
                            ).date()
                        except:
                            continue
            return None

        def emit(self, record):
            current_date = datetime.fromtimestamp(record.created).date()
            if self.last_date and self.last_date != current_date and self.stream:
                self.stream.write("\n\n")
            self.last_date = current_date
            super().emit(record)

    def __init__(self, log_file="logfile.log"):
        self.log_dir = "log"
        self._ensure_log_dir()
        self.log_file = os.path.join(self.log_dir, log_file)
        self.logger = self._setup_logger()

    def _ensure_log_dir(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def _setup_logger(self):
        logger = logging.getLogger("core_logger")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = self.DayChangeHandler(self.log_file, encoding="utf-8")
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
                )
            )
            logger.addHandler(handler)
        return logger

    def cleanup(self, max_kb=500):
        if (
            os.path.exists(self.log_file)
            and os.path.getsize(self.log_file) > max_kb * 1024
        ):
            for h in logging.root.handlers[:]:
                logging.root.removeHandler(h)
                h.close()
            open(self.log_file, "w", encoding="utf-8").close()


class ConsoleHelper:
    def __init__(self):
        self.console = Console()
        self.logo = LogoPrinter(self.console)
        self.cmd = None

    def prompt_choice(self, prompt, choices=None):
        try:
            while True:
                response = self.console.input(prompt).strip()
                if not choices or response.lower() in [c.lower() for c in choices]:
                    return response
                self.print(
                    f"❌ Invalid choice. Options: {', '.join(choices)}", style="red"
                )
        except EOFError:
            self.print("[red]\n\n[!] Input aborted or unavailable. Exiting...[/red]")
            exit()

    def print(self, msg, style=None):
        self.console.print(f"[{style}]{msg}[/{style}]" if style else msg)


class CommandRunner:
    def __init__(self, console, logger):
        self.console, self.logger = console, logger
        self.is_windows = platform.system() == "Windows"

    def clear_screen(self):
        subprocess.run("cls" if self.is_windows else "clear", shell=True)

    def run(self, cmd, success="", fail=""):
        try:
            subprocess.check_call(cmd)
            if success:
                self.console.print(success, "green")
        except subprocess.CalledProcessError as e:
            if fail:
                self.console.print(f"{fail} {e}", "red")
            self.logger.error(f"{fail} {e}")
            sys.exit(1)


class DependencyInstaller:
    def __init__(self, console, logger, packages=None):
        self.console, self.logger, self.packages = console, logger, packages or []

    def check_and_install(self):
        self.console.print("\n>> Checking Python packages...", "cyan")
        for pkg in self.packages:
            try:
                __import__(pkg)
                self.console.print(f"[✓] {pkg} already installed.", "green")
            except ImportError:
                self.console.print(f"[✓] {pkg} missing. Installing...", "yellow")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
                    self.console.print(f"[✓] {pkg} installed.", "green")
                except subprocess.CalledProcessError:
                    self.console.print(f"Failed to install {pkg}", "red")
                    self.logger.error(f"Could not install {pkg}")
                    sys.exit(1)


class MainMenu:
    def __init__(self, console, logger, cmd, logo, deps, system):
        self.console = console
        self.logger = logger
        self.cmd = cmd
        self.logo = logo
        self.deps = deps
        self.system = system
        self.options = {
            "1": (
                "[bold bright_cyan]Auto Unfollow: All Followers[/bold bright_cyan]",
                self.start_unfollow,
            ),
            "2": (
                "[bold bright_green]Auto Unfollow: Only Non-Followers[/bold bright_green]",
                self.unfollow_non_followers,
            ),
            "3": (
                "[bold bright_blue]Export Followers/Following List[/bold bright_blue]",
                self.export_follow_data,
            ),
            "4": (
                "[bold bright_magenta]Check dependencies (REQUIRED)[/bold bright_magenta]",
                self.check_dependencies,
            ),
            "5": (
                "[bold bright_yellow]Settings & Limits[/bold bright_yellow]",
                self.settings_menu,
            ),
            "0": (
                "[bold bright_red]Exit[/bold bright_red]",
                self.exit_program,
            ),
        }

    def display_menu(self):
        self.cmd.clear_screen()
        self.logo.print_logo()
        self.console.print("[[bold bright_white]" + "=" * 40 + "[/bold bright_white]]")
        self.console.print(
            "[bold bright_white]               MAIN MENU[/bold bright_white]"
        )
        self.console.print(
            "[[bold bright_white]" + "=" * 40 + "[/bold bright_white]]\n"
        )
        for key, (desc, _) in self.options.items():
            self.console.print(f"[{key}]. {desc}")

    def handle_choice(self, choice):
        action = self.options.get(choice)
        if action is None:
            self.console.print(
                "\n[red]❌ Invalid option. Please choose from the list.[/red]"
            )
            input("\nPress Enter to continue...")
            return
        if choice != "4" and not self.system.deps_ready:
            self.console.print(
                "\n[red]❗Dependencies have not been checked. Please select option 2 first.[/red]"
            )
            input("\nPress Enter to continue...")
            return
        self.cmd.clear_screen()
        self.logo.print_logo()
        self.logger.info(f"Menu selected: {action[0]}")
        try:
            action[1]()
        except Exception as e:
            self.console.print(f"[red]❌ Error while executing option:[/red] {e}")
            self.logger.exception("An error occurred during execution")

    def show(self):
        try:
            while True:
                self.display_menu()
                choice = self.console.prompt_choice(
                    "\n[bold bright_white][>] Select: [/bold bright_white]"
                ).strip()
                self.handle_choice(choice)
        except KeyboardInterrupt:
            self.console.print(
                "\n\n[red]✋ Program interrupted by user. Exiting...[/red]\n"
            )
            sys.exit(0)
        except Exception as e:
            self.console.print(f"\n[red]❌ Unexpected error:[/red] {e}")
            self.logger.exception("Unhandled exception")
            sys.exit(1)

    def get_chrome_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        user_data_dir = os.path.join(os.getcwd(), "chrome_profile_ig_cleaner")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        system_os = platform.system()
        if system_os == "Windows":
            driver_path = os.path.join("drivers", "chromedriver.exe")
        elif system_os == "Linux":
            driver_path = os.path.join("drivers", "chromedriver")
        else:
            raise Exception(f"Unsupported OS: {system_os}")
        if not os.path.exists(driver_path):
            raise FileNotFoundError(f"ChromeDriver not found at: {driver_path}")
        service = Service(driver_path)
        try:
            return webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            self.console.print(f"[red]❌ Failed to start ChromeDriver: {e}[/red]")
            raise

    def start_unfollow(self):
        config_path = "settings.json"
        if not os.path.exists(config_path):
            self.console.print(
                "[yellow]⚠️ No settings file found. Using default values.[/yellow]"
            )
            settings = {
                "MAX_SAFE_LIMIT": 150,
                "BATCH_DELAY": 20,
                "SLEEP_BETWEEN": [2, 5],
                "SLEEP_AFTER_BATCH": 60,
            }
        else:
            with open(config_path, "r") as f:
                settings = json.load(f)
        BATCH_DELAY = settings.get("BATCH_DELAY", 20)
        SLEEP_BETWEEN = tuple(settings.get("SLEEP_BETWEEN", [2, 5]))
        SLEEP_AFTER_BATCH = settings.get("SLEEP_AFTER_BATCH", 60)
        MAX_SAFE_LIMIT = settings.get("MAX_SAFE_LIMIT", 150)
        self.console.print("[yellow]🚀 Starting Instagram unfollow process...[/yellow]")
        try:
            driver = self.get_chrome_driver()
        except Exception as e:
            self.console.print(f"[red]❌ Failed to start ChromeDriver: {e}[/red]")
            time.sleep(3)
            return
        self.console.print("[cyan]🌐 Opening Instagram login...[/cyan]")
        driver.get("https://www.instagram.com/accounts/login/")
        self.console.print(
            "[bold yellow]💬 Please log in manually in the browser window.[/bold yellow]"
        )
        WebDriverWait(driver, 300).until(
            lambda d: d.current_url and "/login" not in d.current_url
        )
        time.sleep(1.5)
        username = self.console.prompt_choice(
            "\n🔑 Enter your Instagram username (without @): "
        )
        if not username:
            self.console.print("[red]❌ Username cannot be empty.[/red]")
            driver.quit()
            time.sleep(3)
            return
        driver.get(f"https://www.instagram.com/{username}/")
        try:
            wait = WebDriverWait(driver, 10)
            elem = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//header//a[contains(@href,'/following')]/span/span")
                )
            )
            raw_count = elem.get_attribute("title") or elem.text
            if not raw_count:
                self.console.print(
                    "[red]⚠️ Failed to fetch following count. Make sure your account is public and fully loaded.[/red]"
                )
                time.sleep(5)
                driver.quit()
                return

            def parse_number(text):
                text = text.lower().replace(",", "").strip()
                return int(
                    float(text.replace("k", "").replace("jt", ""))
                    * (1000 if "k" in text else 1_000_000 if "jt" in text else 1)
                )

            total_following = parse_number(raw_count)
            self.console.print(
                f"[green]📊 Detected following: {total_following}[/green]"
            )
        except Exception as e:
            self.console.print(f"[red]❌ Failed to retrieve following count: {e}[/red]")
            driver.quit()
            return
        try:
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//a[contains(@href, '/following') and descendant::span[contains(text(), 'following') or contains(text(), 'Mengikuti')]]",
                    )
                )
            ).click()
            time.sleep(3)
        except Exception as e:
            self.console.print(f"[red]❌ Could not open following list: {e}[/red]")
            driver.quit()
            return
        self.console.print("[blue]📥 Fetching following list...[/blue]")
        scroll_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@role='dialog']//div[contains(@style, 'overflow')]")
            )
        )
        last_height = 0
        while True:
            height = driver.execute_script(
                "arguments[0].scrollTo(0, arguments[0].scrollHeight); return arguments[0].scrollHeight;",
                scroll_box,
            )
            if height == last_height:
                break
            last_height = height
            time.sleep(1)
        clicked_buttons = set()
        total_unfollowed = 0
        try:
            while total_unfollowed < total_following:
                unfollowed = 0
                remaining = total_following - total_unfollowed
                UNFOLLOW_LIMIT = min(MAX_SAFE_LIMIT, remaining)
                est_time = math.ceil(
                    (UNFOLLOW_LIMIT / BATCH_DELAY) * SLEEP_AFTER_BATCH
                    + UNFOLLOW_LIMIT * sum(SLEEP_BETWEEN) / 2
                )
                self.console.print(
                    f"\n[blue]🔒 Batch unfollow limit: {UNFOLLOW_LIMIT}[/blue]"
                )
                self.console.print(
                    f"[cyan]⏱️ Estimated time: ~{est_time // 60} minutes[/cyan]"
                )
                for i, btn in enumerate(
                    scroll_box.find_elements(By.XPATH, ".//button")
                ):
                    if unfollowed >= UNFOLLOW_LIMIT:
                        break
                    if i in clicked_buttons:
                        continue
                    try:
                        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                        time.sleep(1)
                        btn.click()
                        clicked_buttons.add(i)
                        try:
                            WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable(
                                    (
                                        By.XPATH,
                                        "//button[contains(text(), 'Unfollow') or contains(text(), 'Berhenti')]",
                                    )
                                )
                            ).click()
                        except:
                            pass
                        unfollowed += 1
                        total_unfollowed += 1
                        self.console.print(
                            f"[green]{datetime.now().strftime('%H:%M:%S')} ✅ Unfollowed: {unfollowed}/{UNFOLLOW_LIMIT}[/green]"
                        )
                        time.sleep(random.uniform(*SLEEP_BETWEEN))

                        if unfollowed % BATCH_DELAY == 0:
                            self.console.print(
                                "[yellow]⏸️ Cooling down for a minute...[/yellow]"
                            )
                            time.sleep(SLEEP_AFTER_BATCH)
                    except Exception as e:
                        self.console.print(f"[red]⚠️ Error during unfollow: {e}[/red]")
                        time.sleep(2)
                        continue
                if total_unfollowed >= total_following:
                    self.console.print(
                        "[green]✅ All followings have been unfollowed.[/green]"
                    )
                    break
                self.console.print(
                    "\n[bold red]⚠️ WARNING: Continuing to unfollow in large batches may lead to account restrictions or temporary ban by Instagram![/bold red]"
                )
                answer = (
                    input(
                        "\n❓ Do you want to continue with the next 150 unfollows? (y/n): "
                    )
                    .strip()
                    .lower()
                )
                if answer != "y":
                    self.console.print(
                        "[bold yellow]↩️ Returning to main menu...[/bold yellow]"
                    )
                    break
        except KeyboardInterrupt:
            self.console.print("[red]🛑 Interrupted by user![/red]")
        finally:
            self.console.print("[bold green]🎉 Unfollow process complete![/bold green]")
            driver.quit()

    def unfollow_non_followers(self):
        config_path = "settings.json"
        default_settings = {
            "MAX_SAFE_LIMIT": 150,
            "BATCH_DELAY": 20,
            "SLEEP_BETWEEN": [2, 5],
            "SLEEP_AFTER_BATCH": 60,
        }
        if not os.path.exists(config_path):
            self.console.print(
                "[yellow]⚠️ No settings file found. Using default values.[/yellow]"
            )
            settings = default_settings
        else:
            with open(config_path, "r") as f:
                settings = json.load(f)
        BATCH_DELAY = settings.get("BATCH_DELAY", 20)
        SLEEP_BETWEEN = tuple(settings.get("SLEEP_BETWEEN", [2, 5]))
        SLEEP_AFTER_BATCH = settings.get("SLEEP_AFTER_BATCH", 60)
        MAX_SAFE_LIMIT = settings.get("MAX_SAFE_LIMIT", 150)
        self.console.print(
            "[yellow]🚀 Starting Non-Follower Unfollow process...[/yellow]"
        )
        try:
            driver = self.get_chrome_driver()
        except Exception as e:
            self.console.print(f"[red]❌ ChromeDriver error: {e}[/red]")
            return
        driver.get("https://www.instagram.com/accounts/login/")
        self.console.print("[bold yellow]💬 Please log in manually...[/bold yellow]")
        WebDriverWait(driver, 300).until(
            lambda d: d.current_url and "/login" not in d.current_url
        )
        username = self.console.prompt_choice(
            "🔑 Enter your Instagram username (without @): "
        )
        if not username:
            self.console.print("[red]❌ Username required.[/red]")
            driver.quit()
            return
        driver.get(f"https://www.instagram.com/{username}/")
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@href, '/followers')]")
                )
            ).click()
            time.sleep(2)
        except Exception as e:
            self.console.print(f"[red]❌ Failed to open followers: {e}[/red]")
            driver.quit()
            return
        self.console.print("[blue]📥 Fetching followers...[/blue]")
        try:
            scroll_box = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@role='dialog']//div[contains(@style, 'overflow')]",
                    )
                )
            )
        except:
            self.console.print("[red]❌ Timeout opening followers list.[/red]")
            driver.quit()
            return
        followers = set()
        last_height = 0
        while True:
            links = scroll_box.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and "instagram.com" in href:
                    uname = href.rstrip("/").split("/")[-1]
                    followers.add(uname)
            height = driver.execute_script(
                "arguments[0].scrollTo(0, arguments[0].scrollHeight); return arguments[0].scrollHeight;",
                scroll_box,
            )
            if height == last_height:
                break
            last_height = height
            time.sleep(1)

        self.console.print(f"[green]✅ Total followers: {len(followers)}[/green]")
        driver.get(f"https://www.instagram.com/{username}/")
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@href, '/following')]")
                )
            ).click()
            time.sleep(2)
        except Exception as e:
            self.console.print(f"[red]❌ Failed to open following: {e}[/red]")
            driver.quit()
            return
        self.console.print("[blue]📥 Fetching following...[/blue]")
        try:
            scroll_box = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@role='dialog']//div[contains(@style, 'overflow')]",
                    )
                )
            )
        except:
            self.console.print("[red]❌ Timeout opening following list.[/red]")
            driver.quit()
            return
        following = set()
        last_height = 0
        while True:
            links = scroll_box.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and "instagram.com" in href:
                    uname = href.rstrip("/").split("/")[-1]
                    following.add(uname)
            height = driver.execute_script(
                "arguments[0].scrollTo(0, arguments[0].scrollHeight); return arguments[0].scrollHeight;",
                scroll_box,
            )
            if height == last_height:
                break
            last_height = height
            time.sleep(1)
        self.console.print(f"[green]✅ Total following: {len(following)}[/green]")
        non_followers = [user for user in following if user not in followers]
        self.console.print(
            f"[magenta]👤 Non-followers to unfollow: {len(non_followers)}[/magenta]"
        )
        unfollowed = 0
        for i, user in enumerate(non_followers):
            if unfollowed >= MAX_SAFE_LIMIT:
                self.console.print("[yellow]🚫 Reached safe unfollow limit.[/yellow]")
                break
            try:
                driver.get(f"https://www.instagram.com/{user}/")
                time.sleep(2)
                btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//button[contains(text(),'Following') or contains(text(),'Mengikuti')]",
                        )
                    )
                )
                btn.click()
                confirm_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//button[contains(text(),'Unfollow') or contains(text(),'Berhenti')]",
                        )
                    )
                )
                confirm_btn.click()
                unfollowed += 1
                self.console.print(
                    f"[green]{datetime.now().strftime('%H:%M:%S')} ✅ Unfollowed @{user} ({unfollowed}/{MAX_SAFE_LIMIT})[/green]"
                )
                time.sleep(random.uniform(*SLEEP_BETWEEN))
                if unfollowed % BATCH_DELAY == 0:
                    self.console.print("[yellow]⏸️ Cooling down...[/yellow]")
                    time.sleep(SLEEP_AFTER_BATCH)
            except Exception as e:
                self.console.print(f"[red]⚠️ Failed to unfollow @{user}: {e}[/red]")
                continue
        self.console.print(
            "[bold green]🎉 Done! Non-followers have been unfollowed.[/bold green]"
        )
        driver.quit()

    def export_follow_data(self):
        def scroll_and_collect(
            driver, console, wait_time=0.75, max_scrolls=2000, mode="followers"
        ):
            users = set()
            actions = ActionChains(driver)
            try:
                xpath = (
                    "//a[contains(@href,'/followers')]/span"
                    if mode == "followers"
                    else "//a[contains(@href,'/following')]/span"
                )
                count_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                count_text = count_element.get_attribute("title") or count_element.text
                count_text = (
                    count_text.lower().replace(",", "").replace(".", "").strip()
                )
                match = re.search(r"\d+", count_text)
                if match:
                    total_users = int(match.group())
                    console.print(f"[green]📊 Total {mode}: {total_users}[/green]")
                else:
                    console.print(
                        f"[red]❌ Failed to detect total {mode} from: '{count_text}'[/red]"
                    )
                    return users
            except Exception as e:
                console.print(f"[red]❌ Failed to get {mode} count: {e}[/red]")
                return users
            try:
                dialog = WebDriverWait(driver, 100).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//div[@role='dialog']//div[contains(@style, 'overflow')]",
                        )
                    )
                )
            except TimeoutException:
                console.print(f"[red]❌ {mode} dialog not found.[/red]")
                return users
            console.print(f"\n[cyan][~] Collecting {mode} data...[/cyan]")
            for _ in range(7):
                actions.send_keys(Keys.TAB)
            actions.send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(wait_time)
            last_count = 0
            for _ in range(max_scrolls):
                links = dialog.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if href and "instagram.com" in href:
                        username = href.rstrip("/").split("/")[-1]
                        users.add(username)
                if len(users) > last_count:
                    console.print(
                        f"    → Collected: {len(users)} of {total_users} users..."
                    )
                    last_count = len(users)
                if len(users) >= total_users:
                    break
                actions.send_keys(Keys.PAGE_DOWN).perform()
                time.sleep(wait_time)
            actions.send_keys(Keys.END).perform()
            time.sleep(1.5)
            links = dialog.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and "instagram.com" in href:
                    username = href.rstrip("/").split("/")[-1]
                    users.add(username)
            if len(users) >= total_users:
                console.print(f"\n[green][✓] All {mode} collected![/green]")
            else:
                console.print(
                    f"[yellow]⚠️ Only collected {len(users)} of {total_users} {mode}.[/yellow]"
                )
            return users

        try:
            driver = self.get_chrome_driver()
        except Exception as e:
            self.console.print(f"[red]❌ ChromeDriver error: {e}[/red]")
            return
        try:
            driver.get("https://www.instagram.com/accounts/login/")
            self.console.print(
                "[bold yellow]💬 Please log in manually...[/bold yellow]"
            )
            WebDriverWait(driver, 100).until(
                lambda d: d.current_url and "/login" not in d.current_url
            )
            username = self.console.prompt_choice(
                "🔑 Enter your Instagram username (without @): "
            ).strip()
            if not username:
                self.console.print("[red]❌ Username is required.[/red]")
                time.sleep(3)
                return
            data_type = (
                self.console.prompt_choice(
                    "📤 Export (followers) or (following) ? ",
                    choices=["followers", "following"],
                )
                .lower()
                .strip()
            )
            if data_type not in ["followers", "following"]:
                self.console.print(
                    "[red]❌ Invalid input. Please enter 'followers' or 'following'.[/red]"
                )
                driver.quit()
                time.sleep(3)
                return
            export_format = (
                self.console.prompt_choice(
                    "💾 Format (csv / xlsx / json / txt) ? ",
                    choices=["csv", "xlsx", "json", "txt"],
                )
                .lower()
                .strip()
            )
            if export_format not in ["csv", "xlsx", "json", "txt"]:
                self.console.print(
                    "[red]❌ Invalid format. Choose from csv, xlsx, json, or txt.[/red]"
                )
                driver.quit()
                time.sleep(3)
                return
            os.makedirs("exports", exist_ok=True)
            driver.get(f"https://www.instagram.com/{username}/")
            time.sleep(2)
            self.console.print(f"\n[blue]📥 Opening {data_type} list...[/blue]")
            try:
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//a[contains(@href, '/{data_type}')]")
                    )
                ).click()
                time.sleep(2)
            except Exception as e:
                self.console.print(
                    f"[red]❌ Failed to open {data_type} list: {e}[/red]"
                )
                return
            self.console.print("[cyan]🔄 Collecting data...[/cyan]")
            users = scroll_and_collect(driver, self.console, mode=data_type)
            if not users:
                self.console.print(
                    f"[red]⚠️ No {data_type} found or failed to collect.[/red]"
                )
                return

            df = pd.DataFrame(sorted(users), columns=["username"])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"{username}_{data_type}_{timestamp}"
            filepath = os.path.join("exports", f"{base_filename}.{export_format}")
            try:
                if export_format == "csv":
                    df.to_csv(filepath, index=False, encoding="utf-8-sig")
                elif export_format == "xlsx":
                    df.to_excel(filepath, index=False)
                elif export_format == "json":
                    df.to_json(filepath, orient="records", indent=2)
                elif export_format == "txt":
                    with open(filepath, "w", encoding="utf-8") as f:
                        for user in df["username"]:
                            f.write(f"{user}\n")
            except Exception as e:
                self.console.print(f"[red]❌ Error saving file: {e}[/red]")
                return
            self.console.print(
                f"[green][✓] Exported {len(df)} {data_type} to {filepath}[/green]"
            )
        except Exception as e:
            self.console.print(f"[red]❌ Unexpected error: {e}[/red]")
        finally:
            driver.quit()
            input("\n[Press Enter to return to menu...]")

    def check_dependencies(self):
        self.console.print("\n[cyan]>> Rechecking dependencies...[/cyan]")
        self.system.setup_environment()
        self.deps.check_and_install()
        self.system.deps_ready = True

        deps_dir = ".meta"
        os.makedirs(deps_dir, exist_ok=True)

        try:
            flag_file = os.path.join(deps_dir, "deps_checked.flag")
            if os.path.exists(flag_file):
                os.remove(flag_file)
            with open(flag_file, "w") as f:
                f.write("Dependencies checked and ready.\n")
        except Exception as e:
            self.console.print(f"[red]❌ Error writing deps_checked flag: {e}[/red]")
            self.logger.error(f"Failed to write deps_checked flag: {e}")
            return

        self.console.print("\n[green][✓] Dependencies OK![/green]")
        self.console.print("\n[bold bright_white][ PRESS ENTER ][/bold bright_white]")
        input()

    def settings_menu(self):
        config_path = "settings.json"
        default_config = {
            "MAX_SAFE_LIMIT": 150,
            "BATCH_DELAY": 20,
            "SLEEP_BETWEEN": [2, 5],
            "SLEEP_AFTER_BATCH": 60,
        }
        if not os.path.exists(config_path):
            with open(config_path, "w") as f:
                json.dump(default_config, f, indent=4)
        with open(config_path, "r") as f:
            settings = json.load(f)
        self.console.print(
            "\n[bold bright_white]⚙️ Current Settings:[/bold bright_white]"
        )
        for key, val in settings.items():
            self.console.print(f"[cyan]- {key}: [white]{val}[/white][/cyan]")
        self.console.print(
            "\n[bold green]You can press Enter to skip and keep current values.[/bold green]"
        )
        for key in settings:
            user_input = self.console.prompt_choice(
                f"Set value for [yellow]{key}[/yellow] (current: {settings[key]}): "
            )
            if user_input.strip():
                try:
                    if key == "SLEEP_BETWEEN":
                        settings[key] = [int(i) for i in user_input.strip().split(",")]
                    else:
                        settings[key] = int(user_input)
                except ValueError:
                    self.console.print(
                        f"[red]❌ Invalid input for {key}. Keeping current value.[/red]"
                    )
        with open(config_path, "w") as f:
            json.dump(settings, f, indent=4)

        self.console.print("\n[green][✓] Settings updated successfully![/green]")
        input("\nPress Enter to return to menu...")

    def exit_program(self):
        self.cmd.clear_screen()
        self.console.print("[magenta]👋 Exiting. Goodbye![/magenta]\n")
        sys.exit(0)


class SystemSetup:
    def __init__(self):
        self.console = ConsoleHelper()
        self.logo = LogoPrinter(self.console.console)
        self.logger = LoggerManager("ig_cleaner.log").logger
        self.cmd = CommandRunner(self.console, self.logger)
        self.console.cmd = self.cmd
        self.deps_ready = os.path.exists(os.path.join(".meta", "deps_checked.flag"))
        self.deps = DependencyInstaller(
            self.console,
            self.logger,
            ["selenium", "rich", "requests", "pandas", "openpyxl"],
        )

    def log(self, msg, level="info", style=None):
        getattr(self.logger, level)(msg)
        self.console.print(msg, style)

    def setup_environment(self):
        if not self.cmd.is_windows:
            self.console.print("[cyan]🔧 Running apt update & upgrade...[/cyan]")
            self.cmd.run(["sudo", "apt", "update"])
            self.cmd.run(["sudo", "apt", "full-upgrade", "-y"])
            self.cmd.run(["sudo", "apt", "autoremove", "-y"])
            self.cmd.run(["sudo", "apt", "install", "python3-pip", "-y"])
        else:
            self.console.print("[yellow]⚠️ Skipping apt on Windows.[/yellow]")

    def run(self):
        try:
            self.cmd.clear_screen()
            self.logo.print_logo()
            self.log("✅ Setup initialized.", style="green")

            self.cmd.clear_screen()
            self.logo.print_logo()
            MainMenu(
                self.console, self.logger, self.cmd, self.logo, self.deps, self
            ).show()
        finally:
            LoggerManager().cleanup()


if __name__ == "__main__":
    SystemSetup().run()
