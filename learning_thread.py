"""キューに送られてくる経過時間を使ってモデルを学習させるスレッド

- キューに経過時間が入ってくるので、なくなるまで学習を回す
    - Communicatorがキューに入れてくる
    - 空だった場合は待つ

- mqttから受け取った起きるまでの時間がFEEDBACK_TIME_QUEUEに入ってくるので、入り次第学習する
"""

from config import MUSIC_PATH
import os
import threading
from soundAI.rl_model import RLModel
from queue import Queue
import datetime

from audiocraft.data.audio import audio_write


class DQN(threading.Thread):
    def __init__(self, rl_model: RLModel, feedback_queue: Queue, rl_completion_flag_queue: Queue, duration=2) -> None:
        super().__init__()
        self.model = rl_model
        self.feedback_queue = feedback_queue
        self.rl_completion_flag_queue = rl_completion_flag_queue
        self.duration = duration

        # 最新の生成プロンプト
        # フィードバックが返ってきたらこの値のフィードバックと認識する
        # 最初の音楽の決定次第ここの値も変更する
        self.latest_prompt = "calm EDM."
        print("DQNクラスの初期化が完了しました。")
        print("最初の音楽生成プロンプトは以下の通りです。")
        print("\t" + self.latest_prompt)

        # ログ設定
        dt_now = datetime.datetime.now().isoformat()
        self.log_dir = "./log/log_dqn"
        self.log_filename = os.path.join(self.log_dir, dt_now[:19] + ".txt")
        self.audio_id = 0

    def run(self) -> None:
        while True:
            # 起きるまでにかかった時間を取得
            # おそらく時間のみ
            feedback: float = self.feedback_queue.get()  # communication_thread.py 52行目で送られてくる

            # 時間をモデルに渡して学習する
            self.model.add_latest_prompt(self.latest_prompt)
            self.model.add_feedback(feedback)
            self.model.learn()

            # wavをモデルから受け取る
            prompt, wav = self.model.choose_music(self.duration)
            self.latest_prompt = prompt

            # wavを指定のパスに保存
            audio_write(os.path.splitext(MUSIC_PATH)[0], wav.cpu(), 32000, strategy="loudness")

            # ログとっとく
            self._log(prompt, wav)

            # キューにプロンプトを送信する
            self.rl_completion_flag_queue.put(True)

    def _log(self, prompt, wav) -> None:
        """ログの保存"""
        now = datetime.datetime.now().isoformat()
        with open(self.log_filename, "a") as f:
            f.write(f"{prompt} {now}")

        audio_name = prompt + "_" + now
        audio_path = os.path.join(self.log_dir, audio_name)
        audio_write(audio_path, wav.cpu(), 32000, strategy="loudness")
