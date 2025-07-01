#!/bin/bash
export TZ=Europe/Paris

. dash-env/bin/activate
python ./APP.py &
python ./NINJA.py &

chromium http://127.0.0.1:8050
