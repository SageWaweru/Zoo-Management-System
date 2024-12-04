from animal import Mammal, Bird, Reptile

class Zookeeper:
    def __init__(self, name, zoo):
        self.name = name
        self.zoo = zoo

    def feed_animal(self, animal_name, food_type):
        for animal in self.zoo.animals:
            if animal.name == animal_name:
                animal.feed(food_type)
                print(f"{self.name} fed {animal_name}. Health: {animal.health}")
                return
        print(f"Animal {animal_name} not found.")

    def clean_habitat(self, animal_name):
        for animal in self.zoo.animals:
            if animal.name.lower() == animal_name.lower():
                    print(f"{self.name} cleaned the habitat of {animal.name} the {animal.species}.")
                    return
        print(f"No animal named {animal_name} found in the zoo.")   

    def create_mess(self,animal):
        print(f"Event: {animal.name} the {animal.species} has made a mess! The habitat needs cleaning!")
        self.clean_habitat(animal.name)
      

    def check_animal_health(self, animal_name):
        for animal in self.zoo.animals:
            if animal.name == animal_name:
                animal.check_health()
                return
        print(f"Animal {animal_name} not found.")

    def trigger_random_event(self):
        self.zoo.trigger_event()

    def saveData(self):
        self.zoo.save_to_file("zoo_data.json")

    def loadData(self):
        self.zoo.load_from_file("zoo_data.json")
