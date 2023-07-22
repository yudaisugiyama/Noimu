"""杉山用テスト用スクリプト

"""

from typing import *
import time

from communication_thread import Communicator
from config import feedback_queue, open_calm, event_control_queue

from utils import get_s3, plot


def initialize() -> Communicator:
    # 通信用スレッド生成
    communicator = Communicator()  # Unityとの通信機

    return communicator


def main():
    communicator = initialize()

    # スレッドの開始
    communicator.start()
    open_calm.start()

    # try:
    #     get_s3()
    #     print("+ Upload 'grapth.png'.")
    # except Exception as e:
    #     print(f"S3 UPLOAD ERROR: {e}")

    while True:
        key_name, file_name = event_control_queue.get()
        print(f"+ Upload {key_name} {file_name}.")
        time.sleep(1)

if __name__ == "__main__":
    main()