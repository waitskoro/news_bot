import json
import os

class Config:
    def __init__(self):
        self.__config = None
        self.__download_config()

    def __download_config(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, '..', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.__config = json.load(f)

    def get_database_config(self):
        return self.__config['database']

    def get_token_config(self):
        return self.__config['token']