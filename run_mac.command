#!/bin/bash
cd "$(dirname "$0")/companion"
pip3 install -r requirements.txt -q
python3 main.py
