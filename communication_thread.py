# mqtt通信用のスレッドを実装する
# 音楽ファイルは常に最新のものが"../wavs/music.wav"にあるので、それを渡せばいい

import time
import json
import threading
from queue import Queue
from paho.mqtt import client as mqtt

from config import MUSIC_PATH, CLIENT_ID, HOST, PORT, KEEP_ALIVE, FEEDBACK_TOPIC, INFO_TOPIC, feedback_queue, prompt_queue, open_calm

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

        if request == 'start_learning':
            print('+ Start learning process.')

            # キューにフィードバックを入れる
            feedback_queue.put(query_info['feedback'])
            print(query_info['feedback'])

        elif request == 'sound_file':
            print('+ Send sound file info.')
            client.publish(INFO_TOPIC, MUSIC_PATH)
            print("+ Publish")

        elif request == 'open_calm':
            print('+ Send prompt to open calm.')
            open_calm.start()
            time.sleep(5)
            noimu_words = prompt_queue.get()
            print(noimu_words)
            client.publish(INFO_TOPIC, noimu_words)