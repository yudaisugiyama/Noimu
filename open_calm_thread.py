"""ノイミューの言葉を生成するスレッド

"""

import os
import time
import torch
import requests
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer

import threading
from geopy.geocoders import Nominatim

import torch
from peft import PeftModel, PeftConfig
import scipy


class OpenCALM(threading.Thread):
    def __init__(self, prompt_queue, location):
        threading.Thread.__init__(self)
        self.model_name = "cyberagent/open-calm-small"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained("cyberagent/open-calm-small")

        self.prompt_queue = prompt_queue
        self.location = location

        # 基本パラメータ
        model_name = "cyberagent/open-calm-small"
        # dataset = "kunishou/databricks-dolly-15k-ja"
        peft_name = "./lora-calm-small"
        # output_dir = "lora-calm-small-results"

        # モデルの準備
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            load_in_8bit=True,
            device_map="auto",
        )

        # トークンナイザーの準備
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        # LoRAモデルの準備
        self.model = PeftModel.from_pretrained(
            self.model,
            peft_name,
            device_map="auto"
        )

        # 評価モード
        self.model.eval()
        self.generate("おはよ〜！今日の長岡技術科学大学の空は晴れだから、")

        # 天気情報取得
        # self.get_weather()
    
    # テキスト生成関数の定義
    def generate(self, prompt, maxTokens=128):
        # 推論
        input_ids = self.tokenizer(prompt, return_tensors="pt", truncation=True).to(self.device)
        outputs = self.model.generate(
            input_ids=input_ids,
            max_new_tokens=maxTokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.75,
            top_k=40,
            no_repeat_ngram_size=2,
        )
        outputs = outputs[0].tolist()
        print(self.tokenizer.decode(outputs))


    def run(self):
        # 天気情報取得
        # self.response = self.response.json()
        # self.weather = self.response['weather'][0]['description']

        while True:
            prompt = f"おはよ〜！今日の{self.location}の空は晴れだから、"
            # prompt = f"おはよ〜！今日の{self.location}の空は{self.weather}だから、"

            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            with torch.no_grad():
                tokens = self.model.generate(
                    **inputs,
                    max_new_tokens=64,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    repetition_penalty=1.05,
                    pad_token_id=self.tokenizer.pad_token_id,
                )

            output = self.tokenizer.decode(tokens[0], skip_special_tokens=True)
            output = output.replace('\n', '')
            self.prompt_queue.put(output)
            time.sleep(1)


    def get_location_info(self) -> tuple[str, str]:
        # 位置情報取得オブジェクトの生成
        geolocator = Nominatim(user_agent="noimu")

        # 現在地の緯度経度を取得
        location = geolocator.geocode(query=self.location)
        lat = location.latitude
        lon = location.longitude

        return str(lat), str(lon)
    
    def get_weather(self):
        # 天気API使用
        load_dotenv()
        self.api_key = os.getenv("API_TOKEN_OPEN_WEATHER_MAP")
        self.lat, self.lon = self.get_location_info()
        self.url = \
        f"https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={self.api_key}&lang=ja"
        self.response = requests.get(self.url)
