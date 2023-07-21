"""キューに送られてくる経過時間を使ってモデルを学習させるスレッド

- キューに経過時間が入ってくるので、なくなるまで学習を回す
    - Communicatorがキューに入れてくる
    - 空だった場合は待つ

- mqttから受け取った起きるまでの時間がFEEDBACK_TIME_QUEUEに入ってくるので、入り次第学習する
"""

from config import MUSIC_PATH
import threading
from soundAI.rl_model import RLModel
from queue import Queue

from audiocraft.data.audio import audio_write


class DQN(threading.Thread):
    def __init__(self, rl_model: RLModel, feedback_queue: Queue, prompt_queue: Queue) -> None:
        super().__init__()
        self.model = rl_model
        self.feedback_queue = feedback_queue
        self.prompt_queue = prompt_queue

    def run(self) -> None:
        while True:
            # 起きるまでにかかった時間を取得
            feedback: dict = self.feedback_queue.get()

            # 時間をモデルに渡して学習する
            self.model.add_feedback(feedback)
            self.model.learn()

            # wavをモデルから受け取る
            prompt, wav = self.model.choose_music()

            # wavを指定のパスに保存
            audio_write(MUSIC_PATH, wav.cpu(), self.model.music_gen.sample_rate, strategy="loudness", loudness_compressor=True)

            # キューにプロンプトを送信する
            self.prompt_queue.put(prompt)

