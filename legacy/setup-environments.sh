#!/bin/bash

## Setuo Python3 venv
cd "$(dirname "$(realpath "$0")")";
/opt/Python37/bin/python3 -m venv ./venv
source ./venv/bin/activate
pip3 install --upgrade -r requirements.txt

## Download essential program
### geckodriver
wget https://github.com/mozilla/geckodriver/releases/download/v0.25.0/geckodriver-v0.25.0-linux64.tar.gz
tar xvf geckodriver-v0.25.0-linux64.tar.gz
mv geckodriver ./venv/bin/
rm geckodriver-v0.25.0-linux64.tar.gz
### tor-browser
wget https://www.torproject.org/dist/torbrowser/8.5.5/tor-browser-linux64-8.5.5_en-US.tar.xz
tar xvf tor-browser-linux64-8.5.5_en-US.tar.xz
rm tor-browser-linux64-8.5.5_en-US.tar.xz

