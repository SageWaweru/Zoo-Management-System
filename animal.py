import csv
import os

class Animal:
    def __init__(self, name, animal_class, species, gender, age, health=100):
        self.name = name
        self.animal_class = animal_class.capitalize()
        self.species = species.lower()
        self.gender = gender
        self.age = age
        self.health = health  
        self.image_url = self.get_image_url()    

    def get_image_url(self):
        image_path = f"static/images/{self.animal_class}/{self.species}.jpg"
        if os.path.exists(image_path):
            return f"images/{self.animal_class}/{self.species}.jpg"
        else:
            return "images/{self.animal_class}/default.jpg"   
    
    def feed(self, food_type):
        if self.health < 100:
            self.health += 10
            self.health = min(self.health, 100)  
            print(f"{self.name} has been fed. Health is now {self.health}.")
        else:
            print(f"{self.name} is already fully healthy!")
    
    def health_status(self):
        print(f"{self.name} ({self.species}) - Health: {self.health}")


class Mammal(Animal):
    def __init__(self, name, species, gender, age, health=100):
        super().__init__(name, "Mammal", species, gender, age, health)


class Bird(Animal):
    def __init__(self, name, species, gender, age, health=100):  
        super().__init__(name, "Bird", species, gender, age, health)
        self.laid_eggs = []
        

class Reptile(Animal):
    def __init__(self, name, species, gender, age, health=100):  
        super().__init__(name, "Reptile", species, gender, age, health)
        self.laid_eggs = []
   

animals = [
    ["Name", "Animal_class", "Species", "Gender", "Age", "Health"],
    ["Ellie", "Mammal", "Elephant", "Female", 10, 90],
    ["Polly", "Bird", "Parrot", "Male", 3, 100],
    ["Slither", "Reptile", "Snake", "Male", 5, 80]
]


with open("animals.csv", "w", newline='') as file:
    writer = csv.writer(file)
    writer.writerows(animals)