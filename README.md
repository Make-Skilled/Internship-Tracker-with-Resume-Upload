# Internship Tracker

A full-stack web application for managing internship opportunities, built with Flask, Tailwind CSS, and MongoDB.

## Features

### 👥 User Roles

- **Admin**: Approve/reject organization registrations
- **Organization**: Post internships and manage applications
- **Student**: Browse and apply to internships

### 🔐 Authentication

- **Admin**: Static credentials (username: "admin", password: "admin123")
- **Students & Organizations**: Local authentication
- **Organizations**: Require admin approval before login

### 🚀 Core Functionality

#### Admin Features
- View pending organization signup requests
- Approve or reject organizations
- Access via hidden login at bottom-right corner

#### Organization Features
- Sign up with organization details (name, email, address, contact)
- Post internships with title, description, stipend, duration, deadline
- View and manage student applications
- Update application status (Viewed, Selected, Rejected)

#### Student Features
- Sign up and login without approval
- Browse available internships (filtered by deadline)
- Apply with cover letter and resume upload
- Track application status

## Tech Stack

- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Backend**: Python Flask
- **Database**: MongoDB Atlas (with GridFS for file storage)
- **Storage**: MongoDB GridFS (for resume uploads)

## Project Structure

```
Internship Tracker/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── templates/            # HTML templates
    ├── base.html         # Base template with navigation
    ├── home.html         # Landing page with login options
    ├── student_login.html
    ├── student_signup.html
    ├── organization_login.html
    ├── organization_signup.html
    ├── admin_login.html
    ├── admin_dashboard.html
    ├── student_dashboard.html
    ├── organization_dashboard.html
    ├── post_internship.html
    ├── apply_internship.html
    ├── view_applications.html
    └── student_applications.html
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account
- Git

### 2. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd Internship Tracker

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. MongoDB Setup

1. Create a new cluster at [mongodb.com](https://www.mongodb.com)
2. Get your connection string (URI)
3. Update the MongoDB configuration in `app.py`:

```python
MONGO_URI = "your-mongodb-connection-uri"
```

### 4. GridFS Setup

No additional setup is required. The application will automatically use GridFS to store and retrieve resumes in MongoDB.

### 4. Run the Application

```bash
# Set Flask environment variables
set FLASK_APP=app.py
set FLASK_ENV=development

# Run the application
python app.py
```

The application will be available at `http://localhost:5000`

## Usage Guide

### Admin Access
- Click the hidden "Admin" button at the bottom-right corner of the home page
- Login with username: "admin" and password: "admin123"
- Approve or reject pending organization registrations

### Organization Registration
1. Click "Organization Signup" on the home page
2. Fill in organization details
3. Wait for admin approval
4. Login and start posting internships

### Student Registration
1. Click "Student Signup" on the home page
2. Create account (no approval required)
3. Browse and apply to internships

### Posting Internships
1. Login as an approved organization
2. Click "Post New Internship"
3. Fill in internship details
4. View and manage applications

### Applying to Internships
1. Login as a student
2. Browse available internships
3. Click "Apply Now"
4. Upload resume and write cover letter
5. Track application status

## Database Schema & File Storage

The application uses the following collections:

- **organizations**: Organization details and approval status
- **students**: Student account information
- **internships**: Posted internship opportunities
- **applications**: Student applications with status tracking (each application stores a reference to a resume file in GridFS)

Resume files are stored in MongoDB using GridFS. When a student applies, their resume is uploaded directly to the database. Organizations can download resumes securely via the application interface.

## Security Notes

- Passwords are stored in plain text for demo purposes
- In production, use proper password hashing (bcrypt)
- Implement proper file upload validation
- Add CSRF protection

## Customization

### Styling
- Modify Tailwind CSS classes in templates
- Update color scheme in `base.html`
- Add custom CSS in static folder

### Features
- Add email notifications
- Implement search and filtering
- Add file upload size validation
- Create admin user management
- Add internship categories

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify MongoDB URI
   - Check if collections are created

2. **File Upload Issues**
   - Ensure your MongoDB Atlas cluster has sufficient storage
   - Check file size limits (default max is 16MB per file in GridFS)

3. **Template Errors**
   - Check if all template files are in the templates folder
   - Verify Jinja2 syntax

## License

This project is for educational purposes. Feel free to modify and use as needed.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please create an issue in the repository. 