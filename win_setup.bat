@echo off
echo [1/3] Installiere Python Libraries...
pip install discord.py[voice] yt-dlp requests

echo [2/3] lade FFmpeg herunter...
powershell -Command "Invoke-WebRequest https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip -OutFile ffmpeg.zip"

echo [3/3] Entpacke FFmpeg...
powershell -Command "Expand-Archive -Force ffmpeg.zip ."
for /d %%i in (ffmpeg-*) do move "%%i\bin\ffmpeg.exe" .
for /d %%i in (ffmpeg-*) do rd /s /q "%%i"
del ffmpeg.zip

echo.
echo Setup abgeschlossen! ffmpeg.exe liegt nun in deinem Ordner.
pause