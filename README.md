# HomeStage

Let's say you have a little home automation going on, like enjoying music and happen to own some stage lights, and you want to make it a 🔥 music room.

WELCOME TO HOMESTAGE.

This project is a work-in-progress and you're on your own right now.

## This fork

I forked the already very good working repository [sk89q/HomeStage](https://github.com/sk89q/HomeStage) and modified it for my use case. I removed everything I didn't need to make the code easier for me to understand.

I have LED strips in my home which are flashed with [espurna](https://github.com/xoseperez/espurna), which means they can be controlled via MQTT. I did not use a microphone but rather the loopback of the raspberry the audio is playing on. I currently have removed the code for the API, but it looks good so I'll probably readd that later.

I'm also directly relying on the beat detection by `aubio` because using the tempo too had some weird doubled effects for me. I've added an option to enable and disable the system via MQTT, so I can add a "party button" to my house.

*Videos of this in action might follow later.*

## Setup

You need Python 3.6+ on the raspberry, which is only shipped with Raspbian Buster (and higher). Make sure to update the raspberry.

1. Install dependencies using pip: `pip3 install -r requirements.txt`
2. Run `./homestage-server.py`
3. Modify `config.py` according to your needs, especially the MQTT server address and the MQTT brightness and RGB topics for the lights. *If you are using espurna and a 4CH-LED (RGBW), enable Use White Channel in the light settings for better results*

### Setup pulseaudio on the raspberry

For the used library `soundcard` to work, you have to setup pulseaudio, which is not used by default on the raspberry. Here's how:

1. `sudo apt-get install pulseaudio pulseaudio-module-zeroconf alsa-utils avahi-daemon`
2. `sudo modprobe snd-bcm2835`
3. `sudo reboot`

I'm also using [snapcast](https://github.com/xoseperez/espurna), for which I had to put pulseaudio in system mode. That's the tutorial I used for that: https://rudd-o.com/linux-and-free-software/how-to-make-pulseaudio-run-once-at-boot-for-all-your-users  
I had to modify `Exec` with `ExecStart` in the systemd-file from that tutorial. Also do `sudo useradd -a -g pulse-access user` (replace user by either `pi`, `snapclient` or `_snapclient`, I'm unsure) which allows the user to access the system pulseaudio instance.

sudo apt-get install libatlas-base-dev ffmpeg
