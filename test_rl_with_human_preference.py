from typing import *

from communication_thread import Communicator
from open_calm_thread import OpenCALM
from config import feedback_queue


def initialize() -> Communicator:
    """強化学習モデル生成 + 通信機の生成 + 各スレッドの生成

    Returns:
        Tuple[DQN, Communicator]: モデルスレッドとコミュニケーションスレッド
    """

    # 強化学習モデルとスレッド生成
    # open_calm = OpenCALM()

    # 通信用スレッド生成
    communicator = Communicator()  # Unityとの通信機

    return communicator


def main():
    communicator = initialize()

    # スレッドの開始
    communicator.start()
    # open_calm.start()


if __name__ == "__main__":
    main()
