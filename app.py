import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
import uuid
from supabase_config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_STORAGE_URL, get_supabase_headers

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Helper functions

def hash_password(password):
    # In production, use proper hashing like bcrypt
    return password

def verify_password(password, hashed):
    # In production, use proper verification
    return password == hashed

def upload_to_supabase_storage(file, folder="resumes"):
    """Upload file to Supabase Storage"""
    try:
        filename = f"{folder}/{uuid.uuid4()}_{file.filename}"
        headers = {
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': file.content_type or 'application/octet-stream'
        }
        file.seek(0)
        file_content = file.read()
        upload_url = f"{SUPABASE_URL}/storage/v1/object/{filename}"
        response = requests.post(
            upload_url,
            headers=headers,
            data=file_content
        )
        if response.status_code == 200:
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{filename}"
            return public_url
        else:
            return None
    except Exception as e:
        print(f"Upload error: {e}")
        return None

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/student",
            headers=get_supabase_headers(),
            params={"username": f"eq.{username}"}
        )
        students = resp.json() if resp.status_code == 200 else []
        student = students[0] if students else None

        if student and verify_password(password, student['password']):
            session['user_type'] = 'student'
            session['user_id'] = student['id']
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

        # Check if username exists
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/student",
            headers=get_supabase_headers(),
            params={"username": f"eq.{username}"}
        )
        if resp.json():
            flash('Username already exists', 'error')
            return render_template('student_signup.html')

        # Check if email exists
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/student",
            headers=get_supabase_headers(),
            params={"email": f"eq.{email}"}
        )
        if resp.json():
            flash('Email already exists', 'error')
            return render_template('student_signup.html')

        # Insert new student
        data = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "password": hash_password(password)
        }
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/student",
            headers={**get_supabase_headers(), "Prefer": "return=representation"},
            json=data
        )
        if resp.status_code in (200, 201):
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('student_login'))
        else:
            flash('Error creating account', 'error')
            return render_template('student_signup.html')

    return render_template('student_signup.html')

@app.route('/organization/login', methods=['GET', 'POST'])
def organization_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/organization",
            headers=get_supabase_headers(),
            params={"username": f"eq.{username}"}
        )
        orgs = resp.json() if resp.status_code == 200 else []
        organization = orgs[0] if orgs else None

        if organization and verify_password(password, organization['password']):
            if not organization['is_approved']:
                flash('Your account is pending approval', 'error')
                return render_template('organization_login.html')
            session['user_type'] = 'organization'
            session['user_id'] = organization['id']
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

        # Check if username exists
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/organization",
            headers=get_supabase_headers(),
            params={"username": f"eq.{username}"}
        )
        if resp.json():
            flash('Username already exists', 'error')
            return render_template('organization_signup.html')

        # Check if email exists
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/organization",
            headers=get_supabase_headers(),
            params={"email": f"eq.{email}"}
        )
        if resp.json():
            flash('Email already exists', 'error')
            return render_template('organization_signup.html')

        # Insert new organization
        data = {
            "username": username,
            "email": email,
            "organization_name": organization_name,
            "address": address,
            "contact_number": contact_number,
            "password": hash_password(password),
            "is_approved": False
        }
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/organization",
            headers={**get_supabase_headers(), "Prefer": "return=representation"},
            json=data
        )
        if resp.status_code in (200, 201):
            flash('Account created successfully! Please wait for admin approval.', 'success')
            return redirect(url_for('organization_login'))
        else:
            flash('Error creating account', 'error')
            return render_template('organization_signup.html')

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

    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/organization",
        headers=get_supabase_headers(),
        params={"is_approved": "eq.false"}
    )
    pending_organizations = resp.json() if resp.status_code == 200 else []

    for org in pending_organizations:
        if isinstance(org.get('created_at'), str):
            try:
                org['created_at'] = datetime.fromisoformat(org['created_at'].replace('Z', '+00:00'))
            except Exception:
                org['created_at'] = None

    return render_template('admin_dashboard.html', organizations=pending_organizations)

@app.route('/admin/approve/<int:org_id>')
def approve_organization(org_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('admin_login'))

    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/organization?id=eq.{org_id}",
        headers={**get_supabase_headers(), "Prefer": "return=representation"},
        json={"is_approved": True}
    )
    if resp.status_code in (200, 204):
        flash('Organization approved successfully', 'success')
    else:
        flash('Failed to approve organization', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/<int:org_id>')
def reject_organization(org_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('admin_login'))
    
    organization = Organization.query.get_or_404(org_id)
    db.session.delete(organization)
    db.session.commit()
    flash('Organization rejected and deleted', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/student/dashboard')
def student_dashboard():
    if session.get('user_type') != 'student':
        return redirect(url_for('student_login'))

    from datetime import datetime
    today = datetime.now().date().isoformat()
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/internship",
        headers=get_supabase_headers(),
        params={
            "deadline": f"gte.{today}",
            "select": "*,organization:organization_id(*)"
        }
    )
    internships = resp.json() if resp.status_code == 200 else []

    for internship in internships:
        if isinstance(internship.get('deadline'), str):
            try:
                internship['deadline'] = datetime.fromisoformat(internship['deadline']).date()
            except Exception:
                internship['deadline'] = None

    return render_template('student_dashboard.html', internships=internships)

@app.route('/organization/dashboard')
def organization_dashboard():
    if session.get('user_type') != 'organization':
        return redirect(url_for('organization_login'))

    org_id = session['user_id']
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/internship",
        headers=get_supabase_headers(),
        params={"organization_id": f"eq.{org_id}"}
    )
    internships = resp.json() if resp.status_code == 200 else []

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
        deadline = request.form['deadline']  # should be in 'YYYY-MM-DD' format

        data = {
            "title": title,
            "description": description,
            "stipend": stipend,
            "duration": duration,
            "deadline": deadline,
            "organization_id": session['user_id']
        }
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/internship",
            headers={**get_supabase_headers(), "Prefer": "return=representation"},
            json=data
        )
        if resp.status_code in (200, 201):
            flash('Internship posted successfully!', 'success')
            return redirect(url_for('organization_dashboard'))
        else:
            flash('Error posting internship', 'error')
            return render_template('post_internship.html')

    return render_template('post_internship.html')

@app.route('/internship/apply/<int:internship_id>', methods=['GET', 'POST'])
def apply_internship(internship_id):
    if session.get('user_type') != 'student':
        return redirect(url_for('student_login'))

    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/internship",
        headers=get_supabase_headers(),
        params={"id": f"eq.{internship_id}"}
    )
    internships = resp.json() if resp.status_code == 200 else []
    internship = internships[0] if internships else None

    if not internship:
        flash('Internship not found', 'error')
        return redirect(url_for('student_dashboard'))

    # Fetch organization details and attach to internship
    org_id = internship.get('organization_id')
    if org_id:
        org_resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/organization",
            headers=get_supabase_headers(),
            params={"id": f"eq.{org_id}"}
        )
        orgs = org_resp.json() if org_resp.status_code == 200 else []
        internship['organization'] = orgs[0] if orgs else None

    if request.method == 'POST':
        cover_letter = request.form['cover_letter']
        resume = request.files['resume']

        if resume:
            resume_url = upload_to_supabase_storage(resume)
            if resume_url:
                data = {
                    "student_id": session['user_id'],
                    "internship_id": internship_id,
                    "resume_url": resume_url,
                    "cover_letter": cover_letter
                }
                resp = requests.post(
                    f"{SUPABASE_URL}/rest/v1/application",
                    headers={**get_supabase_headers(), "Prefer": "return=representation"},
                    json=data
                )
                if resp.status_code in (200, 201):
                    flash('Application submitted successfully!', 'success')
                    return redirect(url_for('student_dashboard'))
                else:
                    flash('Error submitting application', 'error')
            else:
                flash('Error uploading resume', 'error')
        else:
            flash('Please upload a resume', 'error')

    return render_template('apply_internship.html', internship=internship)

@app.route('/organization/applications/<int:internship_id>')
def view_applications(internship_id):
    if session.get('user_type') != 'organization':
        return redirect(url_for('organization_login'))

    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/application",
        headers=get_supabase_headers(),
        params={
            "internship_id": f"eq.{internship_id}",
            "select": "*,internship:internship_id(*),student:student_id(*)"
        }
    )
    applications = resp.json() if resp.status_code == 200 else []

    from datetime import datetime
    for app in applications:
        if isinstance(app.get('applied_at'), str):
            try:
                app['applied_at'] = datetime.fromisoformat(app['applied_at'].replace('Z', '+00:00'))
            except Exception:
                app['applied_at'] = None

    return render_template('view_applications.html', applications=applications)

@app.route('/application/update_status/<int:application_id>/<status>')
def update_application_status(application_id, status):
    if session.get('user_type') != 'organization':
        return redirect(url_for('organization_login'))

    # Fetch the application to get the internship_id for redirect
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/application",
        headers=get_supabase_headers(),
        params={"id": f"eq.{application_id}"}
    )
    applications = resp.json() if resp.status_code == 200 else []
    application = applications[0] if applications else None

    if not application:
        flash('Application not found', 'error')
        return redirect(url_for('organization_dashboard'))

    # Update the status
    patch_resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/application?id=eq.{application_id}",
        headers={**get_supabase_headers(), "Prefer": "return=representation"},
        json={"status": status}
    )

    if patch_resp.status_code in (200, 204):
        flash(f'Application status updated to {status}', 'success')
    else:
        flash('Failed to update application status', 'error')

    return redirect(url_for('view_applications', internship_id=application['internship_id']))

@app.route('/student/applications')
def student_applications():
    if session.get('user_type') != 'student':
        return redirect(url_for('student_login'))

    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/application",
        headers=get_supabase_headers(),
        params={
            "student_id": f"eq.{session['user_id']}",
            "select": "*,internship:internship_id(*,organization:organization_id(*))"
        }
    )
    applications = resp.json() if resp.status_code == 200 else []

    from datetime import datetime
    for app in applications:
        if isinstance(app.get('applied_at'), str):
            try:
                app['applied_at'] = datetime.fromisoformat(app['applied_at'].replace('Z', '+00:00'))
            except Exception:
                app['applied_at'] = None

    return render_template('student_applications.html', applications=applications)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True) 