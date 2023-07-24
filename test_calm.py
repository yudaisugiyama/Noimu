import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

# 基本パラメータ
model_name = "cyberagent/open-calm-small"
dataset = "kunishou/databricks-dolly-15k-ja"
peft_name = "lora-calm-small"
output_dir = "lora-calm-small-results"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# モデルの準備
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_8bit=True,
    device_map="auto",
)

# トークンナイザーの準備
tokenizer = AutoTokenizer.from_pretrained(model_name)

# LoRAモデルの準備
model = PeftModel.from_pretrained(
    model, 
    peft_name, 
    device_map="auto"
)

# 評価モード
model.eval()

# プロンプトテンプレートの準備
def generate_prompt(data_point):
    if data_point["input"]:
        return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{data_point["instruction"]}

### Input:
{data_point["input"]}

### Response:"""
    else:
        return f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{data_point["instruction"]}

### Response:"""


# テキスト生成関数の定義
def generate(prompt, maxTokens=128):
    # 推論
    input_ids = tokenizer(prompt, return_tensors="pt", truncation=True)

    # モデルのgenerateメソッドをCPUで実行するために、input_idsをCPUに移動
    input_ids = input_ids.to(torch.device('cpu'))

    outputs = model.generate(
        input_ids=input_ids,
        max_new_tokens=maxTokens,
        do_sample=True,
        temperature=0.7,
        top_p=0.75,
        top_k=40,
        no_repeat_ngram_size=2,
    )
    outputs = outputs[0].tolist()
    print(tokenizer.decode(outputs))

generate("おはよ〜！今日の長岡技術科学大学の空は晴れだから、")