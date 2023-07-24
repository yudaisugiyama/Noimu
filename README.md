# Noimu | TNuts

### シーケンスフロー
```mermaid
sequenceDiagram
    participant Unity
    participant Python
    participant S3

    Unity->>+Unity: アラームを止める
    activate Unity
    Unity->>+Python: フィードバックの送信(compute_main_function)
    activate Python
    Python->>Python: OpenCALM
    Python-->>Unity: {"words": "noimu_words"}
    deactivate Unity
    deactivate Python
    Unity->>+Unity: ノイミューの吹き出し出力
    activate Python
    Python->>Python: 強化学習
    Python-->>S3: music.wav

    deactivate Python
    activate Python
    Python->>Python: 睡眠時間のグラフ作成
    Python-->>S3: graph.png
    deactivate Python

    Unity->>Unity: グラフ表示ボタンを押す
    activate Unity
    Unity->>+S3: graph.pngのダウンロードリクエスト
    S3-->>-Unity: graph.png
    Unity->>Unity: グラフ画面遷移
    deactivate Unity

    Unity->>+Unity: アラームを設定
    activate Unity
    Unity->>+Python: 音ファイルのリクエスト(sound_file)
    Python-->-Unity: {"value": "music.wav"}
    activate Python
    Unity->>+S3: music.wavのダウンロードリクエスト
    S3-->>-Unity: music.wav
    Unity->>Unity: アラーム設定完了
    deactivate Unity

    Unity->>+Unity: ノイミューにおやすみ（睡眠時間カウンタースタート）
```

### MQTT通信仕様

```
# Unity => Python

## フィードバックの送信
msg = {
    "request": "compute_main_function",
    "feedback": {
        "elapsed_time": 999,
        "sleep_time": 999,
    },
}


## 音ファイルのリクエスト
msg = {
    "request": "sound_file",
}



# Python => Unity

## ノイミューの言葉の送信
msg = {
    "request": "noimu_words",
    "value": "おはよ〜、今日の睡眠時間はxx時間で、・・・",
}


## 音ファイルのレスポンス
msg = {
    "request": "sound_file",
    "value": "music.wav",
}
```

### OpenCALMのLoRMファインチューニング

参考:
https://note.com/npaka/n/na5b8e6f749ce

データセット: @kun1em0nさんの[「kunishou/databricks-dolly-15k-ja」](https://github.com/kunishou/databricks-dolly-15k-ja)
