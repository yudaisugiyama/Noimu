from collections import deque
import torch
import numpy as np

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
        assert len(self.latest_actions) == self.replay_buffer, f"num of actions != num replay buffer items. {len(self.latest_actions)} != {len(self.replay_buffer)}." \
                                                               f"最初の行動がlatest_actionsに入っていない可能性があります"

        input_outputs = self.rl_network.calc_all_qvalues()
        outputs, targets = [], []
        for music, elapsed_time in zip(self.latest_actions, self.replay_buffer):
            outputs.append(input_outputs[music][1])
            targets.append(elapsed_time)

        self.optimizer.zero_grad()
        loss = self.loss_function(outputs, targets)
        loss.backward()
        self.optimizer.step()

    def choose_music(self, debug=False) -> tuple[str, torch.Tensor]:
        """現在のQ値から音楽をソフトマックス行動選択する


        Returns:
            tuple[str, torch.Tensor]: 送信するプロンプトと、それによって生成した音楽
        """
        # プロンプトの選択
        # Softmax(-(Q - 30))で選択する
        # 30秒を基準にしているので、0周辺にリスケールし、
        # 値が小さい方が価値が高いのでマイナスをかける
        input_outputs = self.rl_network.calc_all_qvalues()
        outputs = [-(i_o[1] - 30) for i_o in input_outputs]
        selected = self._softmax(outputs, 1.0, debug)

        # 入力プロンプトの生成
        prompt = self.catman.combination_tensor_to_text(
            input_outputs[selected][0]
        )

        if debug:
            print(f"{prompt} の音楽を選択しました")

        # テキストから音楽の生成
        music: torch.Tensor = self.music_gen.generate(
            descriptions=[prompt],
            progress=True
        )
        assert music.shape[:2] == (1, 1)  # バッチ次元、行列の高さがそれぞれ1であることを確認
        return prompt, music[0]  # バッチ次元を削除

    def _softmax(self, values: list[float], tau=1.0, debug=True) -> int:
        """Q値を参照して音楽選択を行う

        ネットから持ってきた
        https://www.tcom242242.net/entry/ai-2/%E5%BC%B7%E5%8C%96%E5%AD%A6%E7%BF%92/softmax/

        Returns:
            int: プロンプトに対応するID
        """
        sum_exp_values = sum([np.exp(v/tau) for v in values])   # softmax選択の分母の計算
        p = [np.exp(v/tau)/sum_exp_values for v in values]      # 確率分布の生成

        if debug:
            print("ソフトマックス行動選択の確立は以下のようになりました。")
            print(p)

        action = np.random.choice(np.arange(len(values)), p=p)  # 確率分布pに従ってランダムで選択

        return action
