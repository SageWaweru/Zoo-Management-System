import csv
import os

class Animal:
    def __init__(self, name, animal_class, species, gender, age, food, health_status="Healthy", uploaded_image_path=None):
        self.name = name
        self.animal_class = animal_class.capitalize()
        self.species = species.lower()
        self.gender = gender
        self.age = age
        self.food = food  
        self.health_status = health_status
        self.health_history = [] 
        self.image_url = self.get_image_url(uploaded_image_path)

    def get_image_url(self, uploaded_image_path=None):
        if uploaded_image_path:
            # Return the custom uploaded image if provided
            return uploaded_image_path
        
        # If no uploaded image is provided, check for a specific image path
        image_path = f"static/images/{self.animal_class}/{self.species}.jpg"
        if os.path.exists(image_path):
            # Return the specific image for the class and species if it exists
            return f"images/{self.animal_class}/{self.species}.jpg"
        
        # If neither exists, return the default image for the class
        return f"images/{self.animal_class}/default.jpg"
    
    def feed(self):
        print(f"{self.name} has been fed.")

    def edit_details(self, name=None, animal_class=None, species=None, gender=None, age=None, food=None,uploaded_image_path=None):
        if name:
            self.name = name
        if animal_class:
            self.animal_class = animal_class.capitalize()
        if species:
            self.species = species.lower()
        if gender:
            self.gender = gender
        if age is not None:
            self.age = age
        if food:
            self.food = food
        
        self.image_url = self.get_image_url(uploaded_image_path)        
        print(f"Details updated for {self.name}.")     

    def update_health_status(self, health_status, description=""):
        self.health_status = health_status
        self.health_history.append({
            "status": health_status,
            "description": description,
            "age": self.age 
        })

    def clear_health_history(self):
        self.health_history = []
            
class Mammal(Animal):
    def __init__(self, name, species, gender, age, food):
        super().__init__(name, "Mammal", species, gender, age, food)


class Bird(Animal):
    def __init__(self, name, species, gender, age, food):  
        super().__init__(name, "Bird", species, gender, age, food)
        self.laid_eggs = []
        

class Reptile(Animal):
    def __init__(self, name, species, gender, age, food):  
        super().__init__(name, "Reptile", species, gender, age, food)
        self.laid_eggs = []
   

def load_animals_from_csv():
    animals = []
    try:
        with open("animals.csv", "r") as file:
            reader = csv.reader(file)
            next(reader)  
            for row in reader:
                name, animal_class, species, gender, age, food = row
                age = int(age)
                
                if animal_class.lower() == "mammal":
                    animal = Mammal(name, species, gender, age, food)
                elif animal_class.lower() == "bird":
                    animal = Bird(name, species, gender, age, food)
                elif animal_class.lower() == "reptile":
                    animal = Reptile(name, species, gender, age, food)
                else:
                    continue  
                
                animals.append(animal)
    except FileNotFoundError:
        print("No animal data file found.")
    
    return animals

def save_animals_to_csv(animals):
    with open("animals.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Animal_class", "Species", "Gender", "Age", "Food"])
        for animal in animals:
            writer.writerow([animal.name, animal.animal_class, animal.species, animal.gender, animal.age, animal.food])

animals = load_animals_from_csv()

for animal in animals:
    print(f"{animal.name} - {animal.species}")

polly = next(animal for animal in animals if animal.name == "Polly")
polly.feed()

slither = next(animal for animal in animals if animal.name == "Slither")
slither.update_health_status("Sick")

save_animals_to_csv(animals)

print(f"Updated health status for Slither: {slither.health_status}")
