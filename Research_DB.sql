-- =====================================================
-- FINAL CORRECTED MYSQL RESEARCH SCHEMA
-- Topic: SQL Query Performance Prediction
-- Domain: University Management System
-- DB Name: researchdb
-- MySQL 8.x Compatible
-- =====================================================

DROP DATABASE IF EXISTS researchdb;
CREATE DATABASE researchdb;
USE researchdb;

-- =====================================================
-- 1. DEPARTMENTS
-- =====================================================

CREATE TABLE departments (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_code VARCHAR(10) NOT NULL UNIQUE,
    dept_name VARCHAR(100) NOT NULL,
    office_location VARCHAR(100),
    budget DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =====================================================
-- 2. STUDENTS
-- =====================================================

CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    university_no VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    gender ENUM('Male','Female'),
    birth_date DATE,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    city VARCHAR(50),
    country VARCHAR(50),
    enrollment_year YEAR,
    gpa DECIMAL(3,2),
    status ENUM('Active','Graduated','Suspended') DEFAULT 'Active',
    dept_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_students_department
        FOREIGN KEY (dept_id)
        REFERENCES departments(dept_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- =====================================================
-- 3. INSTRUCTORS
-- =====================================================

CREATE TABLE instructors (
    instructor_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_no VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    rank_title ENUM(
        'Lecturer',
        'Assistant Professor',
        'Associate Professor',
        'Professor'
    ),
    salary DECIMAL(10,2),
    hire_date DATE,
    dept_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_instructors_department
        FOREIGN KEY (dept_id)
        REFERENCES departments(dept_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- =====================================================
-- 4. COURSES
-- =====================================================

CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    course_title VARCHAR(120),
    credit_hours INT,
    level_no INT,
    dept_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_courses_department
        FOREIGN KEY (dept_id)
        REFERENCES departments(dept_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- =====================================================
-- 5. CLASSROOMS
-- =====================================================

CREATE TABLE classrooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    building_name VARCHAR(50),
    room_no VARCHAR(20),
    capacity INT,
    room_type ENUM('Lecture Hall','Lab','Classroom')
) ENGINE=InnoDB;

-- =====================================================
-- 6. COURSE_SECTIONS
-- =====================================================

CREATE TABLE course_sections (
    section_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT,
    instructor_id INT,
    room_id INT,
    semester ENUM('Fall','Spring','Summer'),
    academic_year YEAR,
    section_no VARCHAR(10),
    max_students INT,
    schedule_days VARCHAR(20),
    schedule_time VARCHAR(30),

    CONSTRAINT fk_sections_course
        FOREIGN KEY (course_id)
        REFERENCES courses(course_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_sections_instructor
        FOREIGN KEY (instructor_id)
        REFERENCES instructors(instructor_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_sections_room
        FOREIGN KEY (room_id)
        REFERENCES classrooms(room_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- =====================================================
-- 7. ENROLLMENTS
-- =====================================================

CREATE TABLE enrollments (
    enroll_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    section_id INT,
    enroll_date DATE,
    grade ENUM('A','B','C','D','F','I','W'),
    attendance_percent DECIMAL(5,2),
    status ENUM('Enrolled','Dropped','Completed') DEFAULT 'Enrolled',

    CONSTRAINT fk_enrollments_student
        FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_enrollments_section
        FOREIGN KEY (section_id)
        REFERENCES course_sections(section_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- =====================================================
-- 8. PAYMENTS
-- =====================================================

CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    semester ENUM('Fall','Spring','Summer'),
    academic_year YEAR,
    amount DECIMAL(10,2),
    payment_method ENUM('Cash','Card','Transfer'),
    payment_status ENUM('Paid','Pending','Partial'),
    payment_date DATE,

    CONSTRAINT fk_payments_student
        FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- =====================================================
-- PERFORMANCE INDEXES
-- =====================================================

CREATE INDEX idx_students_dept        ON students(dept_id);
CREATE INDEX idx_students_gpa         ON students(gpa);
CREATE INDEX idx_students_city        ON students(city);
CREATE INDEX idx_students_status      ON students(status);

CREATE INDEX idx_courses_dept         ON courses(dept_id);

CREATE INDEX idx_sections_course      ON course_sections(course_id);
CREATE INDEX idx_sections_instructor  ON course_sections(instructor_id);
CREATE INDEX idx_sections_semester    ON course_sections(semester, academic_year);

CREATE INDEX idx_enroll_student       ON enrollments(student_id);
CREATE INDEX idx_enroll_section       ON enrollments(section_id);
CREATE INDEX idx_enroll_grade         ON enrollments(grade);
CREATE INDEX idx_enroll_status        ON enrollments(status);

CREATE INDEX idx_payments_student     ON payments(student_id);
CREATE INDEX idx_payments_status      ON payments(payment_status);

-- =====================================================
-- OPTIONAL SEED DATA (Helpful for testing)
-- =====================================================

INSERT INTO departments
(dept_code, dept_name, office_location, budget)
VALUES
('CPE','Computer Engineering','B1-201',250000),
('CS','Computer Science','B1-205',300000),
('EE','Electrical Engineering','B2-101',280000),
('ME','Mechanical Engineering','B3-110',220000),
('BUS','Business Administration','A1-120',350000);

INSERT INTO classrooms
(building_name, room_no, capacity, room_type)
VALUES
('B1','101',40,'Classroom'),
('B1','102',35,'Classroom'),
('B2','Lab1',25,'Lab'),
('B2','HallA',120,'Lecture Hall'),
('A1','301',50,'Classroom');

-- =====================================================
-- VERIFY TABLES
-- =====================================================

SHOW TABLES;