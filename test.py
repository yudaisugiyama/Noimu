"""杉山用テスト用スクリプト

"""

from typing import *

from communication_thread import Communicator
from open_calm_thread import OpenCALM
from config import feedback_queue


def initialize() -> Communicator:
    # LLMモデルとスレッド生成
    open_calm = OpenCALM()

    # 通信用スレッド生成
    communicator = Communicator()  # Unityとの通信機

    return open_calm, communicator


def main():
    open_calm, communicator = initialize()

    # スレッドの開始
    communicator.start()
    open_calm.start()


if __name__ == "__main__":
    main()
