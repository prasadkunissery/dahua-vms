@echo off
title Dahua Live Stream Viewer

echo Installing and verifying dependencies...
py -m pip install opencv-python Pillow --quiet

echo.
echo Launching Dahua Camera Viewer...
py main.py
