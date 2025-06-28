-- Supabase Database Schema for Internship Tracker
-- Run this in your Supabase SQL editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables with RLS disabled as requested

-- Organization table
CREATE TABLE organization (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    organization_name VARCHAR(200) NOT NULL,
    address TEXT NOT NULL,
    contact_number VARCHAR(20) NOT NULL,
    password VARCHAR(200) NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Student table
CREATE TABLE student (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    password VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Internship table
CREATE TABLE internship (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    stipend VARCHAR(100) NOT NULL,
    duration VARCHAR(100) NOT NULL,
    deadline DATE NOT NULL,
    organization_id INTEGER REFERENCES organization(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Application table
CREATE TABLE application (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES student(id) ON DELETE CASCADE,
    internship_id INTEGER REFERENCES internship(id) ON DELETE CASCADE,
    resume_url VARCHAR(500) NOT NULL,
    cover_letter TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Viewed', 'Selected', 'Rejected')),
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_organization_username ON organization(username);
CREATE INDEX idx_organization_email ON organization(email);
CREATE INDEX idx_organization_approved ON organization(is_approved);

CREATE INDEX idx_student_username ON student(username);
CREATE INDEX idx_student_email ON student(email);

CREATE INDEX idx_internship_organization ON internship(organization_id);
CREATE INDEX idx_internship_deadline ON internship(deadline);

CREATE INDEX idx_application_student ON application(student_id);
CREATE INDEX idx_application_internship ON application(internship_id);
CREATE INDEX idx_application_status ON application(status);

-- Insert sample data for testing (optional)
-- You can uncomment these lines to add sample data

/*
-- Sample organizations
INSERT INTO organization (username, email, organization_name, address, contact_number, password, is_approved) VALUES
('techcorp', 'hr@techcorp.com', 'TechCorp Solutions', '123 Tech Street, Silicon Valley, CA', '+1-555-0123', 'password123', true),
('innovate_labs', 'careers@innovatelabs.com', 'Innovate Labs', '456 Innovation Ave, Austin, TX', '+1-555-0456', 'password123', true);

-- Sample students
INSERT INTO student (username, email, full_name, password) VALUES
('john_doe', 'john.doe@university.edu', 'John Doe', 'password123'),
('jane_smith', 'jane.smith@university.edu', 'Jane Smith', 'password123');

-- Sample internships
INSERT INTO internship (title, description, stipend, duration, deadline, organization_id) VALUES
('Software Development Intern', 'Join our development team to work on cutting-edge web applications using modern technologies.', '$3000/month', '3 months', '2024-06-30', 1),
('Data Science Intern', 'Work with big data and machine learning projects to gain hands-on experience in data analytics.', '$2500/month', '4 months', '2024-07-15', 2);
*/

-- also create the storage bucket named with "resumes"
