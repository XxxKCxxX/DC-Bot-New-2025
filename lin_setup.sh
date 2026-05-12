#!/bin/bash

echo "[1/3] Update System-Pakete..."
sudo apt update && sudo apt upgrade -y

echo "[2/3] Installiere FFmpeg und Audio-Codecs..."
sudo apt install ffmpeg libopus-dev python3-pip -y

echo "[3/3] Installiere Python Libraries..."
pip3 install discord.py[voice] yt-dlp requests

echo ""
echo "Setup abgeschlossen! Du kannst den Bot nun mit 'python3 main.py' starten."