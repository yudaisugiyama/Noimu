from collections import deque
import torch


class RLModel:
    def __init__(self) -> None:
        self.network = ...  # DQN風ネットワーク
        self.latest_actions = deque(5)  # 直近の行動を記録
        self.latest_feedbacks = deque(5)  # 直近のフィードバック（報酬）を記録
        raise NotImplementedError

    def add_feedback(self, feedback: dict) -> None:
        """学習に使う、ユーザーからのフィードバックを記録する

        Args:
            feedback (dict): MQQTで受け取った辞書
                以下は何となく
                "prompt_text": ユーザーに送信した音楽の生成に使ったプロンプト
                "elapsed_time": 起きるまでにかかった時間
        """
        # プロンプトを行動idと対応させて記録する
        action_id = self._prompt2action_id(feedback["prompt_text"])
        self.latest_actions.append(action_id)

        # フィードバックを記録する
        self.latest_feedbacks.append(feedback["elapsed_time"])

    def learn(self) -> None:
        """add_feedback()によって追加された経験を利用して学習を行う
        """
        raise NotImplementedError

    def choose_music(self) -> tuple[str, torch.Tensor]:
        """現在のQ値から音楽をソフトマックス行動選択する


        Returns:
            tuple[str, torch.Tensor]: 送信するプロンプトと、それによって生成した音楽
        """
        raise NotImplementedError

    def _softmax(self) -> int:
        """Q値を参照して音楽選択を行う

        Returns:
            int: プロンプトに対応するID
        """
        raise NotImplementedError
