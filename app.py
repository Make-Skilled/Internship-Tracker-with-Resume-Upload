import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import uuid
from gridfs import GridFS

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecret')

# MongoDB Atlas connection
MONGO_URI = 'mongodb+srv://gnana1313:Gnana1212@dbs.8wngtib.mongodb.net/?retryWrites=true&w=majority&appName=DBs'
client = MongoClient(MONGO_URI)
db = client['internship_tracker']
gfs = GridFS(db)

# Helper functions

def hash_password(password):
    # In production, use proper hashing like bcrypt
    return password

def verify_password(password, hashed):
    # In production, use proper verification
    return password == hashed

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        student = db.students.find_one({'username': username})
        if student and verify_password(password, student['password']):
            session['user_type'] = 'student'
            session['user_id'] = str(student['_id'])
            session['username'] = student['username']
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('student_login.html')

@app.route('/student/signup', methods=['GET', 'POST'])
def student_signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        full_name = request.form['full_name']
        password = request.form['password']
        if db.students.find_one({'username': username}):
            flash('Username already exists', 'error')
            return render_template('student_signup.html')
        if db.students.find_one({'email': email}):
            flash('Email already exists', 'error')
            return render_template('student_signup.html')
        db.students.insert_one({
            'username': username,
            'email': email,
            'full_name': full_name,
            'password': hash_password(password)
        })
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('student_login'))
    return render_template('student_signup.html')

@app.route('/organization/login', methods=['GET', 'POST'])
def organization_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        organization = db.organizations.find_one({'username': username})
        if organization and verify_password(password, organization['password']):
            if not organization.get('is_approved', False):
                flash('Your account is pending approval', 'error')
                return render_template('organization_login.html')
            session['user_type'] = 'organization'
            session['user_id'] = str(organization['_id'])
            session['username'] = organization['username']
            return redirect(url_for('organization_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('organization_login.html')

@app.route('/organization/signup', methods=['GET', 'POST'])
def organization_signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        organization_name = request.form['organization_name']
        address = request.form['address']
        contact_number = request.form['contact_number']
        password = request.form['password']
        if db.organizations.find_one({'username': username}):
            flash('Username already exists', 'error')
            return render_template('organization_signup.html')
        if db.organizations.find_one({'email': email}):
            flash('Email already exists', 'error')
            return render_template('organization_signup.html')
        db.organizations.insert_one({
            'username': username,
            'email': email,
            'organization_name': organization_name,
            'address': address,
            'contact_number': contact_number,
            'password': hash_password(password),
            'is_approved': False,
            'created_at': datetime.utcnow()
        })
        flash('Account created successfully! Please wait for admin approval.', 'success')
        return redirect(url_for('organization_login'))
    return render_template('organization_signup.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['user_type'] = 'admin'
            session['username'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('user_type') != 'admin':
        return redirect(url_for('admin_login'))
    pending_organizations = list(db.organizations.find({'is_approved': False}))
    for org in pending_organizations:
        if 'created_at' not in org or not org['created_at']:
            org['created_at'] = None
        elif isinstance(org['created_at'], str):
            try:
                org['created_at'] = datetime.fromisoformat(org['created_at'])
            except Exception:
                org['created_at'] = None
    return render_template('admin_dashboard.html', organizations=pending_organizations)

@app.route('/admin/approve/<org_id>')
def approve_organization(org_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('admin_login'))
    result = db.organizations.update_one({'_id': ObjectId(org_id)}, {'$set': {'is_approved': True}})
    if result.modified_count:
        flash('Organization approved successfully', 'success')
    else:
        flash('Failed to approve organization', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/<org_id>')
def reject_organization(org_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('admin_login'))
    result = db.organizations.delete_one({'_id': ObjectId(org_id)})
    if result.deleted_count:
        flash('Organization rejected and deleted', 'success')
    else:
        flash('Failed to delete organization', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/student/dashboard')
def student_dashboard():
    if session.get('user_type') != 'student':
        return redirect(url_for('student_login'))
    today = datetime.now().date().isoformat()
    internships = list(db.internships.find({'deadline': {'$gte': today}}))
    for internship in internships:
        org = db.organizations.find_one({'_id': ObjectId(internship['organization_id'])})
        internship['organization'] = org
        if isinstance(internship.get('deadline'), str):
            try:
                internship['deadline'] = datetime.fromisoformat(internship['deadline']).date()
            except Exception:
                internship['deadline'] = None
    # Get all applications for this student
    applications = list(db.applications.find({'student_id': session['user_id']}))
    applied_internship_ids = {str(app['internship_id']) for app in applications}
    return render_template(
        'student_dashboard.html',
        internships=internships,
        applied_internship_ids=applied_internship_ids
    )

@app.route('/organization/dashboard')
def organization_dashboard():
    if session.get('user_type') != 'organization':
        return redirect(url_for('organization_login'))
    org_id = session['user_id']
    internships = list(db.internships.find({'organization_id': org_id}))
    for internship in internships:
        if isinstance(internship.get('deadline'), str):
            try:
                internship['deadline'] = datetime.fromisoformat(internship['deadline']).date()
            except Exception:
                internship['deadline'] = None
    return render_template('organization_dashboard.html', internships=internships)

@app.route('/internship/post', methods=['GET', 'POST'])
def post_internship():
    if session.get('user_type') != 'organization':
        return redirect(url_for('organization_login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        stipend = request.form['stipend']
        duration = request.form['duration']
        deadline = request.form['deadline']
        data = {
            'title': title,
            'description': description,
            'stipend': stipend,
            'duration': duration,
            'deadline': deadline,
            'organization_id': session['user_id']
        }
        db.internships.insert_one(data)
        flash('Internship posted successfully!', 'success')
        return redirect(url_for('organization_dashboard'))
    return render_template('post_internship.html')

@app.route('/internship/apply/<internship_id>', methods=['GET', 'POST'])
def apply_internship(internship_id):
    if session.get('user_type') != 'student':
        return redirect(url_for('student_login'))
    internship = db.internships.find_one({'_id': ObjectId(internship_id)})
    if not internship:
        flash('Internship not found', 'error')
        return redirect(url_for('student_dashboard'))
    org = db.organizations.find_one({'_id': ObjectId(internship['organization_id'])})
    internship['organization'] = org
    if request.method == 'POST':
        cover_letter = request.form['cover_letter']
        resume = request.files['resume']
        resume_file_id = None
        if resume:
            # Save resume to MongoDB GridFS
            resume_file_id = gfs.put(resume, filename=resume.filename, content_type=resume.content_type)
        if resume_file_id:
            db.applications.insert_one({
                'student_id': session['user_id'],
                'internship_id': internship_id,
                'resume_file_id': str(resume_file_id),
                'cover_letter': cover_letter,
                'applied_at': datetime.utcnow().isoformat(),
                'status': 'pending'
            })
            flash('Application submitted successfully!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Please upload a resume', 'error')
    return render_template('apply_internship.html', internship=internship)

@app.route('/resume/<file_id>')
def download_resume(file_id):
    try:
        file_obj = gfs.get(ObjectId(file_id))
        return send_file(file_obj, download_name=file_obj.filename, mimetype=file_obj.content_type, as_attachment=True)
    except Exception:
        flash('Resume not found', 'error')
        return redirect(url_for('home'))

@app.route('/organization/applications/<internship_id>')
def view_applications(internship_id):
    if session.get('user_type') != 'organization':
        return redirect(url_for('organization_login'))
    applications = list(db.applications.find({'internship_id': internship_id}))
    for app in applications:
        app['student'] = db.students.find_one({'_id': ObjectId(app['student_id'])})
        app['internship'] = db.internships.find_one({'_id': ObjectId(app['internship_id'])})
        if 'resume_file_id' in app:
            app['resume_url'] = url_for('download_resume', file_id=app['resume_file_id'])
        if isinstance(app.get('applied_at'), str):
            try:
                app['applied_at'] = datetime.fromisoformat(app['applied_at'])
            except Exception:
                app['applied_at'] = None
    return render_template('view_applications.html', applications=applications)

@app.route('/application/update_status/<application_id>/<status>')
def update_application_status(application_id, status):
    if session.get('user_type') != 'organization':
        return redirect(url_for('organization_login'))
    allowed_statuses = ['pending', 'viewed', 'shortlisted', 'rejected', 'accepted']
    status = status.lower()
    if status not in allowed_statuses:
        flash('Invalid status', 'error')
        application = db.applications.find_one({'_id': ObjectId(application_id)})
        if application:
            return redirect(url_for('view_applications', internship_id=application['internship_id']))
        else:
            return redirect(url_for('organization_dashboard'))
    application = db.applications.find_one({'_id': ObjectId(application_id)})
    if not application:
        flash('Application not found', 'error')
        return redirect(url_for('organization_dashboard'))
    db.applications.update_one({'_id': ObjectId(application_id)}, {'$set': {'status': status}})
    flash(f'Application status updated to {status.capitalize()}', 'success')
    return redirect(url_for('view_applications', internship_id=application['internship_id']))

@app.route('/student/applications')
def student_applications():
    if session.get('user_type') != 'student':
        return redirect(url_for('student_login'))
    applications = list(db.applications.find({'student_id': session['user_id']}))
    for app in applications:
        app['internship'] = db.internships.find_one({'_id': ObjectId(app['internship_id'])})
        if 'resume_file_id' in app:
            app['resume_url'] = url_for('download_resume', file_id=app['resume_file_id'])
        if app['internship']:
            app['internship']['organization'] = db.organizations.find_one({'_id': ObjectId(app['internship']['organization_id'])})
        if isinstance(app.get('applied_at'), str):
            try:
                app['applied_at'] = datetime.fromisoformat(app['applied_at'])
            except Exception:
                app['applied_at'] = None
    return render_template('student_applications.html', applications=applications)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True) 
