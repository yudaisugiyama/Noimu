# mqtt通信用のスレッドを実装する
# 音楽ファイルは常に最新のものが"../wavs/music.wav"にあるので、それを渡せばいい

import os
import time
import json
import threading
from queue import Queue
from paho.mqtt import client as mqtt

from config import MUSIC_PATH, CLIENT_ID, HOST, PORT, KEEP_ALIVE, FEEDBACK_TOPIC, INFO_TOPIC, feedback_queue, opencalm_prompt_queue, event_control_queue, rl_completion_flag_queue, opencalm_generation_flag_queue

from utils import get_s3, plot

BUCKET_NAME = os.getenv("BUCKET_NAME")

"""以下の1と2をスレッド実行するクラス

1. Unityから `sound_file_id_request` を受け取って、MUSIC_PATHの音楽をUnityに送信する
2. Unityから時間 `elapsed_time` を受け取って、 feedback_queueに入れる
"""


class Communicator(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.client = mqtt.Client(CLIENT_ID)

    def run(self):
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.connect(HOST, PORT, KEEP_ALIVE)
        self.client.subscribe(FEEDBACK_TOPIC, qos=1)
        self.client.loop_forever()

def on_connect(client, userdata, flags, rc):
    print('+ Connected broker.') if rc==0 else print('BROKER CONNECTION ERROR')

def on_message(client, userdata, msg):
    if msg.topic == FEEDBACK_TOPIC:
        print('+ [1] Received message.')

        # メッセージをデコード
        query = msg.payload.decode()
        query_info = json.loads(query)

        # リクエストに応じて処理
        request = query_info['request']

        if request == 'compute_main_function':
            # キューにフィードバックを入れる
            feedback_queue.put(query_info['feedback']['elapsed_time'])
            # openCalmに文章生成を依頼する
            opencalm_generation_flag_queue.put(True)

            # 強化学習 + 音生成の完了待ち
            completion_flag = rl_completion_flag_queue.get()
            print("+ rl done.")

            print(query_info['feedback'])

            # ノイミューの言葉を取得してUnityに送信
            noimu_words = opencalm_prompt_queue.get()
            data = {
                "request": "noimu_words",
                "value": noimu_words,
            }
            msg = json.dumps(dict(data), indent=0)
            client.publish(INFO_TOPIC, msg)

            print(noimu_words)

            # グラフ作成イベント
            event_control_queue.put(query_info['feedback']['sleep_time'])

        elif request == 'sound_file':
            print('+ [1] Received message.')
            data = {
                "request": "sound_file",
                "value": "music.wav",
            }
            msg = json.dumps(dict(data), indent=0)
            client.publish(INFO_TOPIC, msg)
            print("+ [2] Publish sound file info.")