from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///traffic.db'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)

# ---------------- Database Models ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    role = db.Column(db.String(10))  # admin or police

class Vehicle(db.Model):
    vehicle_no = db.Column(db.String(20), primary_key=True)
    owner_name = db.Column(db.String(100))
    license_no = db.Column(db.String(50))
    phone = db.Column(db.String(15))

class Violation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    violation_type = db.Column(db.String(100))
    fine_amount = db.Column(db.Integer)

class Challan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_no = db.Column(db.String(20), db.ForeignKey('vehicle.vehicle_no'))
    violation_id = db.Column(db.Integer, db.ForeignKey('violation.id'))
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(100))
    status = db.Column(db.String(10), default="Pending")

# ---------------- Routes ----------------
@app.route('/')
def home():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
    if user:
        return redirect(url_for('dashboard'))
    return "Invalid login"

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/issue_challan', methods=['GET', 'POST'])
def issue_challan():
    vehicles = Vehicle.query.all()
    violations = Violation.query.all()
    if request.method == "POST":
        challan = Challan(
            vehicle_no=request.form['vehicle_no'],
            violation_id=request.form['violation_id'],
            location=request.form['location']
        )
        db.session.add(challan)
        db.session.commit()
        return redirect(url_for('view_challans'))
    return render_template("issue_challan.html", vehicles=vehicles, violations=violations)

@app.route('/view_challans')
def view_challans():
    challans = Challan.query.all()
    return render_template("view_challans.html", challans=challans)

@app.route('/reports')
def reports():
    results = db.session.query(
        Violation.violation_type, 
        func.count(Challan.id)
    ).join(Challan, Violation.id == Challan.violation_id).group_by(Violation.violation_type).all()
    return render_template("reports.html", results=results)

# ---------------- Main ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Insert sample data if not exists
        if not User.query.first():
            db.session.add(User(username="admin", password="admin", role="admin"))
            db.session.add(Vehicle(vehicle_no="KA01AB1234", owner_name="Ravi Kumar", license_no="DL12345", phone="9876543210"))
            db.session.add(Violation(violation_type="No Helmet", fine_amount=500))
            db.session.add(Violation(violation_type="Signal Jump", fine_amount=1000))
            db.session.commit()

    app.run(debug=True)
