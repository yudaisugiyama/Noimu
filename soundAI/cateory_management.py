import torch
from .net import ShallowQNetwork


class CategoryManager:
    def __init__(self,
                  category_names=[["明るい", "暗い"],
                                  ["ジャズ", "ロック"]],
                  category_postfixes=["感じの", ""]):
        assert type(category_names[0][0]) is str, "category_names はデフォルト引数のように二次元配列で指定します"
        assert len(category_names) == len(category_postfixes), "各カテゴリに一つずつ postfix を設定してください。空文字列でも問題ありません。"

        self.category_names = category_names
        self.category_postfixes = category_postfixes

    def combination_tensor_to_text(self, input_tensor: torch.Tensor) -> str:
        """組み合わせを表す、ネットワークの入力テンソルをテキストに直す
        """
        assert sum(len(category) for category in self.category_names) == len(input_tensor), "カテゴリの数と入力テンソルの数が合いません"

        text = ""  # テキスト

        # それぞれのカテゴリに対して取得する
        for category, postfix in zip(self.category_names, self.category_postfixes):
            category_tensor = input_tensor[:len(category)]  # カテゴリを表す部分を取得する
            input_tensor = input_tensor[len(category):]  # このカテゴリに関する部分を取り除く
            assert sum(category_tensor) == 1, category_tensor

            selected_index = torch.where(category_tensor == 1.)[0].item()  # 戻り値は Tuple[torch.Tensor]
            text += category[selected_index]
            text += postfix

        return text

    def prompt_to_action_id(self, prompt: str, network: ShallowQNetwork) -> int:
        all_input_tensor = network.generate_all_input_combinations(debug=False)

        for i, input_tensor in enumerate(all_input_tensor):
            # ネットワークの入力形式を文字列に戻し、それとプロンプトが一致したらそのインデックス(≒id)を返す
            if prompt == self.combination_tensor_to_text(input_tensor):
                return i

        raise Exception("受け取ったプロンプトと一致するidがありません 鈴木")
