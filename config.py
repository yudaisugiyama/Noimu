# 各種設定を行うファイル

from queue import Queue
from open_calm_thread import OpenCALM

# Unityに渡す音楽のパス
MUSIC_PATH = "Test.wav"

# 人間からのフィードバック時間を受け渡すキュー
feedback_queue = Queue()
prompt_queue = Queue()

# MQTTの設定
CLIENT_ID = "foge"
# HOST = "localhost"
HOST = "192.168.10.101"
PORT = 1883
KEEP_ALIVE = 60
FEEDBACK_TOPIC = "feedback"
INFO_TOPIC = "info"

# OpenCALMの設定
LOCATION = "長岡技術科学大学"
open_calm = OpenCALM(prompt_queue=prompt_queue, location=LOCATION)

# AWSの設定
REGION = "ap-northeast-1"