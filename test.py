"""杉山用テスト用スクリプト

"""

from typing import *

from communication_thread import Communicator
from config import feedback_queue, open_calm

from utils import get_s3, plot


def initialize() -> Communicator:
    # 通信用スレッド生成
    communicator = Communicator()  # Unityとの通信機

    return communicator


def main():
    communicator = initialize()

    try:
        get_s3()
        print("+ Upload 'grapth.png'.")
    except Exception as e:
        print(f"S3 UPLOAD ERROR: {e}")

    # スレッドの開始
    communicator.start()
    open_calm.start()


if __name__ == "__main__":
    main()