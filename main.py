from zoo import Zoo
from zookeeper import Zookeeper
from animal import Animal,Mammal, Bird, Reptile
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__) 

@app.route("/")
def home():
    animals = [
        Mammal("Lea","Lion", "Female", 5),
        Mammal("Ellie", "Elephant", "Male", 10),
        Bird("Polly", "Parrot","Female", 3),
        Reptile("Coco", "Snake", "Female", 2 ),
        Bird("Fifi", "Flamingo", "Female", 6),
        Reptile("Oreo","Lizard", "Male", 2)
    ]
    zoo_name = "Jungle Haven Zoo"
    return render_template("home.html", zoo_name=zoo_name, animals=animals)

@app.route("/zookeeper")
def employee():
 return render_template("zookeeper.html")
# def main():
    
#     print("Welcome to ZooMaster!")
#     zoo_name = input("Enter the name of the zoo: ")
#     zookeeper_name = input("Enter the name of the zookeeper: ")
    
#     my_zoo = Zoo(zoo_name)
#     zookeeper = Zookeeper(zookeeper_name, my_zoo)
#     my_zoo.load_from_csv("animals.csv")

#     while True:
#         print("\n1. Display animals")
#         print("2. Add animal")
#         print("3. Remove animal")
#         print("4. Trigger random event")
#         print("5. Save data")
#         print("6. Load data")
#         print("7. Exit")
        
#         choice = input("Choose an option: ")
        
#         if choice == "1":
#             my_zoo.display_animals()
#         elif choice == "2":
#             name = input("Name: ")
#             species = input("Species: ")
#             gender = input("Gender: ")
#             age = int(input("Age: "))
#             type = input("Type (Mammal/Bird/Reptile): ").capitalize()
            
#             if type == "Mammal":
#                 my_zoo.add_animal(Mammal(name, species, gender, age))
#             elif type == "Bird":
#                 my_zoo.add_animal(Bird(name, species, gender, age))
#             elif type == "Reptile":
#                 my_zoo.add_animal(Reptile(name, species, gender, age))
#             else:
#                 print("Invalid type!")
#         elif choice == "3":
#             name = input("Enter the name of the animal to remove: ")
#             my_zoo.remove_animal(name)
#         elif choice == "4":
#             zookeeper.trigger_random_event()
#         elif choice == "5":
#             my_zoo.save_to_csv("animals.csv")
#         elif choice == "6":
#             my_zoo.load_from_csv("animals.csv")
#         elif choice == "7":
#             print("Goodbye!")
#             break
#         else:
#             print("Invalid choice, please try again.")

if __name__ == "__main__":
    # main()
    app.run(debug=True)
