# SpotiLike

Spotilike displays the current song you're listening to on Spotify on an OLED SH1106 screen, with a button to "like" the song.

## Features
- OLED SH1106 (I2C): Displays the song name and artist.
- Push Button: Likes the current song on Spotify when pressed.
- ESP32-WROOM-32D: Handles communication and controls.
- MicroPython: Runs the entire application.

## Wiring
- SDA Pin: 21
- SCL Pin 22
- Push Button Pin: 15

## Setup
1. Install MicroPython on the ESP32.
3. Set up Wi-Fi in config/wifi.json.
4. Create an App in Spotify Developer and config parameters in config/spotify.json (callback -> http://127.0.0.1:80/callback).
5. Upload the MicroPython code to the ESP32.
6. Power On
7. Do Authentication. First, go to http://`IP-ESP32`/login. Accept. Replace http://127.0.0.1:80 with http://`IP-ESP32`

## Credits
- **SH1106 Driver**: [Robert HH](https://github.com/robert-hh/SH1106/)
