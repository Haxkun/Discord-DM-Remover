import os
import requests
import json
import random
from pprint import pprint
from time import sleep

with open("configurations.json", "r")as f: config = json.load(f)

token = config["Token"]
fast_delete = config["Fast_Delete"]

offset = 0

def login(headers):
    try:
        response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
        if "id" in response.json():
            return {
                "worked": response.status_code == 200,
                "user_id": response.json()["id"],
                "cookies": dict(response.cookies)
            }
        else:
            return {
                "worked": False
            }
    except Exception as E:
        print(f"Exception Occurred. [{E.__class__.__name__}]")
        os._exit(0)

def choice_dm(cookies, headers):
    try:
        response = requests.get("https://discord.com/api/v9/users/@me/channels", cookies=cookies, headers=headers)
        index_count = 0
        for _ in response.json():
            try:
                if "recipients" in _:
                    if "owner_id" in _:
                        users = []
                        for __ in _["recipients"]:
                            users.append(__["username"])
                        print(f"[{index_count}] {_['name']} (users: {users[:2]})")
                    else:
                        print(f"[{index_count}] {_['recipients'][0]['username']}")
                else:
                    pass
                index_count += 1
            except Exception as E:
                print(f"[!] {E.__class__.__name__}")
        while True:
            try:
                choice = int(input(">>"))
                return response.json()[choice]["id"]
            except Exception as E:
                print(f"Exception Occurred. [{E.__class__.__name__}]")
    except Exception as E:
        print(f"Exception Occurred. [{E.__class__.__name__}]")
        os._exit(0)

def get_message(cookies, headers, channel_id, user_id):
    global offset
    status = False
    while status != True:
        try:
            response = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/messages/search?author_id={user_id}&offset={offset}", cookies=cookies, headers=headers)
            if "messages" in response.json():
                if len(response.json()["messages"]) == 0:
                    status = True
                else:
                    for _ in response.json()["messages"]:
                        for __ in _:
                            if "id" in __:
                                delete_dm(cookies, headers, channel_id, __["id"])
                                if fast_delete:
                                    pass
                                else:
                                    sleep(random.randint(1, 5))
                            else:
                                continue
            elif "retry_after" in response.json():
                print(f"[!] Rate Limited...! ({response.json()['retry_after']}sec)")
                sleep(response.json()["retry_after"])
            else:
                break
        except Exception as E:
            print(f"[!] Exception Occurred. [{E.__class__.__name__}]")

def delete_dm(cookies, headers, channel_id, message_id):
    global offset
    while True:
        try:
            response = requests.delete(f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}", cookies=cookies, headers=headers)
            if response.status_code == 204:
                print(f"[+] Message Has Been Deleted! ({message_id})")
                break
            elif response.status_code == 429:
                print(f"[!] Rate Limited... ({response.json()['retry_after']}sec)")
                sleep(int(response.json()["retry_after"]))
            else:
                print(f"[!] {response.json()['message']}")
                offset += 1
                break
        except Exception as E:
            print(f"[!] Exception Occurred. [{E.__class__.__name__}]")
            break

def main():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.45 Chrome/91.0.4472.164 Electron/13.6.6 Safari/537.36",
        "authorization": token,
    }
    login_result = login(headers)
    if login_result["worked"]:
        result_choice_dm = choice_dm(login_result["cookies"], headers)
        get_message(login_result["cookies"], headers, result_choice_dm, login_result["user_id"])
    else:
        print(f"[!] Account Login Failed...")

if __name__ == "__main__":
    main()
