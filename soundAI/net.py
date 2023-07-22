"""ネットワークを定義するファイル
"""
from typing import *
import torch
from torch import nn


class ShallowQNetwork(nn.Module):
    def __init__(self, num_categories: int, num_category_contents: List[int], num_hidden=4):
        super().__init__()
        self.num_category = num_categories  # カテゴリ数。感情やジャンルなど
        self.num_category_contents = num_category_contents.copy()  # 各カテゴリにどれだけのパターンがあるか。感情が（明るい・暗い）、ジャンルが（ロック・ジャズ）なら[2, 2]

        self.input_layer = torch.nn.Linear(sum(num_category_contents), num_hidden)  # num_hiddenは隠れ層のユニット数
        self.activation = torch.nn.ReLU()
        self.output_layer = torch.nn.Linear(num_hidden, 1)

        self.all_input_combinations = None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.input_layer(x)
        x = self.activation(x)
        x = self.output_layer(x)

        # ネットワークの出力を後処理して、理想的な出力の範囲に収める
        # とりあえず30秒の前後で出力するようにする
        x = x + 30
        return x

    def calc_all_qvalues(self, device="cpu") -> torch.Tensor:
        """全入力パターンと、それに対応するQ値を返す
        """
        all_inputs = self.generate_all_input_combinations(debug=False).to(device)
        all_outputs = self(all_inputs)

        inputs_outputs = [[input, output] for input, output in zip(all_inputs, all_outputs)]
        return inputs_outputs

    def generate_all_input_combinations(self, debug=False) -> torch.Tensor:
        """ネットワークの入力としてあり得る配列をすべて生成する
        """
        # 二回目以降は計算しない
        if self.all_input_combinations is not None:
            return self.all_input_combinations

        # 各カテゴリにおける、どの項目を選ぶかを示す入力形式（例えば、[0, 1]や[1, 0]など）のリスト
        category_onehot_list: List[Tuple[Tuple[int]]] = []

        # 各カテゴリ内でまずありうる可能性を列挙する
        for num_contents in self.num_category_contents:
            # カテゴリ内要素の選択を表すone-hotベクトルを全列挙する配列
            category_inside_selections = []

            for i in range(num_contents):
                # 選択されたカテゴリ内の要素だけ1のリストを作る
                content_selection = [0] * num_contents
                content_selection[i] = 1

                category_inside_selections.append(tuple(content_selection))

            category_onehot_list.append(tuple(category_inside_selections))

        if debug:
            print("category_onehot_list")
            print(category_onehot_list)

        # 各カテゴリの選択を結合する
        # すべての結合の組み合わせを生成する
        all_input_combinations = self._generate_each_combinations_recursively(category_onehot_list) # 組み合わせを生成する。どうにかして

        if debug:
            print("all_input_combinations")
            print(all_input_combinations)

        self.all_input_combinations = all_input_combinations
        return all_input_combinations

    def _generate_each_combinations_recursively(self, category_onehot_list: List[Tuple[Tuple[int]]], category_num=0) -> torch.Tensor:
        # 再帰の終了条件
        if category_num == self.num_category:
            return torch.tensor([[]])

        # 自身以降のカテゴリの組み合わせをすべて取得する
        combinations_after_me = self._generate_each_combinations_recursively(category_onehot_list, category_num + 1)

        # 自身以降のカテゴリの組み合わせと、自身の組み合わせをすべて生成する
        combinations = []
        for content in category_onehot_list[category_num]:
            content = torch.tensor(content)
            for combi in combinations_after_me:
                combinations.append(
                    torch.concat([
                        content, combi
                    ])
                )

        return torch.stack(combinations)
