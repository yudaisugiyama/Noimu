# mqtt通信用のスレッドを実装する
# 音楽ファイルは常に最新のものが"../wavs/music.wav"にあるので、それを渡せばいい

import time
import json
import threading
from queue import Queue
from paho.mqtt import client as mqtt

from config import MUSIC_PATH, CLIENT_ID, HOST, PORT, KEEP_ALIVE, TOPIC, feedback_queue, prompt_queue, open_calm

"""以下の1と2をスレッド実行するクラス

1. Unityから `sound_file_id_request` を受け取って、MUSIC_PATHの音楽をUnityに送信する
2. Unityから時間 `elapsed_time` を受け取って、 feedback_queueに入れる
"""