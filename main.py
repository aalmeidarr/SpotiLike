from machine import Pin, SoftI2C
from webserver import WebServer
import gc
import json
import network
import os
import time
import sh1106
import ubinascii
import urequests as requests
import random

SDA_PIN = 21
SCL_PIN = 22
LED_PIN = 2
PUSH_PIN = 15

def init():
    with open("config/wifi.json", "r") as f:
        wifi_config = json.load(f)
        wlan = network.WLAN(network.WLAN.IF_STA)
        wlan.active(True)
        if not wlan.isconnected():
            wlan.connect(wifi_config['ssid'], wifi_config['key'])
        while wlan.isconnected() == False:
            pass
        print(f"Connected to {wifi_config['ssid']} with IP {wlan.ipconfig('addr4')[0]}")

def init_display():
    i2c = SoftI2C(sda=Pin(SDA_PIN), scl=Pin(SCL_PIN))
    display = sh1106.SH1106_I2C(128, 64, i2c)
    for i in range(5):
        display.invert(i%2)
        display.text("SpotiLike", 24, 30)
        display.ellipse(64, 32 , 64, 15, 1)
        display.show()
        time.sleep(0.2)
    return display

def auth() -> str :
    with open("config/spotify.json", "r") as f:
        spotify_config = json.load(f)
    authorization =  ubinascii.b2a_base64(f"{spotify_config['client_id']}:{spotify_config['client_secret']}".encode()).strip()
    headers = {
        "Content-type":"application/x-www-form-urlencoded",
        "Authorization":f"Basic {authorization.decode()}"
    }

    if not ".refresh_token" in os.listdir():
        ws = WebServer()
        code = ws.listen()
        data = f"grant_type=authorization_code&code={code}&redirect_uri=http://127.0.0.1:80/callback"
        res = requests.post(url="https://accounts.spotify.com/api/token", data=data, headers=headers)
        with open('.refresh_token', 'w') as f:
            f.write(res.json()['refresh_token'])
    else:
        with open('.refresh_token', 'r') as f:
            refresh_token = f.readline().strip()
        data = f"grant_type=refresh_token&refresh_token={refresh_token}"
        res = requests.post(url="https://accounts.spotify.com/api/token", data=data, headers=headers)
    return res.json()['access_token']

def get_user_name(auth_token) -> str:
    headers = {"Authorization":f"Bearer {auth_token}"}
    res = requests.get(url="https://api.spotify.com/v1/me", headers=headers)
    return res.json()["display_name"]
        
def get_playback_state(auth_token) -> dict:
    headers = {"Authorization":f"Bearer {auth_token}"}
    res = requests.get(url="https://api.spotify.com/v1/me/player", headers=headers)
    if res.text:
        album = res.json()["item"]["album"]["name"]
        main_artist = res.json()["item"]["artists"][0]["name"]
        song = res.json()["item"]["name"]
        href = res.json()["item"]["href"]
        return {"album":album, "main_artist":main_artist, "song":song, "href":href}
    else:
        return {}

def save_song(song_url, auth_token):
    led = Pin(LED_PIN, Pin.OUT)
    led.value(1)
    headers = {"Authorization":f"Bearer {auth_token}", "Content-Type": "application/json"}
    ids = song_url.split('/')[-1].strip()
    json_data = json.dumps({"ids":[ids]})
    requests.put(url=f"https://api.spotify.com/v1/me/tracks?ids={ids}", headers=headers, json=json_data)
    led.value(0)
    

def main():
    display = init_display()
    init()
    display.fill(0)
    display.text("Authenticating", 5, 30)
    display.show()
    auth_code = auth()
    username = get_user_name(auth_code)
    display.fill(0)
    display.text("Welcome!", 0, 20)
    display.text(username, 0, 30)
    display.show()
    pin = Pin(PUSH_PIN, Pin.OUT)
    pin.value(1)
    push = Pin(23, Pin.IN, Pin.PULL_DOWN)
    while True:
        gc.collect()
        display.fill(0)
        current = get_playback_state(auth_code)
        try:
            display.text(current["song"], 0,10)
            display.text(current["album"], 0,20)
            display.text(current["main_artist"], 0,30)
        except:
            display.fill(0)
        display.show()
        for i in range(12):
            if push.value() and current:
                display.fill(0)
                display.invert(1)
                display.text("Banger!!!", 20, 30)
                display.show()
                save_song(current["href"], auth_code)
                display.invert(0)
                break
            display.fill_rect(10*i, 50, 6, 6, 1)
            display.show()
            time.sleep(0.5)

main()
    


