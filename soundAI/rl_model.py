from collections import deque
import torch
import numpy as np
from audiocraft.models import MusicGen
import pprint

from .net import ShallowQNetwork
from .cateory_management import CategoryManager


class RLModel:
    def __init__(self, categories=[["delightful", "depressing"], ["jazz", "rock"]], num_hidden=32, replay_buffer_size=1) -> None:
        """強化学習モデルの生成

        Args:
            categories (list[str]): カテゴリのリスト
            num_hidden (int): 1層存在する隠れ層のノードの数
            replay_buffer_size (int): リプレイバッファ（バッファ全部使って学習する）のサイズ。ややこしいのでとりあえず1にしてある
        """
        # カテゴリの数を数える
        num_categories = len(categories)
        num_category_contents = [len(category) for category in categories]

        # ネットワーク定義
        self.network = ShallowQNetwork(num_categories=num_categories, num_category_contents=num_category_contents, num_hidden=num_hidden)  # DQN風ネットワーク
        self.latest_actions = deque(maxlen=replay_buffer_size)  # 直近の行動を記録
        self.latest_feedbacks = deque(maxlen=replay_buffer_size)  # 直近のフィードバック（報酬）を記録
        self.optimizer = torch.optim.Adam(self.network.parameters(), lr=0.2)
        self.loss_function = torch.nn.L1Loss()  # 誤差の絶対値

        # カテゴリ管理クラス
        self.catman = CategoryManager(category_names=categories, category_postfixes=[" ", "."])

        # 音楽生成モデルの定義
        self.music_gen: MusicGen = MusicGen.get_pretrained("medium")
        self.music_gen.set_generation_params(
            use_sampling=True,
            top_k=250,
            duration=2  # 2秒の音楽を生成
        )

    @property
    def all_prompts(self) -> list[str]:
        """全プロンプトを行動ID順に並べたリストを返す

        Returns:
            list[str]: プロンプトリスト
        """
        all_input_tensors = self.network.generate_all_input_combinations(debug=False)
        prompts = [
            self.catman.combination_tensor_to_text(input_tensor)
            for input_tensor in all_input_tensors
        ]
        return prompts

    def add_latest_prompt(self, prompt: str):
        """学習に使う、ユーザーからのフィードバックに対応する音楽のプロンプトを記録する

        Args:
            prompt (str): 音楽生成プロンプト
        """
        if not prompt in self.all_prompts:
            raise ValueError(prompt)
        # プロンプトを行動idと対応させて記録する
        action_id = self.catman.prompt_to_action_id(prompt, self.network)
        self.latest_actions.append(action_id)

    def add_feedback(self, feedback: float) -> None:
        """学習に使う、ユーザーからのフィードバックを記録する

        Args:
            feedback (float): MQQTで受け取った起床までにかかった時間
        """
        # フィードバックを記録する
        self.latest_feedbacks.append(feedback)

    def learn(self) -> None:
        """add_feedback()によって追加された経験を利用して学習を行う
        """
        assert len(self.latest_actions) == len(self.latest_feedbacks), f"num of actions != num replay buffer items. {len(self.latest_actions)} != {len(self.latest_feedbacks)}."

        input_outputs = self.network.calc_all_qvalues()
        outputs, targets = [], []
        for music, elapsed_time in zip(self.latest_actions, self.latest_feedbacks):
            outputs.append(input_outputs[music][1])
            targets.append(elapsed_time)
        outputs = torch.stack(outputs)
        targets = torch.tensor([targets]).T  # 転置するとちょうどよさそう？

        print("outputs", outputs)
        print("targets", targets)

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
        input_outputs = self.network.calc_all_qvalues()
        outputs = [-(i_o[1] - 30).item() for i_o in input_outputs]
        selected = self._softmax(outputs, 0.5, debug)

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
            q_values = {prompt : v for prompt, v in zip(self.all_prompts, values)}
            action_probs = {prompt : prob for prompt, prob in zip(self.all_prompts, p)}

            print("各行動のQ値は以下のようになります。")
            pprint.pprint(q_values, width=1)
            print(f"ソフトマックス行動選択(t={tau})の確率は以下のようになりました。")
            pprint.pprint(action_probs, width=1)

        action = np.random.choice(np.arange(len(values)), p=p)  # 確率分布pに従ってランダムで選択

        return action
