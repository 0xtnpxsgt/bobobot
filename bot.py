import cloudscraper
import json
import random
import time
import threading
import shareithub
from shareithub import shareithub


shareithub()
# Membaca API Key dan URL API dari file account.txt (multi API support)
api_accounts = []
with open('account.txt', 'r') as file:
    for line in file:
        parts = line.strip().split('|')  # Format: API_KEY|API_URL
        if len(parts) == 2:
            api_accounts.append((parts[0], parts[1]))

if not api_accounts:
    print("Error: Tidak ada API Key dan URL yang valid di account.txt!")
    exit()

# Membaca pesan-pesan pengguna dari file message.txt
with open('message.txt', 'r') as file:
    user_messages = [msg.strip() for msg in file.readlines() if msg.strip()]

if not user_messages:
    print("Error: Tidak ada pesan dalam message.txt!")
    exit()

# Inisialisasi Cloudscraper
scraper = cloudscraper.create_scraper()

# Fungsi untuk mengirim permintaan ke API
def send_request(message):
    while True:
        # Pilih API key dan URL secara acak
        api_key, api_url = random.choice(api_accounts)

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        data = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ]
        }

        try:
            response = scraper.post(api_url, headers=headers, json=data)

            # Cek status code dan pastikan respons tidak kosong
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    print(f"✅ [SUCCESS] API: {api_url} | Message: '{message}'")
                    print(response_json)
                    break  # Keluar dari loop jika berhasil
                except json.JSONDecodeError:
                    print(f"⚠️ [ERROR] Invalid JSON response! API: {api_url}")
                    print(f"Response Text: {response.text}")
            else:
                print(f"⚠️ [ERROR] API: {api_url} | Status: {response.status_code} | Retrying in 2s...")
                time.sleep(2)

        except Exception as e:
            print(f"❌ [REQUEST FAILED] API: {api_url} | Error: {e} | Retrying in 5s...")
            time.sleep(2)

# Fungsi untuk menjalankan thread
def start_thread():
    while True:
        random_message = random.choice(user_messages)
        send_request(random_message)

# Menentukan jumlah thread yang akan digunakan
try:
    num_threads = int(input("Enter the number of threads you want to use: "))
    if num_threads < 1:
        print("Please enter a number greater than 0.")
        exit()
except ValueError:
    print("Invalid input. Please enter an integer.")
    exit()

# Memulai multi-threading untuk pengiriman pesan acak
threads = []
for _ in range(num_threads):
    thread = threading.Thread(target=start_thread, daemon=True)  # Menggunakan daemon agar bisa dihentikan dengan CTRL+C
    threads.append(thread)
    thread.start()

# Menunggu hingga semua thread selesai (script akan terus berjalan)
for thread in threads:
    thread.join()

print("All requests have been processed.")  # (Ini tidak akan pernah tercapai karena looping terus menerus)
