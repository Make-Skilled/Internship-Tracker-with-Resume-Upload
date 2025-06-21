# Internship Tracker

A full-stack web application for managing internship opportunities, built with Flask, Tailwind CSS, and Supabase.

## Features

### 👥 User Roles

- **Admin**: Approve/reject organization registrations
- **Organization**: Post internships and manage applications
- **Student**: Browse and apply to internships

### 🔐 Authentication

- **Admin**: Static credentials (username: "admin", password: "admin123")
- **Students & Organizations**: Supabase-based authentication
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
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage (for resume uploads)

## Project Structure

```
Internship Tracker/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── schema.sql            # Supabase database schema
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
- Supabase account
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

### 3. Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run the contents of `schema.sql`
3. Go to Settings > API to get your project URL and anon key
4. Update the Supabase configuration in `app.py`:

```python
SUPABASE_URL = "your-supabase-project-url"
SUPABASE_KEY = "your-supabase-anon-key"
```

### 4. Supabase Storage Setup

1. Go to Storage in your Supabase dashboard
2. Create a new bucket called "resumes"
3. Set the bucket to public (for demo purposes)
4. Configure CORS if needed

### 5. Run the Application

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

## Database Schema

The application uses the following tables:

- **organization**: Organization details and approval status
- **student**: Student account information
- **internship**: Posted internship opportunities
- **application**: Student applications with status tracking

## Security Notes

- Passwords are stored in plain text for demo purposes
- In production, use proper password hashing (bcrypt)
- Enable Row Level Security (RLS) in Supabase for production
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
   - Verify Supabase URL and key
   - Check if tables are created

2. **File Upload Issues**
   - Ensure Supabase Storage bucket exists
   - Check file size limits
   - Verify CORS settings

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