from langchain.text_splitter import CharacterTextSplitter

import json
import csv
import os
import time
from pathlib import Path
from charset_normalizer import from_path

def detect_encoding(file_path):
    result = from_path(file_path).best()
    return result

def get_all_txt_files(directory):
    txt_files = []
    # 指定したディレクトリ以下を再帰的に走査
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt") and file != "res.txt":
                # ファイルの絶対パスを取得
                txt_files.append(os.path.join(root, file))
    return txt_files

def get_all_json_files(directory):
    txt_files = []
    # 指定したディレクトリ以下を再帰的に走査
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                # ファイルの絶対パスを取得
                txt_files.append(os.path.join(root, file))
    return txt_files

# JSONデータをCSVに書き出す関数
def json_to_csv(json_data, csv_file_path):
    
    # CSVファイルを書き込みモードで開く
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        # CSVファイルに書き込むためのライターを作成
        writer = csv.DictWriter(csvfile, fieldnames=["title", "content"])
        
        # ヘッダーを書き込む
        writer.writeheader()
        
        # 各セクションをCSVに書き込む
        for section in json_data:
            writer.writerow(section)

def concatText(whisper_res):
    text = ''
    for idx, res in enumerate(whisper_res):
        if idx == len(whisper_res)-1:
            text += res['text']
        else:
            text += res['text'] + "\n"
    return text

def save(result, out_path):
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    time.sleep(1)

text_splitter = CharacterTextSplitter(
    separator = "。",  # セパレータ
    chunk_size = 4000,  # チャンクの文字数
    chunk_overlap = 0,  # チャンクオーバーラップの文字数
)
