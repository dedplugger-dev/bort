# coding=utf-8
#!/usr/bin/env python3

import requests
import time
from multiprocessing import Process
from colorama import Fore, Style, init
from bs4 import BeautifulSoup
import threading

# Initialize colorama
init()

# ======== CONFIGURATION ========
BOT_TOKEN = "8307666131:AAHcCxoXwv6Z4JVu9IbGI1CtBDQWEvUlP0M"  # ← REPLACE WITH YOUR ACTUAL TOKEN
# ===============================

# Global proxy storage
user_proxies = {}

# Proxy websites
PROXY_WEBSITES = [
    "https://www.sslproxies.org/",
    "https://free-proxy-list.net/",
    "https://www.us-proxy.org/"
]

def print_success(message):
    print(Fore.GREEN + "[+] " + str(message) + Style.RESET_ALL)

def print_error(message):
    print(Fore.RED + "[-] " + str(message) + Style.RESET_ALL)

def print_status(message):
    print(Fore.BLUE + "[*] " + str(message) + Style.RESET_ALL)

def validate_proxy(proxy):
    """Test if a proxy is working"""
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    try:
        response = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=5)
        return response.status_code == 200
    except:
        return False

def validate_proxy_list(proxies):
    """Validate multiple proxies quickly"""
    valid_proxies = []
    
    def check_proxy(proxy):
        if validate_proxy(proxy):
            valid_proxies.append(proxy)
    
    threads = []
    
    for proxy in proxies:
        t = threading.Thread(target=check_proxy, args=(proxy,))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join(timeout=3)
    
    return valid_proxies

def collect_proxies_from_web(target_count):
    """Collect proxies from proxy websites"""
    all_proxies = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for website in PROXY_WEBSITES:
        try:
            response = requests.get(website, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'table table-striped table-bordered'})
            
            if table and table.tbody:
                for row in table.tbody.find_all('tr'):
                    columns = row.find_all('td')
                    if len(columns) >= 2:
                        ip = columns[0].text.strip()
                        port = columns[1].text.strip()
                        proxy = f"{ip}:{port}"
                        all_proxies.append(proxy)
                        
                        if len(all_proxies) >= target_count * 2:  # Collect extra for validation
                            break
                
            if len(all_proxies) >= target_count * 2:
                break
                
        except Exception as e:
            print_error(f"Error scraping {website}: {e}")
            continue
    
    return all_proxies[:target_count * 2]  # Return up to 2x target for validation

def report_profile_attack(username, proxy=None):
    """Report a profile"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = "https://example.com/report/profile"
    data = {'username': username, 'reason': 'spam'}
    
    try:
        if proxy:
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            response = requests.post(url, data=data, headers=headers, proxies=proxies, timeout=10)
        else:
            response = requests.post(url, data=data, headers=headers, timeout=10)
        return response.status_code == 200
    except:
        return False

def report_video_attack(video_url, proxy=None):
    """Report a video"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = "https://example.com/report/video"
    data = {'video_url': video_url, 'reason': 'spam'}
    
    try:
        if proxy:
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            response = requests.post(url, data=data, headers=headers, proxies=proxies, timeout=10)
        else:
            response = requests.post(url, data=data, headers=headers, timeout=10)
        return response.status_code == 200
    except:
        return False

def send_telegram_message(chat_id, message):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=data, timeout=5)
    except:
        pass

def get_bot_updates():
    """Get latest messages from bot"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return {"result": []}

def load_proxies_from_text(text):
    """Load and validate proxies from text"""
    proxies = []
    for line in text.split('\n'):
        line = line.strip()
        if line and ':' in line:
            proxies.append(line)
    return proxies

def collect_proxies_thread(chat_id, target_count):
    """Thread function to collect and validate proxies"""
    try:
        send_telegram_message(chat_id, f"🌐 Collecting {target_count} proxies from web... This may take 2-3 minutes.")
        
        # Step 1: Collect raw proxies
        raw_proxies = collect_proxies_from_web(target_count)
        send_telegram_message(chat_id, f"📥 Collected {len(raw_proxies)} raw proxies. Now validating...")
        
        # Step 2: Validate proxies
        valid_proxies = validate_proxy_list(raw_proxies)
        
        if valid_proxies:
            user_proxies[chat_id] = {
                "proxies": valid_proxies,
                "loaded_at": time.time()
            }
            send_telegram_message(chat_id, f"✅ <b>Proxy collection completed!</b>\n\nTarget: {target_count} proxies\nCollected: {len(raw_proxies)} raw\nValid: {len(valid_proxies)} working\n\nNow use:\n/profile username\n/video url\n/attack_all username")
        else:
            send_telegram_message(chat_id, "❌ No valid proxies found. Try again with a higher number.")
    
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Error collecting proxies: {str(e)}")

def process_command(message):
    """Process user command"""
    text = message.get('text', '').strip()
    chat_id = message['chat']['id']
    
    if text == '/start':
        help_text = """🤖 <b>RAZA REPORT BOT</b> ⚡

<b>PROXY SYSTEM:</b>
• /collect_proxy 50 - Auto-collect proxies from web
• /load_proxies - Manually load proxies (send list after)
• /proxy_status - Check loaded proxies

<b>ATTACK COMMANDS:</b>
/profile username - Attack with loaded proxies
/video url - Attack video with proxies
/attack_all username - Mass attack (2 rounds)

<b>QUICK ATTACKS (no proxies):</b>
/quick_profile username - Direct attack
/quick_video url - Direct video attack

<b>UTILITY:</b>
/help - Detailed help
/status - Bot status"""
        send_telegram_message(chat_id, help_text)
    
    elif text == '/help':
        help_text = """📖 <b>HELP MENU</b>

<b>AUTO PROXY COLLECTION:</b>
/collect_proxy 50 - Gets 50 working proxies from web
/collect_proxy 100 - Gets 100 working proxies

<b>MANUAL PROXY LOADING:</b>
1. /load_proxies
2. Send proxy list (ip:port, one per line)

<b>ATTACKS WITH PROXIES:</b>
• /profile username - Use all loaded proxies
• /video url - Attack video
• /attack_all username - Mass attack (2 rounds)

<b>Proxy Sources:</b>
• sslproxies.org
• free-proxy-list.net  
• us-proxy.org"""
        send_telegram_message(chat_id, help_text)
    
    elif text.startswith('/collect_proxy '):
        try:
            parts = text.split()
            if len(parts) < 2:
                send_telegram_message(chat_id, "❌ Format: /collect_proxy <number>\nExample: /collect_proxy 50")
                return
            
            target_count = int(parts[1])
            if target_count > 200:
                send_telegram_message(chat_id, "⚠️ Maximum 200 proxies. Setting to 200.")
                target_count = 200
            elif target_count < 10:
                send_telegram_message(chat_id, "⚠️ Minimum 10 proxies. Setting to 10.")
                target_count = 10
            
            # Start proxy collection in background thread
            thread = threading.Thread(target=collect_proxies_thread, args=(chat_id, target_count))
            thread.start()
            
        except ValueError:
            send_telegram_message(chat_id, "❌ Please provide a valid number\nExample: /collect_proxy 50")
    
    elif text == '/load_proxies':
        send_telegram_message(chat_id, "📥 <b>Send your proxy list</b>\n\nFormat: ip:port (one per line)\nExample:\n192.168.1.1:8080\n10.0.0.1:3128\n\nI will validate and store them.")
        user_proxies[chat_id] = {"step": "waiting_for_proxies"}
    
    elif text == '/proxy_status':
        if chat_id in user_proxies and "proxies" in user_proxies[chat_id]:
            proxies = user_proxies[chat_id]["proxies"]
            status_msg = f"✅ <b>Loaded Proxies:</b> {len(proxies)}\n\nFirst 5 proxies:\n" + "\n".join(proxies[:5])
            if len(proxies) > 5:
                status_msg += f"\n... and {len(proxies) - 5} more"
            send_telegram_message(chat_id, status_msg)
        else:
            send_telegram_message(chat_id, "❌ No proxies loaded. Use /collect_proxy 50 or /load_proxies")
    
    elif text == '/clear_proxies':
        if chat_id in user_proxies:
            user_proxies.pop(chat_id)
        send_telegram_message(chat_id, "✅ Proxies cleared!")
    
    elif text == '/status':
        if chat_id in user_proxies and "proxies" in user_proxies[chat_id]:
            proxy_count = len(user_proxies[chat_id]["proxies"])
            send_telegram_message(chat_id, f"✅ <b>Bot Status:</b> ONLINE\n📊 Loaded Proxies: {proxy_count}\n⚡ Ready to attack!")
        else:
            send_telegram_message(chat_id, "✅ <b>Bot Status:</b> ONLINE\n📊 Loaded Proxies: 0\nUse /collect_proxy 50 to get proxies")
    
    elif chat_id in user_proxies and user_proxies[chat_id].get("step") == "waiting_for_proxies":
        # User is sending proxies after /load_proxies command
        send_telegram_message(chat_id, "⏳ Validating proxies... This may take a minute.")
        
        proxies = load_proxies_from_text(text)
        valid_proxies = validate_proxy_list(proxies)
        
        if valid_proxies:
            user_proxies[chat_id] = {
                "proxies": valid_proxies,
                "loaded_at": time.time()
            }
            send_telegram_message(chat_id, f"✅ <b>Proxies loaded successfully!</b>\n\nValid: {len(valid_proxies)}/{len(proxies)}\n\nNow you can use:\n/profile username\n/video url\n/attack_all username")
        else:
            send_telegram_message(chat_id, "❌ No valid proxies found. Please check your proxy list and try again.")
    
    elif text.startswith('/profile '):
        if chat_id not in user_proxies or "proxies" not in user_proxies[chat_id]:
            send_telegram_message(chat_id, "❌ No proxies loaded! Use /collect_proxy 50 first.")
            return
        
        username = text.replace('/profile ', '').strip()
        if not username:
            send_telegram_message(chat_id, "❌ Please provide a username")
            return
        
        proxies = user_proxies[chat_id]["proxies"]
        send_telegram_message(chat_id, f"⚡ Attacking {username} with {len(proxies)} proxies...")
        
        # Attack with all loaded proxies
        success = 0
        for i, proxy in enumerate(proxies):
            if report_profile_attack(username, proxy):
                success += 1
            # Progress update every 10 proxies
            if (i + 1) % 10 == 0:
                send_telegram_message(chat_id, f"📊 Progress: {i+1}/{len(proxies)} | Success: {success}")
        
        send_telegram_message(chat_id, f"✅ Proxy attack completed!\nTarget: {username}\nProxies used: {len(proxies)}\nSuccessful reports: {success}")
    
    elif text.startswith('/video '):
        if chat_id not in user_proxies or "proxies" not in user_proxies[chat_id]:
            send_telegram_message(chat_id, "❌ No proxies loaded! Use /collect_proxy 50 first.")
            return
        
        video_url = text.replace('/video ', '').strip()
        if not video_url.startswith('http'):
            send_telegram_message(chat_id, "❌ Please provide a valid URL")
            return
        
        proxies = user_proxies[chat_id]["proxies"]
        send_telegram_message(chat_id, f"⚡ Attacking video with {len(proxies)} proxies...")
        
        # Attack with all loaded proxies
        success = 0
        for i, proxy in enumerate(proxies):
            if report_video_attack(video_url, proxy):
                success += 1
            # Progress update every 10 proxies
            if (i + 1) % 10 == 0:
                send_telegram_message(chat_id, f"📊 Progress: {i+1}/{len(proxies)} | Success: {success}")
        
        send_telegram_message(chat_id, f"✅ Video proxy attack completed!\nTarget: {video_url}\nProxies used: {len(proxies)}\nSuccessful reports: {success}")
    
    elif text.startswith('/attack_all '):
        if chat_id not in user_proxies or "proxies" not in user_proxies[chat_id]:
            send_telegram_message(chat_id, "❌ No proxies loaded! Use /collect_proxy 50 first.")
            return
        
        username = text.replace('/attack_all ', '').strip()
        if not username:
            send_telegram_message(chat_id, "❌ Please provide a username")
            return
        
        proxies = user_proxies[chat_id]["proxies"]
        send_telegram_message(chat_id, f"💥 MASS ATTACK starting on {username} with {len(proxies)} proxies...")
        
        # Mass attack - use each proxy multiple times
        success = 0
        total_attempts = len(proxies) * 2  # Each proxy used twice
        
        for round_num in range(2):  # 2 rounds with all proxies
            send_telegram_message(chat_id, f"🔁 Round {round_num + 1}/2 starting...")
            
            for i, proxy in enumerate(proxies):
                if report_profile_attack(username, proxy):
                    success += 1
                
                # Progress update
                current_attempt = (round_num * len(proxies)) + i + 1
                if current_attempt % 20 == 0:
                    send_telegram_message(chat_id, f"📊 Progress: {current_attempt}/{total_attempts} | Success: {success}")
        
        send_telegram_message(chat_id, f"💥 MASS ATTACK COMPLETED!\nTarget: {username}\nTotal attempts: {total_attempts}\nSuccessful reports: {success}")
    
    elif text.startswith('/quick_profile '):
        username = text.replace('/quick_profile ', '').strip()
        if not username:
            send_telegram_message(chat_id, "❌ Please provide a username")
            return
        
        send_telegram_message(chat_id, f"⚡ Quick attack on: {username} (no proxies)")
        
        # Quick attack without proxies
        success = 0
        for i in range(20):  # 20 direct attempts
            if report_profile_attack(username):
                success += 1
            if (i + 1) % 5 == 0:
                send_telegram_message(chat_id, f"📊 Progress: {i+1}/20 | Success: {success}")
        
        send_telegram_message(chat_id, f"✅ Quick attack completed!\nTarget: {username}\nSuccess: {success}/20")
    
    elif text.startswith('/quick_video '):
        video_url = text.replace('/quick_video ', '').strip()
        if not video_url.startswith('http'):
            send_telegram_message(chat_id, "❌ Please provide a valid URL")
            return
        
        send_telegram_message(chat_id, f"⚡ Quick video attack (no proxies)")
        
        # Quick attack without proxies
        success = 0
        for i in range(20):  # 20 direct attempts
            if report_video_attack(video_url):
                success += 1
            if (i + 1) % 5 == 0:
                send_telegram_message(chat_id, f"📊 Progress: {i+1}/20 | Success: {success}")
        
        send_telegram_message(chat_id, f"✅ Quick video attack completed!\nTarget: {video_url}\nSuccess: {success}/20")
    
    else:
        send_telegram_message(chat_id, "❌ Unknown command. Use /help for available commands")

def main():
    """Simple polling bot"""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print_error("Please set your BOT_TOKEN in the script!")
        return
    
    print_success("🤖 RAZA REPORT BOT Started!")
    print_status("Bot is running... Send commands to your bot on Telegram")
    print_status("Use /collect_proxy 50 to auto-collect proxies")
    print_status("Press Ctrl+C to stop\n")
    
    last_update_id = 0
    
    while True:
        try:
            updates = get_bot_updates()
            
            if updates.get('result'):
                for update in updates['result']:
                    if update['update_id'] > last_update_id:
                        last_update_id = update['update_id']
                        if 'message' in update and 'text' in update['message']:
                            process_command(update['message'])
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            print_success("\nBot stopped by user")
            break
        except Exception as e:
            print_error(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()