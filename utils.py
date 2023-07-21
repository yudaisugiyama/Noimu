import os

import boto3
from boto3.session import Session
from dotenv import load_dotenv

import pandas as pd
import matplotlib.pyplot as plt

from config import REGION


load_dotenv()
S3_POOL_ID = os.getenv("S3_POOL_ID")
BUKET_NAME = os.getenv("BUKET_NAME")

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


def plot():
    # CSVファイルのパス
    csv_file = "test.csv"
    s3 = get_s3()

    try:
        s3.Bucket(BUKET_NAME).download_file(csv_file, csv_file)
        print("CSVファイルのダウンロードが完了しました。")
    except:
        # ファイルが存在しない場合
        pass

    # 日付列と睡眠時間列を取得
    df = pd.read_csv(csv_file)
    dates = pd.to_datetime(df['date'])
    sleep_duration = df['sleep_time']

    # グラフを描画
    plt.figure(figsize=(10, 6))
    plt.plot(dates, sleep_duration, marker='o', linestyle='-')
    plt.xlabel('date')
    plt.ylabel('sleep time, hour')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    # グラフをPNGファイルとして出力
    grapth_file = "graph.png"
    plt.savefig(grapth_file)