import random
from animal import Mammal, Bird, Reptile
from zookeeper import Zookeeper

def create_mess(animal, zookeeper):
    print(f"Event: {animal.name} the {animal.species} has made a mess! The habitat needs cleaning!")
    zookeeper.clean_habitat(animal.name)

def fall_sick(animals):
    if not animals:
        print("No animals available to get sick")
        return
    sick_animal = random.choice(animals)
    health_loss = random.randint(10, 30)
    sick_animal.health -= health_loss
    sick_animal.health = max(0, sick_animal.health)
    print(f"Event: {sick_animal.name} ({sick_animal.species}) got sick and lost {health_loss} health!")
    if sick_animal.health == 0:
        print(f"Warning: {sick_animal.name} needs urgent care or might die!")
            
    create_mess(sick_animal)


def escape(zoo):
    if not zoo.animals:
        print("No animals to escape.")
        return
    escapee = random.choice(zoo.animals)
    zoo.remove_animal(escapee.name)  
    print(f"Event: {escapee.name} ({escapee.species}) has escaped from the zoo!")
    create_mess(escapee)


def visitors(zoo):
    print("Event: A group of visitors has arrived at the zoo!")
    zoo.reputation += 5
    zoo.finances += 100  
    print(f"Zoo reputation: {zoo.reputation}, Finances: ${zoo.finances}")


def give_birth(zoo):
    female_mammals = [animal for animal in zoo.animals if isinstance(animal, Mammal) and animal.gender.lower() == "female"]
    if not female_mammals:
        print("No female mammals available to give birth.")
        return
    
    mother = random.choice(female_mammals)
    baby_name = input(f"{mother.name} just gave birth! Enter a name for {mother.name}'s baby: ")
    baby_animal = Mammal(baby_name, mother.species, mother.gender, 0, 50)  
    zoo.add_animal(baby_animal)
    print(f"Event: {mother.name} the {mother.species} has given birth to {baby_name}!")
    create_mess(mother)

def lay_eggs(zoo):
    egg_laying_animals = [animal for animal in zoo.animals if isinstance(animal, (Bird, Reptile))]
    if not egg_laying_animals:
        print("No egg-laying animals available to lay eggs.")
        return

    parent = random.choice(egg_laying_animals)
    egg_id = f"Egg-{parent.name}-{len(parent.laid_eggs) + 1}"
    parent.laid_eggs.append(egg_id)
    print(f"Event: {parent.name} the {parent.species} has laid an egg! (Egg ID: {egg_id})")
    create_mess(parent)


def hatch_eggs(zoo):
    egg_laying_animals_with_eggs = [animal for animal in zoo.animals if isinstance(animal, (Bird, Reptile)) and animal.laid_eggs]
    if not egg_laying_animals_with_eggs:
        print("No eggs available to hatch.")
        return

    parent = random.choice(egg_laying_animals_with_eggs)
    egg_id = parent.laid_eggs.pop(0)
    baby_name = f"{parent.name}'s Hatchling"
    baby_animal = type(parent)(baby_name, parent.species, parent.gender, 0, 50)  
    zoo.add_animal(baby_animal)
    print(f"Event: {egg_id} has hatched! {parent.name} the {parent.species} is now the proud parent of {baby_name}.")
    create_mess(parent)

def shedding(zoo):
    reptiles = [animal for animal in zoo.animals if isinstance(animal, Reptile)]
    if not reptiles:
        print("No reptiles in the zoo to shed their skin.")
        return

    reptile = random.choice(reptiles)
    reptile.shedding()
    print(f"Event: {reptile.name} the {reptile.species} has shed its skin. The habitat needs cleaning!")
    create_mess(reptile)
    return reptile  

def care_for_animal(zoo):
    sick_animals = [animal for animal in zoo.animals if animal.health < 100]
    if sick_animals:
        animal_to_care_for = random.choice(sick_animals)
        health_boost = random.randint(5, 20)
        animal_to_care_for.health += health_boost
        animal_to_care_for.health = min(animal_to_care_for.health, 100) 
        print(f"Event: {animal_to_care_for.name} has been cared for and gained {health_boost} health!")
    else:
        print("No sick animals to care for.")

def random_event(zoo):
    events = [fall_sick, escape, visitors, give_birth, lay_eggs,hatch_eggs, care_for_animal, shedding]
    event = random.choice(events)
    event(zoo) 