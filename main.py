from zoo import Zoo
from zookeeper import Zookeeper
from animal import Animal, Mammal, Bird, Reptile
from events import random_event 
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import firebase_admin
from firebase_admin import auth, credentials
from firebase_admin.exceptions import FirebaseError
from flask_session import Session
from datetime import timedelta
import logging

# Initialize Flask app and configurations
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_fallback_key')
app.config['SESSION_COOKIE_SAME'] = 'session'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Set session timeout to 7 days.
app.config['TEMPLATES_AUTO_RELOAD'] = True

Session(app)

# Firebase Admin initialization
cred = credentials.Certificate(r'c:/Users/Lenovo/Downloads/zoo-management-cbf7c-firebase-adminsdk-bbk8s-e6e496a05b.json')  # Update the path
firebase_admin.initialize_app(cred)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Flask-Login initialization
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# User class for Flask-Login integration
class User(UserMixin):
    def __init__(self, email, uid, role=None):
        self.id = uid
        self.email = email
        self.uid = uid
        self.role = role
    
    def get_id(self):
        return self.id     

@login_manager.user_loader
def load_user(user_id):
    try:
        # Retrieve the user from Firebase using the user_id (typically the uid)
        firebase_user = auth.get_user(user_id)
        # Get custom claims or set a default role
        role = firebase_user.custom_claims.get('role', 'guest') if firebase_user.custom_claims else 'guest'
        # Return the User object
        return User(email=firebase_user.email, uid=firebase_user.uid, role=role)
    except Exception as e:
        print(f"Error loading user: {e}")
        return None  # Return None if the user can't be loaded

def assign_role(user_id, role):
    # Assign custom claim (role)
    auth.set_custom_user_claims(user_id, {'role': role})

def check_user_role(uid):
    try:
        user = auth.get_user(uid)  # Firebase function
        claims = user.custom_claims  # Firebase custom claims
        return claims.get('role', 'guest')  # Get role from custom claims
    except Exception as e:
        flash(f"Error fetching user claims: {str(e)}", "danger")
        return 'guest'  # Return a default role in case of failure

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        session['user'] = email
        print(f"Registering user: {email}")

        try:
            user = auth.create_user(email=email, password=password)
            uid = user.uid
            claims = user.custom_claims if hasattr(user, 'custom_claims') else {}

            user_obj = User(email=email, uid=uid, role=claims.get('role', 'guest'))
            login_user(user_obj)  # Log the user in using Flask-Login

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except FirebaseError as e:
            flash(f"Error: {str(e)}", "danger")
    
    return render_template("register.html")





@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()  # Clear previous session data

    if current_user.is_authenticated:  # If the user is already logged in, redirect to home
        return redirect(url_for('home'))

    if request.method == 'POST':
        data = request.get_json()  # Get the JSON data from the request body
        id_token = data.get('id_token')  # Extract id_token from JSON body
        print(f"Logging in user with ID token: {id_token}")

        if not id_token:
            return jsonify({"success": False, "error": "ID token is missing"}), 400

        try:
            # Verify the Firebase ID token and decode the user's information
            decoded_token = auth.verify_id_token(id_token)
            email = decoded_token['email']  # Get the email from the decoded token
            uid = decoded_token['uid']  # Get the Firebase UID
            role = check_user_role(uid)  # Get the user role
            
            # Create the user object
            user_obj = User(email=email, uid=uid, role=role)

            # Log the user in using Flask-Login
            login_user(user_obj)

            flash("Login successful!", "success")
            return jsonify({"success": True, "redirect": url_for('home')}), 200
        except Exception as e:
            flash("Invalid login credentials", "danger")
            print(f"Error verifying token: {e}")
            return jsonify({"success": False, "error": "Invalid token"}), 400

    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()  # Log out the user and clear the session
    return redirect(url_for('home'))

# Firebase Token verification (if using Firebase token from frontend)
logging.basicConfig(level=logging.INFO)

@app.route('/verify_token', methods=['POST'])
def verify_token():
    token = request.json.get('token')  # Get the Firebase ID token from the request
    
    if not token:
        # Handle missing token
        logging.warning("No token provided in the request.")
        return jsonify({'success': False, 'error': 'Token is required'}), 400

    try:
        # Verify the Firebase ID token
        logging.info(f"Received token: {token}")
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']  # Extract user UID from decoded token

        # Store UID and user role in the session
        session['uid'] = uid
        session['user_role'] = check_user_role(uid)  # Ensure this function is defined properly

        logging.info(f"User verified successfully with UID: {uid}")
        logging.debug(f"Session data: {session}")
        return jsonify({'success': True, 'uid': uid})
    
    except auth.InvalidIdTokenError:
        logging.error("Invalid ID token.")
        return jsonify({'success': False, 'error': 'Invalid token'}), 400
    
    except auth.ExpiredIdTokenError:
        logging.error("Expired ID token.")
        return jsonify({'success': False, 'error': 'Token has expired'}), 400
    
    except auth.RevokedIdTokenError:
        logging.error("Revoked ID token.")
        return jsonify({'success': False, 'error': 'Token has been revoked'}), 400

    except Exception as e:
        # Catch any other exceptions
        logging.exception("Unexpected error during token verification.")
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 400

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/set-employee', methods=['POST'])
def set_employee():
    try:
        user_id = request.json.get('user_id')

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        auth.set_custom_user_claims(user_id, {'role': 'employee'})

        return jsonify({"message": f"User {user_id} has been marked as an employee."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/remove-employee', methods=['POST'])
def remove_employee():
    try:
        user_id = request.json.get('user_id')

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        auth.set_custom_user_claims(user_id, {'role': 'user'})

        return jsonify({"message": f"User {user_id} is no longer an employee."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/get-employees', methods=['GET'])
def get_employees():
    try:
        employee_list = []

        users = auth.list_users()

        for user in users.users:
            if user.custom_claims and user.custom_claims.get('role') == 'employee':
                employee_list.append(user.email)  

        return jsonify({"employees": employee_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
zoo_name = "Jungle Haven Zoo"
animals = [
        Mammal("Lea", "Lion", "Female", 5, "Meat"),
        Mammal("Ellie", "Elephant", "Male", 10, "Leaves"),
        Bird("Polly", "Parrot", "Female", 3, "Seeds"),
        Reptile("Coco", "Snake", "Female", 2, "Rats"),
        Bird("Fifi", "Flamingo", "Female", 6, "Fish"),
        Reptile("Oreo", "Lizard", "Male", 2, "Insects")
]

zookeeper = Zookeeper("Sage", "Jungle Haven Zoo")


@app.route("/")
def home():
    if not current_user.is_authenticated:  # Check if the user is logged in
        return redirect(url_for('login'))

    return render_template(
        "home.html", user_role=current_user.role, zoo_name=zoo_name, animals=animals
    )
@app.route("/zookeeper", methods=["GET", "POST"])
@login_required
def zookeeper_page():
    if request.method == "POST":
        if session.get('user_role') != 'employee':
            flash("Access denied. Employees only.", "danger")
            return redirect(url_for('home'))  
        
        if "add_animal" in request.form:
            flash("Animal added successfully!", "success")
        elif "delete_animal" in request.form:
            flash("Animal deleted successfully!", "success")
        elif "edit_animal" in request.form:
            flash("Animal details updated successfully!", "success")
        elif "update_health" in request.form:
            flash("Animal health status updated successfully!", "success")
        elif "simulate_event" in request.form:
            flash("Event simulated successfully!", "success")
    
    zoo_name = "Jungle Haven Zoo"
    return render_template("zookeeper.html", zoo_name=zoo_name, animals=animals)

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

zoo = Zoo("Jungle Haven Zoo")

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

@app.route("/tickets")
def tickets_page():
    tickets = [

    {
        "id": 1,
        "title": "Mammal Adventure",
        "description": "Dive into the fascinating world of mammals! From agile monkeys swinging through trees to majestic lions ruling the savanna, this adventure is perfect for animal lovers of all ages. Learn intriguing facts about these creatures and their habitats, and witness their daily routines up close.",
        "image": "static/images/mammaleticket.png",
        "price": {
            "children": 250,
            "adult": 500,
            "elder": 400
        }
    },
    {
        "id": 2,
        "title": "Group Pass",
        "description": "The ultimate package for families and friends! Enjoy a full day of exploration with access to all zoo attractions. This pass is specially designed to provide a fun, interactive, and budget-friendly experience for groups, ensuring everyone can create lasting memories together.",
        "image": "static/images/group.png",
        "price": {
            "children": 200,
            "adult": 1000,
            "elder": 800
        }
    },
    {
        "id": 3,
        "title": "Bird Watching",
        "description": "Embark on a serene and captivating journey to observe some of the rarest and most vibrant bird species in their natural habitats. With guided assistance, you'll learn to spot and identify various birds while enjoying the tranquil surroundings of our lush aviary. Don't miss out on this amazing opportunity. ",
        "image": "static/images/birdticket.png",
        "price": {
            "children": 150,
            "adult": 300,
            "elder": 250
        }
    },
    {
        "id": 4,
        "title": "VIP Zoo Tour",
        "description": "Experience the zoo like never before with our exclusive VIP Zoo Tour! Go behind the scenes to meet zookeepers, see how animals are cared for, and even feed select animals under expert supervision. This premium package is perfect for animal enthusiasts looking for a deeper connection with the wildlife.",
        "image": "static/images/Mammal/default.jpg",
        "price": {
            "children": 750,
            "adult": 1500,
            "elder": 1200
        }
    }
]
    return render_template("tickets.html", tickets=tickets)


@app.route('/buy_tickets', methods=['GET', 'POST'])
def buy_tickets():
    tickets = {
        1: {"title": "Mammal Adventure", "price": {"children": 250, "adult": 500, "elder": 400}},
        2: {"title": "Group Pass", "price": {"children": 200, "adult": 1000, "elder": 800}},
        3: {"title": "Bird Watching", "price": {"children": 150, "adult": 300, "elder": 250}},
        4: {"title": "VIP Zoo Tour", "price": {"children": 750, "adult": 1500, "elder": 1200}},
    }

    if request.method == 'POST':
        try:
            ticket_id = int(request.form.get("ticket_id", 0))
            ticket_type = request.form.get("ticket_type", "").lower()
            quantity = int(request.form.get("quantity", 0))

            ticket = tickets.get(ticket_id)
            if not ticket:
                flash("Invalid ticket selected.", "error")
                return redirect(url_for("buy_tickets"))

            if ticket_type not in ticket["price"]:
                flash("Invalid ticket type.", "error")
                return redirect(url_for("buy_tickets"))

            if quantity <= 0:
                flash("Quantity must be greater than zero.", "error")
                return redirect(url_for("buy_tickets"))

            total_cost = ticket["price"][ticket_type] * quantity

            flash(
                f"Purchase successful! You bought {quantity} {ticket_type.title()} ticket(s) for "
                f"{ticket['title']} at Ksh{total_cost}.",
                "ticket_message"
            )
            return redirect(url_for("buy_tickets"))

        except ValueError:
            flash("Invalid input. Please provide valid data.", "ticket_error")
            return redirect(url_for("buy_tickets"))

    return render_template('buytickets.html', tickets=tickets)

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

    return render_template("health.html", animals=animals, animal_name=animal_name, health_status=health_status, description="")

@app.route("/clear_health_history", methods=["POST"])
def clear_health_history():
    animal_name = request.form["animal_name"]
    animal = next((a for a in animals if a.name.lower() == animal_name.lower()), None)

    if animal:
        animal.clear_health_history()
        flash(f"Health history of {animal_name} cleared.", "success")
    else:
        flash(f"Animal {animal_name} not found.", "danger")

    return redirect(url_for("health_status"))
 

@app.after_request
def add_cache_control(response):
    response.headers["Cache-Control"] = "no-store"
    return response


if __name__ == '__main__':
    app.run(debug=True)
