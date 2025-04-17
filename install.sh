#!/bin/bash
echo "開始安裝 SNR 自動交易機器人..."
sudo apt update
sudo apt install -y python3 python3-pip git
git clone https://github.com/Dash1943/snr-autobot.git
cd snr-autobot
pip3 install -r requirements.txt || true
echo "啟動主程式..."
python3 main.py
