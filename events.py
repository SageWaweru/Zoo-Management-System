import random
from animal import Mammal, Bird, Reptile
from zookeeper import Zookeeper
from flask import flash

def create_mess(animal, zookeeper):
    event_description = f"Event: {animal.name} the {animal.species} made a mess! The habitat needs cleaning!"
    zookeeper.clean_habitat(animal.name)
    flash(event_description, "event_simulation")
    return event_description


def escape(zoo):
    if not zoo.animals:
        flash("No animals to escape.", "warning")
        return "No animals to escape."
    
    escapee = random.choice(zoo.animals)
    zoo.remove_animal(escapee.name)
    event_description = f"Event: {escapee.name} ({escapee.species}) has escaped from the zoo!"
    print(f"Escape event: {event_description}")
    flash(event_description, "event_simulation")
    return event_description

def visitors(zoo):
    event_description = "Event: A group of visitors has arrived at the zoo!"
    zoo.reputation += 5
    zoo.finances += 100
    flash(f"Zoo reputation increased! Finances boosted by $100.", "success")
    flash(event_description, "event_simulation")
    return event_description

def give_birth(zoo):
    female_mammals = [animal for animal in zoo.animals if isinstance(animal, Mammal) and animal.gender.lower() == "female"]
    if not female_mammals:
        flash("No female mammals available to give birth.", "warning")
        return "No female mammals available to give birth."
    
    mother = random.choice(female_mammals)
    baby_name = f"{mother.name}-Junior"
    baby_animal = Mammal(baby_name, mother.species, random.choice(["male", "female"]), 0, 50)
    zoo.add_animal(baby_animal)
    
    event_description = f"Event: {mother.name} the {mother.species} has given birth to {baby_name}!"
    flash(event_description, "event_simulation")
    return event_description

def lay_eggs(zoo):
    egg_laying_animals = [animal for animal in zoo.animals if isinstance(animal, (Bird, Reptile))]
    if not egg_laying_animals:
        flash("No egg-laying animals available to lay eggs.", "warning")
        return "No egg-laying animals available to lay eggs."
    
    parent = random.choice(egg_laying_animals)
    egg_id = f"Egg-{parent.name}-{len(parent.laid_eggs) + 1}"
    parent.laid_eggs.append(egg_id)
    event_description = f"Event: {parent.name} the {parent.species} has laid an egg! (Egg ID: {egg_id})"
    flash(event_description, "event_simulation")
    return event_description

def hatch_eggs(zoo):
    egg_laying_animals_with_eggs = [animal for animal in zoo.animals if isinstance(animal, (Bird, Reptile)) and animal.laid_eggs]
    if not egg_laying_animals_with_eggs:
        flash("No eggs available to hatch.", "warning")
        return "No eggs available to hatch."
    
    parent = random.choice(egg_laying_animals_with_eggs)
    egg_id = parent.laid_eggs.pop(0)
    baby_name = f"{parent.name}'s Hatchling"
    baby_animal = type(parent)(baby_name, parent.species, random.choice(["male", "female"]), 0, 50)
    zoo.add_animal(baby_animal)
    
    event_description = f"Event: {egg_id} has hatched! {parent.name} the {parent.species} is now the proud parent of {baby_name}."
    flash(event_description, "event_simulation")
    return event_description

def shedding(zoo):
    reptiles = [animal for animal in zoo.animals if isinstance(animal, Reptile)]
    if not reptiles:
        flash("No reptiles in the zoo to shed their skin.", "warning")
        return "No reptiles available to shed their skin."
    
    reptile = random.choice(reptiles)
    reptile.shedding()
    event_description = f"Event: {reptile.name} the {reptile.species} has shed its skin. The habitat needs cleaning!"
    flash(event_description, "event_simulation")
    return event_description


def random_event(zoo):
    events = [ escape, visitors, give_birth, lay_eggs, hatch_eggs, shedding]
    event = random.choice(events)  # Pick a random event
    
    try:
        event_description = event(zoo)  # Call the event function
        if event_description:
            zoo.add_event_to_log(event_description)  # Log the event
            flash(event_description, "event_simulation")  # Add a flash message
        else:
            flash("An event occurred, but no details are available.", "warning")
    except Exception as e:
        flash(f"Error during event: {e}", "danger")