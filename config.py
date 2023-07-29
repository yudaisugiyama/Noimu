# 各種設定を行うファイル

import os

from queue import Queue
from open_calm_thread import OpenCALM


# ファイルパスの設定
STATIC_ROOT = "static"
CSV_FILE_PATH = f"{STATIC_ROOT}/sleep_data.csv"
GRAPH_FILE_PATH = f"{STATIC_ROOT}/graph.png"
MUSIC_PATH = f"{STATIC_ROOT}/music.wav"
INTIIAL_MUSIC_PATH = f"{STATIC_ROOT}/initial.wav"

# キュー
feedback_queue = Queue()
opencalm_prompt_queue = Queue()
rl_completion_flag_queue = Queue()
event_control_queue = Queue()
opencalm_generation_flag_queue = Queue()

# MQTTの設定
CLIENT_ID = "noimu"
HOST = "192.168.100.10"
# HOST = "localhost"
PORT = 1883
KEEP_ALIVE = 60
FEEDBACK_TOPIC = "feedback"
INFO_TOPIC = "info"

# OpenCALMの設定
LOCATION = "金沢駅"
open_calm = OpenCALM(prompt_queue=opencalm_prompt_queue, opencalm_generation_flag_queue=opencalm_generation_flag_queue, location=LOCATION)

# AWSの設定
REGION = "ap-northeast-1"
