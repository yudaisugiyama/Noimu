# 各種設定を行うファイル

from queue import Queue

# Unityに渡す音楽のパス
MUSIC_PATH = "music.wav"

# 人間からのフィードバック時間を受け渡すキュー
feedback_queue = Queue()
prompt_queue = Queue()

# MQTTの設定
CLIENT_ID = "foge"
HOST = "localhost"
PORT = 1883
KEEP_ALIVE = 60
TOPIC1 = "foge"
TOPIC2 = "piyo"

# OpenCALMの設定
LOCATION = "長岡技術科学大学"