"""Unityの挙動をPythonで再現する
"""

import time
import json
import paho.mqtt.client as mqtt


def main():
    host = "192.168.10.101"
    # host = "localhost"
    topic = "feedback"

    client = mqtt.Client("unity")
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(host, 1883, 60)
    client.loop_start()


    ## フィードバックの送信
    msg1 = {
        "request": "compute_main_function",
        "feedback": {
            "elapsed_time": 999,
            "sleep_time": 999,
        },
    }

    ## 音ファイルのリクエスト
    msg2 = {
        "request": "sound_file",
    }


    data = [msg1, msg2]

    for i in range(2):
        msg = json.dumps(dict(data[i]), indent=0)
        info = client.publish(topic, msg, qos=1)
        if info[0] != 0:
            print("PUBLISH FAILED")
        time.sleep(6)


def on_connect(client, userdata, flags, rc):
    print('+ Connected broker.') if rc==0 else print('BROKER CONNECTION ERROR')

def on_publish(client, userdata, mid):
    print("+ Publish: {0}".format(mid))


if __name__ == '__main__':
  main()
