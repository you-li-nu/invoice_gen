import json
import random
import os.path
from os import path

class JsonLoader():
    def __init__(self, name):
        self.n = name
        file_name = "database/restaurants/" + name + ".json"
        print(file_name)
        with open(file_name) as json_file:
            self.locations = json.load(json_file)


    def new_item(self):
        i = random.randint(0, len(self.locations['businesses']) - 1)
        self.location = self.locations['businesses'][i]

    def get_name(self):
        return self.location.get('name')

    def get_address(self):
        return self.location.get('location').get('display_address')

    def get_phone(self):
        return self.location.get('display_phone')

    def has_logo(self):
        print (self.location.get('name'))
        return path.exists("database/logos/" + self.location.get('name') + ".png")

if __name__ == '__main__':
    location = JsonLoader("Evanston")
    location.new_item()
    print(location.get_name())
    print(location.get_address())
    print(location.get_phone())
    print(location.has_logo())

