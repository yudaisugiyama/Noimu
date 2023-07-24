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
from config import TYPE_OF_MUSIC

from audiocraft.data.audio import audio_write


class DQN(threading.Thread):
    def __init__(self, rl_model: RLModel, feedback_queue: Queue, audio_prompt_queue: Queue) -> None:
        super().__init__()
        self.model = rl_model
        self.feedback_queue = feedback_queue
        self.audio_prompt_queue = audio_prompt_queue

        # 最新の生成プロンプト
        # フィードバックが返ってきたらこの値のフィードバックと認識する
        # 最初の音楽の決定次第ここの値も変更する
        self.latest_prompt = self.model.catman.combination_tensor_to_text(
            self.model.network.generate_all_input_combinations()[0]
        )
        print("DQNクラスの初期化が完了しました。")
        print("学習前の最初の音楽生成プロンプトは以下のように認識しています。")
        print("\t" + self.latest_prompt)

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
            prompt, wav = self.model.choose_music()
            self.latest_prompt = prompt

            # wavを指定のパスに保存
            audio_write(os.path.splitext(MUSIC_PATH)[0], wav.cpu(), self.model.music_gen.sample_rate, strategy="loudness")

            # キューにプロンプトを送信する
            self.audio_prompt_queue.put(prompt)
