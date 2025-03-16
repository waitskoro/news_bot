import json

class Config:
    def __init__(self):
        self.__config = None
        self.__download_config('../config.json')

    def __download_config(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.__config = json.load(f)

    def get_database_config(self):
        return self.__config['database']

    def get_token_config(self):
        return self.__config['token']