import os
import boto3
import pandas as pd
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from datetime import datetime
from boto3.session import Session
from config import REGION, CSV_FILE_PATH, GRAPH_FILE_PATH

load_dotenv()
S3_POOL_ID = os.getenv("S3_POOL_ID")
BUCKET_NAME = os.getenv("BUCKET_NAME")


def get_s3():
    client = boto3.client('cognito-identity', REGION)

    # 1回目のアクセスでCognitoの認証IDを得る
    resp =  client.get_id(IdentityPoolId=f'{REGION}:{S3_POOL_ID}')

    # 2回目のアクセスでSessionを確立するための認証情報を得る
    resp = client.get_credentials_for_identity(IdentityId=resp['IdentityId'])
    secretKey = resp['Credentials']['SecretKey']
    accessKey = resp['Credentials']['AccessKeyId']
    token = resp['Credentials']['SessionToken']

    # 認証情報を用いて S3 Object にアクセスする
    session = Session(aws_access_key_id=accessKey,
                      aws_secret_access_key=secretKey,
                      aws_session_token=token,
                      region_name=REGION)
    s3 = session.resource('s3')

    return s3


s3 = get_s3()

def plot(time):
    try:
        s3.Object(BUCKET_NAME, "sleep_data.csv").download_file(CSV_FILE_PATH)
        print("+ Downloaded csvfile.")
    except Exception as e:
        print(f"DOWNLOAD ERROR: {e}")

    # 現在の日付を取得
    today = datetime.now()

    # 日付を指定した形式の文字列に変換（例：2023-07-24）
    formatted_date = today.strftime('%Y-%m-%d')

    # サンプルのデータを作成
    new_data = {
        'date': [f'{formatted_date}'],
        'sleep_time': [time]
    }

    # 新しい日付と睡眠時間をDataFrameに追加
    new_df = pd.DataFrame(new_data)

    # CSVファイルに保存されているデータを読み込む
    df = pd.read_csv(CSV_FILE_PATH)

    # 既存のDataFrameに新しいデータを追加
    df = pd.concat([df, new_df], ignore_index=True)

    # DataFrameをCSVファイルに保存
    df.to_csv(CSV_FILE_PATH, index=False)

    # 日付列と睡眠時間列を取得
    df = pd.read_csv(CSV_FILE_PATH)
    dates = pd.to_datetime(df['date'])
    sleep_duration = df['sleep_time']

    fontsize = 20

    # グラフを描画
    plt.figure(figsize=(9, 21))
    plt.bar(dates, sleep_duration, color='cyan')  # 色を水色に変更
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    # 軸ラベルのfontsizeを設定
    plt.xlabel('date', fontsize=fontsize)  # x軸ラベルのfontsizeを14に設定

    # 軸のfontsizeを設定
    plt.xticks(fontsize=fontsize)  # x軸のfontsizeを12に設定
    plt.yticks(fontsize=fontsize)  # y軸のfontsizeを12に設定

    # 凡例の表示と文字サイズの設定
    plt.legend(['sleep duration'], fontsize=fontsize)  # fontsizeを適宜調整

    # グラフをPNGファイルとして出力
    plt.savefig(GRAPH_FILE_PATH)

plot()

# try:
#     s3.Object(BUCKET_NAME, "graph.png").upload_file(GRAPH_FILE_PATH)
#     print("+ Uploaded graphfile.")
# except Exception as e:
#     print(f"UPLOAD ERROR: {e}")

# try:
#     s3.Object(BUCKET_NAME, "sleep_data.csv").upload_file(CSV_FILE_PATH)
#     print("+ Uploaded csvfile.")
# except Exception as e:
#     print(f"UPLOAD ERROR: {e}")