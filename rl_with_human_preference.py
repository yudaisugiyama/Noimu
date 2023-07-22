from typing import *

from learning_thread import DQN
from communication_thread import Communicator

from soundAI.rl_model import RLModel

from config import feedback_queue, prompt_queue


def initialize() -> Tuple[DQN, Communicator]:
    """強化学習モデル生成 + 通信機の生成 + 各スレッドの生成

    Returns:
        Tuple[DQN, Communicator]: モデルスレッドとコミュニケーションスレッド
    """

    # 強化学習モデルとスレッド生成
    model = RLModel()  # モデル生成
    dqn = DQN(model, feedback_queue, prompt_queue)

    # 通信用スレッド生成
    communicator = Communicator()  # Unityとの通信機

    return dqn, communicator


def main():
    dqn, communicator = initialize()

    # スレッドの開始
    communicator.start()
    dqn.start()

    # 無限ループの終了待ち
    communicator.join()
    dqn.join()


if __name__ == "__main__":
    main()
