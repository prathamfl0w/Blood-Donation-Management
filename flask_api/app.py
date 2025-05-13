from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blood_donation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

db = SQLAlchemy(app)
api = Api(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='user')

    def __init__(self, name, email, blood_group, phone, city, role='user'):
        self.name = name
        self.email = email
        self.blood_group = blood_group
        self.phone = phone
        self.city = city
        self.role = role
        
    def generate_pw(self, password):
        self.password_hash = generate_password_hash(password)

    def check_pw(self, password):
        return check_password_hash(self.password_hash, password)

class BloodDonation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(3), nullable=False)
    amount_ml = db.Column(db.Integer, default=450)
    donation_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='available')
    phone = db.Column(db.String(15))
    city = db.Column(db.String(100))

# Seed data function
def seed_data():
    """Seed the database with initial test data"""
    try:
        # Try to get existing admin user
        admin = User.query.filter_by(email='vikas040805@gmail.com').first()
        
        # Create admin only if doesn't exist
        if not admin:
            admin = User(
                name='Vikash',
                email='vikas040805@gmail.com',
                blood_group='A+',
                phone='6306028152',
                city='prayagraj',
                role='admin'
            )
            admin.generate_pw('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created")
        else:
            print("Admin user already exists")

        # Only add test donations if none exist
        if BloodDonation.query.count() == 0:
            test_donations = [
                {'donor_name': 'John Doe', 'blood_group': 'A+', 'amount_ml': 450, 'status': 'available'},
                {'donor_name': 'Jane Smith', 'blood_group': 'B+', 'amount_ml': 450, 'status': 'available'},
                {'donor_name': 'Bob Wilson', 'blood_group': 'O+', 'amount_ml': 450, 'status': 'available'},
                {'donor_name': 'Alice Brown', 'blood_group': 'AB+', 'amount_ml': 450, 'status': 'available'},
                {'donor_name': 'Tom Clark', 'blood_group': 'A-', 'amount_ml': 450, 'status': 'available'},
                {'donor_name': 'Sarah Davis', 'blood_group': 'B-', 'amount_ml': 450, 'status': 'available'},
                {'donor_name': 'Mike Johnson', 'blood_group': 'O-', 'amount_ml': 450, 'status': 'available'},
                {'donor_name': 'Emily White', 'blood_group': 'AB-', 'amount_ml': 450, 'status': 'available'}
            ]

            for donation in test_donations:
                new_donation = BloodDonation(**donation)
                db.session.add(new_donation)
            
            db.session.commit()
            print("Test donations added successfully!")
        else:
            print("Test donations already exist")
        
    except Exception as e:
        print(f"Error seeding database: {str(e)}")
        db.session.rollback()

# Resources
class RegisterResource(Resource):
    def post(self):
        data = request.get_json()
        
        # Check if user exists
        if User.query.filter_by(email=data.get('email')).first():
            return {'message': 'Email already registered'}, 409

        try:
            user = User(
                name=data.get('name'),
                email=data.get('email'),
                blood_group=data.get('blood_group'),
                phone=data.get('phone'),
                city=data.get('city')
            )
            user.generate_pw(data.get('password'))
            
            db.session.add(user)
            db.session.commit()
            return {'message': 'User registered successfully'}, 201
            
        except Exception as e:
            db.session.rollback()
            return {'message': f'Registration failed: {str(e)}'}, 500

class LoginResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            print(f"Debug - Login attempt for email: {data.get('email')}")  # Debug print
            
            user = User.query.filter_by(email=data.get('email')).first()
            if not user:
                print("Debug - User not found")  # Debug print
                return {'message': 'Invalid credentials'}, 401

            if user.check_pw(data.get('password')):
                access_token = create_access_token(identity=str(user.id))
                print(f"Debug - Login successful for user: {user.name}, role: {user.role}")  # Debug print
                return {
                    'message': 'Login successful',
                    'access_token': access_token,
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'role': user.role
                    }
                }
            
            print("Debug - Invalid password")  # Debug print
            return {'message': 'Invalid credentials'}, 401
            
        except Exception as e:
            print(f"Debug - Login error: {str(e)}")  # Debug print
            return {'message': 'Login failed'}, 500

class BloodStatsResource(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
            stats = {group: 0 for group in blood_groups}
            
            user = db.session.get(User, current_user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}, 404

            # Get Flask donations
            if user.role == 'admin':
                flask_donations = BloodDonation.query.all()
                available_flask_donations = BloodDonation.query.filter_by(status='available').all()
            else:
                flask_donations = BloodDonation.query.filter_by(donor_name=user.name).all()
                available_flask_donations = BloodDonation.query.filter_by(
                    donor_name=user.name,
                    status='available'
                ).all()

            # Count available donations by blood group
            for donation in available_flask_donations:
                if donation.blood_group in stats:
                    stats[donation.blood_group] += 1

            # Format donations for display
            recent_donations = [{
                'donor_name': d.donor_name,
                'blood_group': d.blood_group,
                'amount_ml': d.amount_ml,
                'donation_date': d.donation_date.isoformat(),
                'status': d.status,
                'city': d.city
            } for d in flask_donations]

            # Calculate totals
            total_donations = len(flask_donations)
            available_units = len(available_flask_donations)
            total_ml = sum(d.amount_ml for d in available_flask_donations)

            return {
                'success': True,
                'stats': stats,
                'total_donations': total_donations,
                'available_units': available_units,
                'available_units_ml': total_ml,
                'blood_data': [stats[group] for group in blood_groups],
                'donations': recent_donations,
                'is_admin': user.role == 'admin'
            }

        except Exception as e:
            print(f"Error in blood stats: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'stats': {},
                'total_donations': 0,
                'available_units': 0,
                'available_units_ml': 0,
                'blood_data': [0] * 8,
                'donations': []
            }, 500

class DonationResource(Resource):
    @jwt_required()
    def get(self, donation_id=None):
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user:
            return {'message': 'User not found'}, 404

        if donation_id:
            donation = db.session.get(BloodDonation, donation_id)
            if not donation:
                return {'message': 'Donation not found'}, 404
            
            # Check if user has access to this donation
            if user.role != 'admin' and donation.donor_name != user.name:
                return {'message': 'Access denied'}, 403
                
            return {
                'id': donation.id,
                'donor_name': donation.donor_name,
                'blood_group': donation.blood_group,
                'amount_ml': donation.amount_ml,
                'status': donation.status,
                'donation_date': donation.donation_date.isoformat(),
                'city': donation.city
            }

        # Get all donations or user-specific donations
        if user.role == 'admin':
            donations = BloodDonation.query.all()
        else:
            donations = BloodDonation.query.filter_by(donor_name=user.name).all()

        return [{
            'id': d.id,
            'donor_name': d.donor_name,
            'blood_group': d.blood_group,
            'amount_ml': d.amount_ml,
            'status': d.status,
            'donation_date': d.donation_date.isoformat(),
            'city': d.city
        } for d in donations]

    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            required_fields = ['donor_name', 'blood_group']
            for field in required_fields:
                if field not in data:
                    return {'message': f'Missing required field: {field}'}, 400

            # Validate blood group
            valid_blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
            if data['blood_group'] not in valid_blood_groups:
                return {'message': 'Invalid blood group'}, 400

            # Validate amount
            amount = data.get('amount_ml', 450)
            if not isinstance(amount, (int, float)) or amount <= 0:
                return {'message': 'Invalid amount'}, 400

            new_donation = BloodDonation(
                donor_name=data['donor_name'],
                blood_group=data['blood_group'],
                amount_ml=amount,
                phone=data.get('phone'),
                city=data.get('city'),
                status='available'
            )
            db.session.add(new_donation)
            db.session.commit()
            return {'message': 'Donation recorded successfully', 'id': new_donation.id}, 201

        except Exception as e:
            db.session.rollback()
            return {'message': f'Error creating donation: {str(e)}'}, 500

    @jwt_required()
    def put(self, donation_id):
        donation = BloodDonation.query.get_or_404(donation_id)
        data = request.get_json()
        for key, value in data.items():
            if hasattr(donation, key):
                setattr(donation, key, value)
        db.session.commit()
        return {'message': 'Donation updated successfully'}

    @jwt_required()
    def delete(self, donation_id):
        donation = BloodDonation.query.get_or_404(donation_id)
        db.session.delete(donation)
        db.session.commit()
        return {'message': 'Donation deleted successfully'}

# API Routes
api.add_resource(RegisterResource, '/api/register')
api.add_resource(LoginResource, '/api/login')
api.add_resource(BloodStatsResource, '/api/blood-stats')
api.add_resource(DonationResource, '/api/donations', '/api/donations/<int:donation_id>')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data() 
    app.run(debug=True)

