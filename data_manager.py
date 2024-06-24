import os
import pickle

def load_data(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    else:
        return {}

def save_data(data, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)
        