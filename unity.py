"""Unity通信のスタブ
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
    data = {
        "request": "compute_main_function",
        "feedback": {
            "elapsed_time": 999,
            "sleep_time": 999,
        },
    }

    while True:
        msg = json.dumps(dict(data), indent=0)
        info = client.publish(topic, msg, qos=1)
        if info[0] != 0:
            print("PUBLISH FAILED")
        time.sleep(10)


def on_connect(client, userdata, flags, rc):
    print('+ Connected broker.') if rc==0 else print('BROKER CONNECTION ERROR')

def on_publish(client, userdata, mid):
    print("+ Publish: {0}".format(mid))


if __name__ == '__main__':
  main()
