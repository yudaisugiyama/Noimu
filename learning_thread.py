"""キューに送られてくる経過時間を使ってモデルを学習させるスレッド

- キューに経過時間が入ってくるので、なくなるまで学習を回す
    - Communicatorがキューに入れてくる
    - 空だった場合は待つ

- mqttから受け取った起きるまでの時間がFEEDBACK_TIME_QUEUEに入ってくるので、入り次第学習する
"""

import threading
from soundAI.rl_model import RLModel


class DQN(threading.Thread):
    def __init__(self, rl_model: RLModel) -> None:
        super().__init__()
        self.rl_model = rl_model
        raise NotImplementedError

    def run(self) -> None:
        raise NotImplementedError
