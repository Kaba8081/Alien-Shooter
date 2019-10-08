# classes for 'Alien Shooter' server
from os import path
import pickle

player_save_template = '[]'

class Player:
    def __init__(self):
        pass
    def set_variables(self, nickname, id):
        self.nickname, self.id = str(nickname), id
    def load_data(self):
        if path.isfile(path.join('saves', self.nickname)):
            with open(path.join('saves', self.nickname), 'rb') as file:
                return pickle.load(file)
        else:
            with open(path.join('saves', self.nickname), 'wb') as file:
                pickle.dump(player_save_template, file, pickle.HIGHEST_PROTOCOL)
                return player_save_template
    
    def save_data(self, player_save):
        with open(path.join('saves', self.nickname), 'wb') as file:
            pickle.dump(player_save, file, pickle.HIGHEST_PROTOCOL)
            return 1