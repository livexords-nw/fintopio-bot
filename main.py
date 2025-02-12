from datetime import datetime
import json
import time
from colorama import Fore
import requests
import random

class fintopia:
    BASE_URL = "https://api.fintopio.com/"
    HEADERS = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
        "connection": "keep-alive",
        "origin": "https://fintopio-tg.fintopio.com",
        "referer": "https://fintopio-tg.fintopio.com/",
        "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24", "Microsoft Edge WebView2";v="131"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    }

    def __init__(self):
        self.query_list = self.load_query("query.txt")
        self.token = None
        self.coins = 0
        self.config = self.load_config()

    def banner(self) -> None:
        """Displays the banner for the bot."""
        self.log("🎉 Fintopia Free Bot", Fore.CYAN)
        self.log("🚀 Created by LIVEXORDS", Fore.CYAN)
        self.log("📢 Channel: t.me/livexordsscript\n", Fore.CYAN)

    def log(self, message, color=Fore.RESET):
            print(Fore.LIGHTBLACK_EX + datetime.now().strftime("[%Y:%m:%d ~ %H:%M:%S] |") + " " + color + message + Fore.RESET)

    def load_config(self) -> dict:
        """
        Loads configuration from config.json.

        Returns:
            dict: Configuration data or an empty dictionary if an error occurs.
        """
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                self.log("✅ Configuration loaded successfully.", Fore.GREEN)
                return config
        except FileNotFoundError:
            self.log("❌ File not found: config.json", Fore.RED)
            return {}
        except json.JSONDecodeError:
            self.log("❌ Failed to parse config.json. Please check the file format.", Fore.RED)
            return {}

    def load_query(self, path_file: str = "query.txt") -> list:
        """
        Loads a list of queries from the specified file.

        Args:
            path_file (str): The path to the query file. Defaults to "query.txt".

        Returns:
            list: A list of queries or an empty list if an error occurs.
        """
        self.banner()

        try:
            with open(path_file, "r") as file:
                queries = [line.strip() for line in file if line.strip()]

            if not queries:
                self.log(f"⚠️ Warning: {path_file} is empty.", Fore.YELLOW)

            self.log(f"✅ Loaded {len(queries)} queries from {path_file}.", Fore.GREEN)
            return queries

        except FileNotFoundError:
            self.log(f"❌ File not found: {path_file}", Fore.RED)
            return []
        except Exception as e:
            self.log(f"❌ Unexpected error loading queries: {e}", Fore.RED)
            return []

    def login(self, index: int) -> None:
        self.log("🔒 Attempting to log in...", Fore.GREEN)

        if index >= len(self.query_list):
            self.log("❌ Invalid login index. Please check again.", Fore.RED)
            return

        token = self.query_list[index]
        req_url = f"{self.BASE_URL}auth/telegram?{token}"

        self.log(
            f"📋 Using token: {token[:10]}... (truncated for security)",
            Fore.CYAN,
        )

        headers = {**self.HEADERS}

        try:
            self.log("📡 Sending request to fetch user information...", Fore.CYAN)
            response = requests.get(req_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Mengambil token dari data respons
            auth_token = data.get("token", None)
            if auth_token:
                self.token = auth_token
                self.log("🔑 Token successfully retrieved.", Fore.GREEN)
            else:
                self.log("⚠️ Token not found in response.", Fore.YELLOW)
                return

            # === Request ke API fast/init ===
            init_url = f"{self.BASE_URL}fast/init"
            init_headers = {**headers, "Authorization": f"Bearer {self.token}"}
            init_response = requests.get(init_url, headers=init_headers)
            init_response.raise_for_status()
            init_data = init_response.json()

            # Ambil data balance dan profile
            balance_info = init_data.get("balance", {})
            profile_info = init_data.get("profile", {})

            if balance_info:
                self.log(f"💰 Balance: {balance_info.get('balance')}", Fore.GREEN)
            else:
                self.log("⚠️ Balance information not found in init response.", Fore.YELLOW)

            if profile_info:
                self.log("👤 Profile Information:", Fore.GREEN)
                self.log(f"🆔 ID: {profile_info.get('id')}", Fore.GREEN)
                self.log(f"📝 Name: {profile_info.get('name')}", Fore.GREEN)
                self.log(f"💬 Telegram Username: {profile_info.get('telegramUsername')}", Fore.GREEN)
            else:
                self.log("⚠️ Profile information not found in init response.", Fore.YELLOW)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to send login request: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
        except ValueError as e:
            self.log(f"❌ Data error (possible JSON issue): {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
        except KeyError as e:
            self.log(f"❌ Key error: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)

    def daily(self) -> bool:
        """Performs the daily check-in."""
        daily_url = f"{self.BASE_URL}daily-checkins"
        headers = {**self.HEADERS}
        init_headers = {**headers, "Authorization": f"Bearer {self.token}"}

        try:
            self.log("📡 Sending daily check-in request...", Fore.CYAN)
            response = requests.get(daily_url, headers=init_headers)
            
            if response.status_code == 200:
                self.log("✅ Daily check-in successful!", Fore.GREEN)
                return True
            else:
                self.log(f"❌ Daily check-in failed with status code: {response.status_code}", Fore.RED)
                self.log(f"📄 Response content: {response.text}", Fore.RED)
                return False

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to perform daily check-in: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {response.text}", Fore.RED)
            except Exception:
                pass
            return False
    
    def task(self) -> None:
        """Fetches tasks from the server and verifies tasks that are in progress."""
        tasks_url = f"{self.BASE_URL}hold/tasks"
        headers = {**self.HEADERS}
        init_headers = {**headers, "Authorization": f"Bearer {self.token}"}

        try:
            self.log("📡 Fetching tasks...", Fore.CYAN)
            response = requests.get(tasks_url, headers=init_headers)
            response.raise_for_status()
            data = response.json()

            # Tampilkan informasi daily reward
            daily = data.get("daily", {})
            if "reward" in daily:
                self.log(f"💰 Daily Reward: {daily['reward']}", Fore.GREEN)
            else:
                self.log("⚠️ Daily reward not found.", Fore.YELLOW)

            # Ambil dan tampilkan daftar tasks
            tasks = data.get("tasks", [])
            if not tasks:
                self.log("⚠️ No tasks available.", Fore.YELLOW)
                return

            self.log("📋 Listing tasks:", Fore.CYAN)
            for task in tasks:
                task_id = task.get("id")
                task_type = task.get("type")
                task_subtype = task.get("subtype")
                task_status = task.get("status")
                task_reward = task.get("rewardAmount")
                task_slug = task.get("slug")
                self.log(
                    f"🆔 Task ID: {task_id} | 📂 Type: {task_type} | 🔍 Subtype: {task_subtype} | 💎 Reward: {task_reward} | ⏳ Status: {task_status} | 🏷️ Slug: {task_slug}",
                    Fore.GREEN,
                )

                # Jika task berstatus "in-progress", verifikasi task tersebut
                if task_status == "in-progress":
                    verify_url = f"{self.BASE_URL}hold/tasks/{task_id}/verify"
                    self.log(f"🔍 Verifying task {task_id}...", Fore.CYAN)
                    verify_response = requests.post(verify_url, headers=init_headers)
                    verify_response.raise_for_status()
                    verify_data = verify_response.json()
                    if verify_data.get("status") == "verifying":
                        self.log(f"✅ Task {task_id} is verifying.", Fore.GREEN)
                    else:
                        self.log(f"⚠️ Unexpected verification status for task {task_id}: {verify_data}", Fore.YELLOW)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch or verify tasks: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {response.text}", Fore.RED)
            except Exception:
                pass
        except ValueError as e:
            self.log(f"❌ Data error: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {response.text}", Fore.RED)
            except Exception:
                pass
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {response.text}", Fore.RED)
            except Exception:
                pass
    
    def farm(self) -> None:
        """Claims farming rewards and starts farming."""
        claim_url = f"{self.BASE_URL}farming/claim"
        farm_url = f"{self.BASE_URL}farming/farm"
        headers = {**self.HEADERS, "Authorization": f"Bearer {self.token}"}

        try:
            # Langkah 1: Claim farming
            self.log("📡 Claiming farming rewards...", Fore.CYAN)
            claim_response = requests.post(claim_url, headers=headers)
            claim_response.raise_for_status()
            claim_data = claim_response.json()

            if claim_data.get("state") == "idling":
                self.log("✅ Farming claim successful. State is idling.", Fore.GREEN)
            else:
                self.log(f"⚠️ Unexpected farming claim state: {claim_data.get('state')}", Fore.YELLOW)

            # Langkah 2: Mulai farming
            self.log("🚜 Starting farming...", Fore.CYAN)
            farm_response = requests.post(farm_url, headers=headers)
            farm_response.raise_for_status()
            farm_data = farm_response.json()

            if farm_data.get("state") == "farming":
                self.log("✅ Farming started successfully!", Fore.GREEN)
                self.log(f"💰 Farmed amount: {farm_data.get('farmed')}", Fore.GREEN)
                timings = farm_data.get("timings", {})
                if timings:
                    start = timings.get("start")
                    finish = timings.get("finish")
                    left = timings.get("left")
                    self.log(f"⏳ Farming started at: {start}", Fore.GREEN)
                    self.log(f"⏰ Farming will finish at: {finish}", Fore.GREEN)
                    self.log(f"⏱️ Time left: {left}", Fore.GREEN)
            else:
                self.log(f"⚠️ Unexpected farming state: {farm_data.get('state')}", Fore.YELLOW)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to perform farming: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {claim_response.text}", Fore.RED)
            except Exception:
                pass
        except Exception as e:
            self.log(f"❌ An unexpected error occurred during farming: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {claim_response.text}", Fore.RED)
            except Exception:
                pass

    def game(self) -> None:
        """Handles game related functions."""
        
        def diamond_breath() -> None:
            """Plays the diamond-breath game."""
            endpoint = f"{self.BASE_URL}games/diamond-breath"
            headers = {**self.HEADERS, "Authorization": f"Bearer {self.token}"}
            
            try:
                self.log("📡 Fetching diamond-breath game info...", Fore.CYAN)
                get_response = requests.get(endpoint, headers=headers)
                get_response.raise_for_status()
                game_info = get_response.json()
                self.log("🎮 Diamond-breath game info retrieved.", Fore.GREEN)
                
                delay = random.randint(13, 15)
                self.log(f"⏱️ Waiting for {delay} seconds before playing diamond-breath...", Fore.CYAN)
                time.sleep(delay)
                
                payload = {"seconds": delay}
                self.log("📡 Sending diamond-breath play request...", Fore.CYAN)
                post_response = requests.post(endpoint, headers=headers, json=payload)
                post_response.raise_for_status()
                play_result = post_response.json()
                reward = play_result.get("reward")
                self.log(f"✅ Diamond-breath played. Reward: {reward}", Fore.GREEN)
                
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Failed to play diamond-breath: {e}", Fore.RED)
                try:
                    self.log(f"📄 Response content: {get_response.text}", Fore.RED)
                except Exception:
                    pass
            except Exception as e:
                self.log(f"❌ Unexpected error in diamond-breath: {e}", Fore.RED)
        
        def tap() -> None:
            """Plays the tap game."""
            state_endpoint = f"{self.BASE_URL}clicker/diamond/state"
            complete_endpoint = f"{self.BASE_URL}clicker/diamond/complete"
            headers = {**self.HEADERS, "Authorization": f"Bearer {self.token}"}
            
            try:
                self.log("📡 Fetching clicker diamond state...", Fore.CYAN)
                state_response = requests.get(state_endpoint, headers=headers)
                state_response.raise_for_status()
                state_data = state_response.json()
                self.log("🎮 Diamond state fetched.", Fore.GREEN)
                
                state_str = state_data.get("state", "unknown")
                clicks = state_data.get("clicks", "N/A")
                self.log(f"🆙 State: {state_str} | 👆 Clicks: {clicks}", Fore.GREEN)
                
                delay = random.randint(4, 8)
                self.log(f"⏱️ Waiting for {delay} seconds before completing tap...", Fore.CYAN)
                time.sleep(delay)
                
                self.log("📡 Sending tap complete request...", Fore.CYAN)
                complete_response = requests.post(complete_endpoint, headers=headers)
                complete_response.raise_for_status()
                self.log("✅ Tap completed successfully!", Fore.GREEN)
                
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Failed to complete tap game: {e}", Fore.RED)
                try:
                    self.log(f"📄 Response content: {state_response.text}", Fore.RED)
                except Exception:
                    pass
            except Exception as e:
                self.log(f"❌ Unexpected error in tap game: {e}", Fore.RED)
        
        def space_tappers() -> None:
            """Plays the space tappers game."""
            headers = {**self.HEADERS, "Authorization": f"Bearer {self.token}"}
            
            try:
                # Step 1: Ambil pengaturan game space-tappers
                settings_endpoint = f"{self.BASE_URL}hold/space-tappers/game-settings"
                self.log("📡 Fetching space tappers game settings...", Fore.CYAN)
                settings_response = requests.get(settings_endpoint, headers=headers)
                settings_response.raise_for_status()
                game_settings = settings_response.json()
                self.log(f"🎮 Space tappers settings retrieved: {game_settings}", Fore.GREEN)
                
                # Ambil nilai maksimum score dari game settings
                max_score = game_settings.get("maxScore", 57)
                # Kurangi nilai max_score secara acak antara 10 hingga 100
                reduction = random.randint(10, 50)
                score = max_score - reduction
                self.log(f"🎲 Calculated score: {score} (max {max_score} reduced by {reduction})", Fore.GREEN)
                
                # Step 2: Ambil boosts (jika diperlukan untuk log atau pemrosesan tambahan)
                boosts_endpoint = f"{self.BASE_URL}hold/boosts"
                self.log("📡 Fetching boosts...", Fore.CYAN)
                boosts_response = requests.get(boosts_endpoint, headers=headers)
                boosts_response.raise_for_status()
                boosts_data = boosts_response.json()
                self.log("🎮 Boosts data retrieved.", Fore.GREEN)
                
                # Step 3: Siapkan collectedGems secara acak
                gem_list = [
                    {"id": 1, "name": "quartz", "rarity": "c", "count": "56", "status": "available", "condition": None},
                    {"id": 2, "name": "turquoise", "rarity": "c", "count": "57", "status": "available", "condition": None},
                    {"id": 3, "name": "onyx", "rarity": "c", "count": "75", "status": "available", "condition": None},
                    {"id": 4, "name": "amethyst", "rarity": "s", "count": "27", "status": "available", "condition": None},
                    {"id": 5, "name": "topaz", "rarity": "s", "count": "56", "status": "available", "condition": None},
                    {"id": 6, "name": "opal", "rarity": "r", "count": "0", "status": "unavailable", "condition": {"key": "completed-wallet-task-1", "type": "complete-task", "count": 1, "subtype": "wallet"}},
                    {"id": 7, "name": "ruby", "rarity": "r", "count": "0", "status": "unavailable", "condition": {"key": "completed-wallet-task-1", "type": "complete-task", "count": 1, "subtype": "wallet"}},
                    {"id": 8, "name": "sapphire", "rarity": "er", "count": "0", "status": "unavailable", "condition": {"key": "completed-wallet-task-3", "type": "complete-task", "count": 3, "subtype": "wallet"}},
                    {"id": 9, "name": "emerald", "rarity": "er", "count": "0", "status": "unavailable", "condition": {"key": "completed-wallet-task-3", "type": "complete-task", "count": 3, "subtype": "wallet"}},
                    {"id": 10, "name": "diamond", "rarity": "ur", "count": "0", "status": "unavailable", "condition": {"key": "completed-wallet-task-5", "type": "complete-task", "count": 5, "subtype": "wallet"}}
                ]
                # Filter gem yang tersedia
                available_gems = [gem for gem in gem_list if gem["status"] == "available"]
                # Tentukan jumlah gem yang akan dikumpulkan (misal antara 1 sampai 3)
                num_gems = random.randint(1, min(3, len(available_gems)))
                selected_gems = random.sample(available_gems, num_gems)
                
                # Buat list collectedGems dengan jumlah masing-masing gem secara acak antara 1 hingga 5
                collected_gems = [{"gem": gem["name"], "count": random.randint(1, 5)} for gem in selected_gems]
                
                # Step 4: Siapkan payload dan kirim hasil game space-tappers
                payload = {
                    "score": score,
                    "collectedGems": collected_gems,
                    "additionalGame": False,
                    "additionalLiveBoosts": 0
                }
                self.log(f"📡 Sending space tappers result with payload: {payload}", Fore.CYAN)
                
                result_endpoint = f"{self.BASE_URL}hold/space-tappers/add-new-result"
                post_response = requests.post(result_endpoint, headers=headers, json=payload)
                post_response.raise_for_status()
                result_data = post_response.json()
                self.log(f"✅ Space tappers result submitted. Reward: {result_data.get('actualReward')}", Fore.GREEN)
                
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Failed in space tappers game: {e}", Fore.RED)
                try:
                    self.log(f"📄 Response content: {settings_response.text}", Fore.RED)
                except Exception:
                    pass
            except Exception as e:
                self.log(f"❌ Unexpected error in space tappers game: {e}", Fore.RED)
        
        # Panggil semua fungsi game: diamond_breath, tap, dan space_tappers
        diamond_breath()
        tap()
        space_tappers()

    def load_proxies(self, filename="proxy.txt"):
        """
        Reads proxies from a file and returns them as a list.
        
        Args:
            filename (str): The path to the proxy file.
        
        Returns:
            list: A list of proxy addresses.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                proxies = [line.strip() for line in file if line.strip()]
            if not proxies:
                raise ValueError("Proxy file is empty.")
            return proxies
        except Exception as e:
            self.log(f"❌ Failed to load proxies: {e}", Fore.RED)
            return []

    def set_proxy_session(self, proxies: list) -> requests.Session:
        """
        Creates a requests session with a working proxy from the given list.
        
        If a chosen proxy fails the connectivity test, it will try another proxy
        until a working one is found. If no proxies work or the list is empty, it
        will return a session with a direct connection.

        Args:
            proxies (list): A list of proxy addresses (e.g., "http://proxy_address:port").
        
        Returns:
            requests.Session: A session object configured with a working proxy,
                            or a direct connection if none are available.
        """
        # If no proxies are provided, use a direct connection.
        if not proxies:
            self.log("⚠️ No proxies available. Using direct connection.", Fore.YELLOW)
            self.proxy_session = requests.Session()
            return self.proxy_session

        # Copy the list so that we can modify it without affecting the original.
        available_proxies = proxies.copy()

        while available_proxies:
            proxy_url = random.choice(available_proxies)
            self.proxy_session = requests.Session()
            self.proxy_session.proxies = {"http": proxy_url, "https": proxy_url}

            try:
                test_url = "https://httpbin.org/ip"
                response = self.proxy_session.get(test_url, timeout=5)
                response.raise_for_status()
                origin_ip = response.json().get("origin", "Unknown IP")
                self.log(f"✅ Using Proxy: {proxy_url} | Your IP: {origin_ip}", Fore.GREEN)
                return self.proxy_session
            except requests.RequestException as e:
                self.log(f"❌ Proxy failed: {proxy_url} | Error: {e}", Fore.RED)
                # Remove the failed proxy and try again.
                available_proxies.remove(proxy_url)
        
        # If none of the proxies worked, use a direct connection.
        self.log("⚠️ All proxies failed. Using direct connection.", Fore.YELLOW)
        self.proxy_session = requests.Session()
        return self.proxy_session
    
    def override_requests(self):
        """Override requests and WebSocket functions globally when proxy is enabled."""

        if self.config.get("proxy", False):
            self.log("[CONFIG] 🛡️ Proxy: ✅ Enabled", Fore.YELLOW)
            proxies = self.load_proxies()
            self.set_proxy_session(proxies)

            # Override HTTP request methods
            requests.get = self.proxy_session.get
            requests.post = self.proxy_session.post
            requests.put = self.proxy_session.put
            requests.delete = self.proxy_session.delete

        else:
            self.log("[CONFIG] Proxy: ❌ Disabled", Fore.RED)
            # Restore original HTTP request methods if proxy is disabled
            requests.get = self._original_requests["get"]
            requests.post = self._original_requests["post"]
            requests.put = self._original_requests["put"]
            requests.delete = self._original_requests["delete"]

if __name__ == "__main__":
    fin = fintopia()
    index = 0
    max_index = len(fin.query_list)
    config = fin.load_config()
    if config.get("proxy", False):
        proxies = fin.load_proxies()

    fin.log("🎉 [LIVEXORDS] === Welcome to fintopia Automation === [LIVEXORDS]", Fore.YELLOW)
    fin.log(f"📂 Loaded {max_index} accounts from query list.", Fore.YELLOW)

    while True:
        current_account = fin.query_list[index]
        display_account = current_account[:10] + "..." if len(current_account) > 10 else current_account

        fin.log(f"👤 [ACCOUNT] Processing account {index + 1}/{max_index}: {display_account}", Fore.YELLOW)

        if config.get("proxy", False):
            fin.override_requests()
        else:
            fin.log("[CONFIG] Proxy: ❌ Disabled", Fore.RED)

        fin.login(index)

        fin.log("🛠️ Starting task execution...")
        tasks = {
            "daily": "🌞 Daily Check-In: Automatically claim your daily rewards and bonuses.",
            "task": "📝 Task Automation: Effortlessly complete tasks to earn bonus rewards.",
            "farm": "🌾 Farming: Auto claim and initiate farming operations to harvest extra resources.",
            "game": "🎮 Game Automation: Engage in automatic gameplay to maximize your in-game earnings."
        }

        for task_key, task_name in tasks.items():
            task_status = config.get(task_key, False)
            fin.log(f"[CONFIG] {task_name}: {'✅ Enabled' if task_status else '❌ Disabled'}", Fore.YELLOW if task_status else Fore.RED)

            if task_status:
                fin.log(f"🔄 Executing {task_name}...")
                getattr(fin, task_key)()

        if index == max_index - 1:
            fin.log("🔁 All accounts processed. Restarting loop.")
            fin.log(f"⏳ Sleeping for {config.get('delay_loop', 30)} seconds before restarting.")
            time.sleep(config.get("delay_loop", 30))
            index = 0
        else:
            fin.log(f"➡️ Switching to the next account in {config.get('delay_account_switch', 10)} seconds.")
            time.sleep(config.get("delay_account_switch", 10))
            index += 1