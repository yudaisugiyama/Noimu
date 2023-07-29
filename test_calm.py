import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# 基本パラメータ
model_name = "cyberagent/open-calm-small"
peft_name = "lora-calm-small"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# モデルの準備
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32
)
model.to(device)

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
def generate(prompt, maxTokens=128) -> str:
    # 推論
    input_ids = tokenizer(prompt, return_tensors="pt", truncation=True).input_ids.to(device)
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
    output = tokenizer.decode(outputs)
    # print(output)
    return output

# generate("おはよ〜！今日の金沢の空は晴れだから、")