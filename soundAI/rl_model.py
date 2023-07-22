from collections import deque
import torch

from .net import ShallowQNetwork
from .cateory_management import CategoryManager


class RLModel:
    def __init__(self, categories=[["delightful", "depressing"], ["jazz", "rock"]], num_hidden=32) -> None:
        """強化学習モデルの生成

        Args:
            categories (list[str]): カテゴリのリスト
            num_hidden (_type_): 1層存在する隠れ層のノードの数
        """
        # カテゴリの数を数える
        num_categories = len(categories)
        num_category_contents = [len(category) for category in categories]

        # ネットワーク定義
        self.network = ShallowQNetwork(num_categories=num_categories, num_category_contents=num_category_contents, num_hidden=num_hidden)  # DQN風ネットワーク
        self.latest_actions = deque(maxlen=5)  # 直近の行動を記録
        self.latest_feedbacks = deque(maxlen=5)  # 直近のフィードバック（報酬）を記録

        # カテゴリ管理クラス
        self.catman = CategoryManager(category_names=categories, category_postfixes=[" ", "."])

    def add_feedback(self, feedback: dict) -> None:
        """学習に使う、ユーザーからのフィードバックを記録する

        Args:
            feedback (dict): MQQTで受け取った辞書
                以下は何となく
                "prompt_text": ユーザーに送信した音楽の生成に使ったプロンプト
                "elapsed_time": 起きるまでにかかった時間
        """
        # プロンプトを行動idと対応させて記録する
        action_id = self.catman.prompt_to_action_id(feedback["prompt_text"], self.network)
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
