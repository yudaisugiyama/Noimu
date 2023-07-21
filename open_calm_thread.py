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

from config import prompt_queue, LOCATION

class OpenCALM(threading.Thread):
    def __init__(self, prompt_queue, location):
        threading.Thread.__init__(self)
        self.model_name = "cyberagent/open-calm-small"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained("cyberagent/open-calm-small")

        # 天気API使用
        # load_dotenv()
        # self.api_key = os.getenv("API_TOKEN_OPEN_WEATHER_MAP")
        # self.prompt_queue = prompt_queue
        # self.location = location
        # self.lat, self.lon = self.get_location_info()
        # self.url = \
        # f"https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={self.api_key}&lang=ja"
        # self.response = requests.get(self.url)

    def run(self):
        self.response = self.response.json()
        self.weather = self.response['weather'][0]['description']

        prompt = f"おはよ〜！今日の長岡技術科学大学の空は厚い雲だから、"

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


    def get_location_info(self) -> tuple[str, str]:
        # 位置情報取得オブジェクトの生成
        geolocator = Nominatim(user_agent="noi-mu")

        # 現在地の緯度経度を取得
        location = geolocator.geocode(query=self.location)
        lat = location.latitude
        lon = location.longitude

        return str(lat), str(lon)