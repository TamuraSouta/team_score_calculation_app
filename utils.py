import os
import pickle

def save_data(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)  # ディレクトリが存在しない場合は作成
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)

def load_data(filepath):
    if not os.path.exists(filepath):
        return {}  # ファイルが存在しない場合は空の辞書を返す
    with open(filepath, 'rb') as f:
        return pickle.load(f)
