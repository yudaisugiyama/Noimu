"""メインファイル

それぞれのスレッドを起動し、連携させる
"""
from typing import *
import os
import time

from learning_thread import DQN
from communication_thread import Communicator

from soundAI.rl_model import RLModel

from dotenv import load_dotenv
from utils import get_s3, plot
from config import CSV_FILE_PATH, GRAPH_FILE_PATH, MUSIC_PATH
from config import feedback_queue, open_calm, event_control_queue, rl_completion_flag_queue


load_dotenv()
S3_POOL_ID = os.getenv("S3_POOL_ID")
BUCKET_NAME = os.getenv("BUCKET_NAME")


def initialize() -> Tuple[DQN, Communicator]:
    """強化学習モデル生成 + 通信機の生成 + 各スレッドの生成

    Returns:
        Tuple[DQN, Communicator]: モデルスレッドとコミュニケーションスレッド
    """

    # 強化学習モデルとスレッド生成
    model = RLModel([["uptempo", "calm"], ["rock", "classic piano", "EDM"]], num_hidden=32, replay_buffer_size=1, debug=True)  # モデル生成
    dqn = DQN(model, feedback_queue, rl_completion_flag_queue, duration=20)  # スレッド生成

    # 通信用スレッド生成
    communicator = Communicator()  # Unityとの通信機

    return dqn, communicator


def main():
    dqn, communicator = initialize()

    # スレッドの開始
    communicator.start()
    dqn.start()
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
