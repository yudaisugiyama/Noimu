"""杉山用テスト用スクリプト

"""

import os

from typing import *
import time

from communication_thread import Communicator
from config import feedback_queue, open_calm, event_control_queue

from dotenv import load_dotenv
from utils import get_s3, plot
from config import CSV_FILE_PATH, GRAPH_FILE_PATH, MUSIC_PATH


load_dotenv()
S3_POOL_ID = os.getenv("S3_POOL_ID")
BUCKET_NAME = os.getenv("BUCKET_NAME")

def initialize() -> Communicator:
    # 通信用スレッド生成
    communicator = Communicator()  # Unityとの通信機

    return communicator


def main():
    communicator = initialize()

    # スレッドの開始
    communicator.start()
    open_calm.start()

    s3 = get_s3()
    # # 音ファイルアップロード
    # try:
    #     s3.Object(BUCKET_NAME, "music.wav").upload_file(MUSIC_PATH)
    #     print("+ Uploaded soundfile.")
    # except Exception as e:
    #     print(f"UPLOAD ERROR: {e}")

    while True:
        sleep_time = event_control_queue.get()
        plot(s3, sleep_time)

        # グラフアップロード
        try:
            s3.Object(BUCKET_NAME, "graph.png").upload_file(GRAPH_FILE_PATH)
            print("+ [3] Uploaded graphfile.")
        except Exception as e:
            print(f"UPLOAD ERROR: {e}")

        # CSVアップロード
        try:
            s3.Object(BUCKET_NAME, "sleep_data.csv").upload_file(CSV_FILE_PATH)
            print("+ [4] Uploaded csvfile.")
        except Exception as e:
            print(f"UPLOAD ERROR: {e}")

        # 音ファイルアップロード
        try:
            s3.Object(BUCKET_NAME, "music.wav").upload_file(MUSIC_PATH)
            print("+ [5] Uploaded soundfile.")
        except Exception as e:
            print(f"UPLOAD ERROR: {e}")

        time.sleep(1)

if __name__ == "__main__":
    main()