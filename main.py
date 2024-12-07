from zoo import Zoo
from zookeeper import Zookeeper
from animal import Animal,Mammal, Bird, Reptile
from events import random_event 
from flask import Flask, render_template, request, redirect, url_for, flash,session
import os
from werkzeug.utils import secure_filename
from functools import wraps
import firebase_admin
from firebase_admin import auth, credentials
from firebase_admin.exceptions import FirebaseError
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user,current_user


app = Flask(__name__) 

app.secret_key = os.getenv('SECRET_KEY', 'default_fallback_key')


cred = credentials.Certificate('zoo-management-cbf7c-firebase-adminsdk-bbk8s-c93028b3a3.json')
firebase_admin.initialize_app(cred)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

users = {}

class User(UserMixin):
    def __init__(self, uid, email, claims):
        self.id = uid
        self.email = email
        self.claims = claims

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.create_user(email=email, password=password)
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except FirebaseError as e:
            flash(f"Error: {str(e)}", "danger")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.get_user_by_email(email)
            # Simulate password check (replace with real validation)
            if user:
                claims = user.custom_claims or {}
                user_obj = User(user.uid, email, claims)
                users[user.uid] = user_obj
                login_user(user_obj)
                session['user_claims'] = claims
                flash("Login successful!", "success")
                return redirect(url_for("home"))
        except FirebaseError as e:
            flash("Invalid email or password", "danger")
        except Exception as e:
            flash(f"Unexpected error: {str(e)}", "danger")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

def employee_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_claims = session.get('user_claims', {})
        if not user_claims.get('employee'):
            flash("Access denied. Employees only.", "danger")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


zoo_name = "Jungle Haven Zoo"
animals = [
        Mammal("Lea","Lion", "Female", 5, "Meat"),
        Mammal("Ellie", "Elephant", "Male", 10, "Leaves"),
        Bird("Polly", "Parrot","Female", 3, "Seeds"),
        Reptile("Coco", "Snake", "Female", 2 ,"Rats"),
        Bird("Fifi", "Flamingo", "Female", 6, "Fish"),
        Reptile("Oreo","Lizard", "Male", 2, "Insects")
]

zookeeper = Zookeeper("Sage","Jungle Haven Zoo")

@app.route("/")
def home():
    return render_template("home.html", zoo_name=zoo_name, animals=animals)

@app.route("/zookeeper")
@employee_required
def zookeeper_page():
 if request.method == "POST":
        if "add_animal" in request.form:
            # Add animal logic
            flash("Animal added successfully!", "add_animal")
        elif "delete_animal" in request.form:
            # Delete animal logic
            flash("Animal deleted successfully!", "delete_animal")
        elif "edit_animal" in request.form:
            # Edit animal logic
            flash("Animal details updated successfully!", "edit_animal")
        elif "update_health" in request.form:
            # Update health status logic
            flash("Animal health status updated successfully!", "health_update")
        elif "simulate_event" in request.form:
            # Simulate event logic
            flash("Event simulated successfully!", "event_simulation")

 return render_template("zookeeper.html", zoo_name=zoo_name, animals=animals)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/add_animal", methods=["GET", "POST"])
def add_animal():
    if request.method == "POST":
        name = request.form["name"]
        species = request.form["species"]
        gender = request.form["gender"]
        age = int(request.form["age"])
        food = request.form["food"]
        animal_class = request.form["animal_class"]
        
        uploaded_image_path = None  

        uploaded_file = request.files.get("image")  
        
        if uploaded_file:
            filename = secure_filename(f"{species.lower()}_{uploaded_file.filename}")
            upload_folder = os.path.join("static", "images", animal_class)
            
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)  
                
            uploaded_image_path = os.path.join(upload_folder, filename)
            uploaded_file.save(uploaded_image_path) 

            uploaded_image_path = f"images/{animal_class}/{filename}"

        new_animal = Animal(
            name=name,
            animal_class=animal_class,
            species=species,
            gender=gender,
            age=age,
            food=food,
            uploaded_image_path=uploaded_image_path  
        )

        animals.append(new_animal)
        flash(f"Animal {name} added successfully!", 'add_animal')
        
        return redirect(url_for("zookeeper_page"))
    
    return render_template("add.html")   
   

@app.route("/remove_animal", methods=["POST"])
def remove_animal():
    animal_name = request.form["animal_name"]

    global animals
    animals = [animal for animal in animals if animal.name.lower() != animal_name.lower()]
    flash(f"Animal {animal_name} removed successfully!", "delete_animal")
    return redirect(url_for("zookeeper_page"))
    

from werkzeug.utils import secure_filename
import os
from flask import request, redirect, url_for, flash

@app.route("/edit_animal/<animal_name>", methods=["GET", "POST"])
def edit_animal(animal_name):
    animal = next((a for a in animals if a.name == animal_name), None)

    if not animal:
        flash("Animal not found!", "danger")
        return redirect(url_for('zookeeper_page'))

    if request.method == "POST":
        name = request.form["name"]
        animal_class = request.form["animal_class"]
        food = request.form["food"]
        gender = request.form["gender"]
        age = int(request.form["age"])

        uploaded_image_path = animal.image_url

        uploaded_file = request.files.get("image")
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            upload_folder = os.path.join("static", "images", animal_class)
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            uploaded_image_path = os.path.join(upload_folder, filename)
            uploaded_file.save(uploaded_image_path)
            uploaded_image_path = f"images/{animal_class}/{filename}"

        animal.edit_details(name=name, animal_class=animal_class, species=animal.species, gender=gender, age=age, food=food)
        animal.image_url = uploaded_image_path  

        flash(f"Animal {name}'s details updated successfully!", "edit_animal")
        return redirect(url_for("zookeeper_page"))

    return render_template("edit.html", animal=animal)

zoo = Zoo ("Jungle Haven Zoo")

@app.route("/trigger_event", methods=["POST"])
def trigger_event():
    event_type = request.form.get("event_type")
    
    # Retrieve the zoo object from session
    zoo = session.get("zoo")
    
    if not zoo:
        flash("Zoo object not found.", "event_simulation")
    
    if event_type == "feeding":
        flash("Time to feed the animals!", "event_simulation")
    elif event_type == "cleaning":
        flash("Animal habitats have been cleaned.", "event_simulation")
    elif event_type == "random_event":
        event_description = random_event(zoo) 
        flash(event_description, "event_simulation")
    else:
        flash("Unknown event type!", "warning")
    
    return redirect(url_for("zookeeper_page"))

@app.route("/tickets", methods=["GET", "POST"])
def tickets_page():
    # Fetch tickets data (e.g., from database)
    tickets = [
        {"id": 1, "name": "Concert A", "price": 50},
        {"id": 2, "name": "Concert B", "price": 75},
        {"id": 3, "name": "Concert C", "price": 100},
    ]

    if request.method == "POST":
        flash("You need to log in to purchase tickets!", "warning")
        return redirect(url_for('login'))

    return render_template("tickets.html", tickets=tickets)


@app.route('/buy_tickets', methods=['GET', 'POST'])
# @login_required
def buy_tickets():
    if not current_user.is_authenticated:
        # Flash a message to notify the user
        flash("You need to log in or register to purchase tickets.", "warning")
        return redirect(url_for("tickets_page"))  # Redirect to the login page

    if request.method == 'POST':
        ticket_type = request.form['ticket_type']
        try:
            quantity = int(request.form['quantity'])
            if quantity <= 0:
                flash("Please enter a valid number of tickets.", "ticket_error")
                return redirect(url_for('buy_tickets'))

            total_cost = zoo.sell_ticket(ticket_type, quantity)
            if isinstance(total_cost, str):
                flash(total_cost, "danger")
                return redirect(url_for('buy_tickets'))
            
            flash(f"Successfully purchased {quantity} {ticket_type} ticket(s) for Ksh{total_cost}.", "ticket_message")
            return redirect(url_for('buy_tickets'))
        
        except ValueError:
            flash("Invalid input. Please enter a valid number.", "ticket_error")
            return redirect(url_for('buy_tickets'))
    return render_template("buytickets.html", ticket_prices=zoo.ticket_prices)


@app.route("/health_status", methods=["GET", "POST"])
def health_status():
    animal_name = None
    health_status = None
    description = None

    if request.method == "POST":
        animal_name = request.form["animal_name"]
        health_status = request.form["health_status"]
        description = request.form.get("description", "")  

        animal = next((a for a in animals if a.name.lower() == animal_name.lower()), None)
        
        if animal:
            animal.update_health_status(health_status, description)
            flash(f"Health status of {animal_name} updated to {health_status}.", "health_update")
        else:
            flash("Animal not found!", "danger")

    else: 
        animal_name = request.args.get("animal_name", None)
        if animal_name:
            animal = next((a for a in animals if a.name.lower() == animal_name.lower()), None)
            if animal:
                health_status = animal.health_status
                description = ""  

    return render_template( "health.html",animals=animals,animal_name=animal_name,health_status=health_status,description="")

@app.route("/clear_health_history", methods=["POST"])
def clear_health_history():
    animal_name = request.form["animal_name"]
    animal = next((a for a in animals if a.name.lower() == animal_name.lower()), None)

    if animal:
        animal.clear_health_history()
        flash(f"Health history of {animal_name} has been cleared.", "health_update")
    else:
        flash("Animal not found!", "danger")

    return redirect(url_for('health_status')) 


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
