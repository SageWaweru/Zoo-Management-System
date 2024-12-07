import csv
from animal import Mammal, Bird, Reptile
from events import random_event

class Zoo:
    def __init__(self, name):
        self.name = name
        self.animals = [] 
        self.event_log = []  
        self.reputation = 100  
        self.finances = 0  
        self.ticket_prices = {  
            'child': 100,
            'adult': 200,
            'senior': 150
        }
        self.tickets_sold = { 
            'child': 0,
            'adult': 0,
            'senior': 0
        }
        self.special_event = False  

    def __len__(self):
        return len(self.animals)  

    def sell_ticket(self, ticket_type, quantity):
        if ticket_type not in self.ticket_prices:
            return "Invalid ticket type"
        
        price = self.ticket_prices[ticket_type]
        
        if self.special_event:
            price *= 1.5 

        total_cost = quantity * price
        self.tickets_sold[ticket_type] += quantity
        self.finances += total_cost
        return total_cost

    def start_special_event(self):
        self.special_event = True

    def end_special_event(self):
        self.special_event = False

    def add_animal(self, animal):
        if not any(a.name == animal.name for a in self.animals):  
            self.animals.append(animal)
            print(f"{animal.name} the {animal.species} has been added to the zoo.")
        else:
            print(f"{animal.name} already exists in the zoo.")

    def remove_animal(self, name):
        animal_to_remove = None
        for animal in self.animals:
            if animal.name.lower() == name.lower():
                animal_to_remove = animal
                break
        if animal_to_remove:
            self.animals.remove(animal_to_remove)
            print(f"{name} has been removed from the zoo.")
        else:
            print(f"Animal named {name} not found.")

    def display_animals(self):
        if not self.animals:
            print(f'No animals in the zoo.')
            return
        for animal in self.animals:
            print(f'{animal.name} ({animal.species})')
    
    def trigger_event(self, event_type=None):
            if event_type:
                if event_type == 'random':
                    event_description = random_event(self)
                # Add more event types here if needed (e.g., 'feeding', 'cleaning', etc.)
                else:
                    event_description = f"Unknown event type: {event_type}"
            else:
                event_description = random_event(self)
            
            self.add_event_to_log(event_description)
            print(f"Event Triggered: {event_description}")
    
    def add_event_to_log(self, event_description):
        self.event_log.append(event_description)
        print(f"Logged Event: {event_description}")

    def display_event_log(self):
        for event in self.event_log:
            print(event)
    def save_to_csv(self, filename):
        with open(filename, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Animal_class", "Species", "Gender", "Age", "Health"])
            for animal in self.animals:
                writer.writerow([animal.name, animal.animal_class, animal.species, animal.gender, animal.age, animal.health])
        print("Animal data has been saved to CSV.")

    def load_from_csv(self, filename):
        try:
            with open(filename, "r") as file:
                reader = csv.reader(file)
                next(reader)  # Skip header row
                loaded_any_animals = False
                for row in reader:
                    name, animal_class, species, gender, age, health = row
                    age = int(age)
                    health = int(health)
                    if type == "Mammal":
                        self.add_animal(Mammal(name, species, gender, age, health))
                        loaded_any_animals = True
                    elif type == "Bird":
                        self.add_animal(Bird(name, species, gender, age, health))
                        loaded_any_animals = True
                    elif type == "Reptile":
                        self.add_animal(Reptile(name, species, gender, age, health))
                        loaded_any_animals = True
                if not loaded_any_animals:
                    print(f"No animals were loaded from {filename}.")
            print(f"Animal data has been loaded from {filename}.")
        except FileNotFoundError:
            print(f"File {filename} not found.")
