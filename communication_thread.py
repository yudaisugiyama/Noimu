# mqtt通信用のスレッドを実装する
# 音楽ファイルは常に最新のものが"../wavs/music.wav"にあるので、それを渡せばいい

import os
import time
import json
import threading
from queue import Queue
from paho.mqtt import client as mqtt

from config import MUSIC_PATH, CLIENT_ID, HOST, PORT, KEEP_ALIVE, FEEDBACK_TOPIC, INFO_TOPIC, feedback_queue, prompt_queue, event_control_queue, open_calm

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
        print('+ Received message.')

        # メッセージをデコード
        query = msg.payload.decode()
        query_info = json.loads(query)

        # リクエストに応じて処理
        request = query_info['request']

        if request == 'compute_main_function':
            # キューにフィードバックを入れる
            feedback_queue.put(query_info['feedback'])
            print(query_info['feedback'])

            # ノイミューの言葉を取得してUnityに送信
            noimu_words = prompt_queue.get()
            data = {
                "request": "noimu_words",
                "value": noimu_words,
            }
            msg = json.dumps(dict(data), indent=0)
            client.publish(INFO_TOPIC, msg)

            print(noimu_words)

            # 睡眠時間のグラフを作成
            print('+ Create sleep graph.')
            try:
                print(query_info['sleep_time'])
                fig = plot()
                event_control_queue.put(fig)

            except:
                key_name, file_name = "test", "test"
                msg = [key_name, file_name]
                event_control_queue.put(msg)

        elif request == 'sound_file':
            print('+ Send sound file info.')
            data = {
                "request": "sound_file",
                "value": MUSIC_PATH,
            }
            msg = json.dumps(dict(data), indent=0)
            client.publish(INFO_TOPIC, msg)
            print("+ Publish sound file info.")