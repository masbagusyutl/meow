import requests
import json
import time
import subprocess
from urllib.parse import parse_qs

# URL dan headers
url = "https://api.service.gameeapp.com/"
headers = {
    'accept': 'application/json; indent=2',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://lfg.supermeow.vip',
    'priority': 'u=1, i',
    'referer': 'https://lfg.supermeow.vip/',
    'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24", "Microsoft Edge WebView2";v="125"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
}

def read_initdata_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

def get_nama_from_init_data(auth_data):
    parsed_data = parse_qs(auth_data)
    auth_data_json_str = parsed_data.get('auth_data', [None])[0]

    if auth_data_json_str:
        try:
            auth_data_json = json.loads(auth_data_json_str)
            user_info_str = auth_data_json.get('user')
            if user_info_str:
                user_info = json.loads(user_info_str)
                first_name = user_info.get('first_name', '')
                last_name = user_info.get('last_name', '')
                username = user_info.get('username', '')
                data = f"{first_name} {last_name} ({username})".strip()
                return data
            else:
                return "user info not found in auth_data"
        except json.JSONDecodeError as e:
            return f"Invalid JSON format in auth_data: {e}"
    else:
        return "auth_data not found in the query parameters"

def start_session(auth_data):
    parsed_data = parse_qs(auth_data)
    auth_data_json_str = parsed_data.get('auth_data', [None])[0]
    try:
        auth_data_json = json.loads(auth_data_json_str)
        user_info_str = auth_data_json.get('user')
        user_info = json.loads(user_info_str)

        json_data = {
            'user': {
                'id': int(user_info.get('id', '')),
                'first_name': user_info.get('first_name', ''),
                'last_name': user_info.get('last_name', ''),
                'username': user_info.get('username', ''),
                'language_code': user_info.get('language_code', ''),
                'allows_write_to_pm': user_info.get('allows_write_to_pm', ''),
            }
        }

        response = requests.post(
            f'https://api.supermeow.vip/meow/info?{auth_data}',
            headers=headers,
            json=json_data,
        )
        return response
    except json.JSONDecodeError:
        return "Invalid JSON format in init_data"
    except KeyError:
        return "Missing required fields in user info"

def claim_harian(init_data):
    try:
        response = requests.post(
            f'https://api.supermeow.vip/meow/claim?{init_data}&is_on_chain=false',
            headers=headers,
        )
        return response
    except Exception as e:
        return f"An error occurred: {e}"

def process_initdata(init_data):
    try:
        nama = get_nama_from_init_data(init_data)
        print(f"Nama: {nama}")

        start_response = start_session(init_data)
        if start_response.status_code == 200:
            try:
                start_data = start_response.json()['balance']
                print(f"Balance: {start_data}")
            except KeyError:
                print("Key 'balance' not found in response")
        else:
            print('Belum Waktunya Claim')

        daily_response = claim_harian(init_data)
        if daily_response.status_code == 200:
            try:
                daily_data = daily_response.json()['last_claim']
                print(daily_data)
                print("Sukses Claim")
            except KeyError:
                print("Belum Waktunya Claim")
        else:
            print('Sudah Ambil Daily')

        print("\n")
    except Exception as e:
        print(f"An error occurred: {e}")

def countdown_timer(seconds):
    while seconds:
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        timer = f'{hours:02d}:{mins:02d}:{secs:02d}'
        print(f"Waiting for the next run: {timer}", end="\r")
        time.sleep(1)
        seconds -= 1
    print("\n")

def main():
    initdata_file = "initdata.txt"
    
    while True:
        initdata_list = read_initdata_from_file(initdata_file)
        
        for init_data in initdata_list:
            process_initdata(init_data.strip())
        
        countdown_timer(4 * 3600)  # 4 hours in seconds

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        subprocess.run(["python3.10", "gamee.py"])
