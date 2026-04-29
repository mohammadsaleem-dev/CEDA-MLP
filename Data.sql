USE researchdb;

-- =====================================================
-- FINAL OPTIMIZED DATA GENERATION SCRIPT
-- FAST + SAFE + NO TIMEOUTS
-- FOR IEEE RESEARCH PROJECT
--
-- Target Rows:
-- departments      = 10
-- students         = 10,000
-- instructors      = 100
-- courses          = 300
-- classrooms       = 5
-- course_sections  = 600
-- enrollments      = 50,000
-- =====================================================

-- =====================================================
-- STEP 1: CLEAN TABLES
-- =====================================================

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE enrollments;
TRUNCATE TABLE payments;
TRUNCATE TABLE course_sections;
TRUNCATE TABLE classrooms;
TRUNCATE TABLE students;
TRUNCATE TABLE instructors;
TRUNCATE TABLE courses;
TRUNCATE TABLE departments;

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- STEP 2: DEPARTMENTS
-- =====================================================

INSERT INTO departments (dept_code, dept_name, office_location, budget) VALUES
('CPE','Computer Engineering','B1-201',250000),
('CS','Computer Science','B1-205',300000),
('EE','Electrical Engineering','B2-101',280000),
('ME','Mechanical Engineering','B3-110',220000),
('CE','Civil Engineering','B4-101',210000),
('IE','Industrial Engineering','B4-201',215000),
('BUS','Business Administration','A1-120',350000),
('ACC','Accounting','A1-220',270000),
('MED','Medicine','M1-100',500000),
('LAW','Law','L1-010',190000);

-- =====================================================
-- STEP 3: CLASSROOMS
-- =====================================================

INSERT INTO classrooms (building_name, room_no, capacity, room_type) VALUES
('B1','101',40,'Classroom'),
('B1','102',35,'Classroom'),
('B2','Lab1',25,'Lab'),
('B2','HallA',120,'Lecture Hall'),
('A1','301',50,'Classroom');

-- =====================================================
-- STEP 4: STUDENTS (10,000)
-- =====================================================

DROP PROCEDURE IF EXISTS generate_students;
DELIMITER $$

CREATE PROCEDURE generate_students()
BEGIN
    DECLARE i INT DEFAULT 1;

    START TRANSACTION;

    WHILE i <= 10000 DO

        INSERT INTO students
        (
            university_no, first_name, last_name, gender,
            birth_date, email, phone, city, country,
            enrollment_year, gpa, status, dept_id
        )
        VALUES
        (
            CONCAT('202',LPAD(i,6,'0')),
            CONCAT('Student',i),
            CONCAT('Last',i),
            IF(i % 2 = 0,'Male','Female'),
            DATE_ADD('1998-01-01', INTERVAL FLOOR(RAND()*2500) DAY),
            CONCAT('student',i,'@univ.edu'),
            CONCAT('079',LPAD(FLOOR(RAND()*9999999),7,'0')),
            ELT(1+FLOOR(RAND()*6),
                'Amman','Zarqa','Irbid','Aqaba','Madaba','Salt'),
            'Jordan',
            2020 + FLOOR(RAND()*6),
            ROUND(2 + RAND()*2,2),
            ELT(1+FLOOR(RAND()*3),
                'Active','Graduated','Suspended'),
            1 + FLOOR(RAND()*10)
        );

        SET i = i + 1;

    END WHILE;

    COMMIT;
END$$
DELIMITER ;

CALL generate_students();
DROP PROCEDURE generate_students;

-- =====================================================
-- STEP 5: INSTRUCTORS (100)
-- =====================================================

INSERT INTO instructors
(employee_no,first_name,last_name,email,rank_title,salary,hire_date,dept_id)
SELECT
CONCAT('EMP',LPAD(n,4,'0')),
CONCAT('Prof',n),
CONCAT('Last',n),
CONCAT('prof',n,'@univ.edu'),
ELT(1+FLOOR(RAND()*4),
'Lecturer','Assistant Professor','Associate Professor','Professor'),
ROUND(900 + RAND()*2500,2),
DATE_ADD('2010-01-01', INTERVAL FLOOR(RAND()*5000) DAY),
1 + FLOOR(RAND()*10)
FROM
(
SELECT 1 n UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10
UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20
UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25
UNION SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29 UNION SELECT 30
UNION SELECT 31 UNION SELECT 32 UNION SELECT 33 UNION SELECT 34 UNION SELECT 35
UNION SELECT 36 UNION SELECT 37 UNION SELECT 38 UNION SELECT 39 UNION SELECT 40
UNION SELECT 41 UNION SELECT 42 UNION SELECT 43 UNION SELECT 44 UNION SELECT 45
UNION SELECT 46 UNION SELECT 47 UNION SELECT 48 UNION SELECT 49 UNION SELECT 50
UNION SELECT 51 UNION SELECT 52 UNION SELECT 53 UNION SELECT 54 UNION SELECT 55
UNION SELECT 56 UNION SELECT 57 UNION SELECT 58 UNION SELECT 59 UNION SELECT 60
UNION SELECT 61 UNION SELECT 62 UNION SELECT 63 UNION SELECT 64 UNION SELECT 65
UNION SELECT 66 UNION SELECT 67 UNION SELECT 68 UNION SELECT 69 UNION SELECT 70
UNION SELECT 71 UNION SELECT 72 UNION SELECT 73 UNION SELECT 74 UNION SELECT 75
UNION SELECT 76 UNION SELECT 77 UNION SELECT 78 UNION SELECT 79 UNION SELECT 80
UNION SELECT 81 UNION SELECT 82 UNION SELECT 83 UNION SELECT 84 UNION SELECT 85
UNION SELECT 86 UNION SELECT 87 UNION SELECT 88 UNION SELECT 89 UNION SELECT 90
UNION SELECT 91 UNION SELECT 92 UNION SELECT 93 UNION SELECT 94 UNION SELECT 95
UNION SELECT 96 UNION SELECT 97 UNION SELECT 98 UNION SELECT 99 UNION SELECT 100
) x;

-- =====================================================
-- STEP 6: COURSES (300)
-- =====================================================

DROP PROCEDURE IF EXISTS generate_courses;
DELIMITER $$

CREATE PROCEDURE generate_courses()
BEGIN
    DECLARE i INT DEFAULT 1;

    START TRANSACTION;

    WHILE i <= 300 DO

        INSERT INTO courses
        (course_code,course_title,credit_hours,level_no,dept_id)
        VALUES
        (
            CONCAT('CRS',LPAD(i,4,'0')),
            CONCAT('Course Title ',i),
            ELT(1+FLOOR(RAND()*4),3,3,4,2),
            ELT(1+FLOOR(RAND()*4),1,2,3,4),
            1 + FLOOR(RAND()*10)
        );

        SET i = i + 1;

    END WHILE;

    COMMIT;
END$$
DELIMITER ;

CALL generate_courses();
DROP PROCEDURE generate_courses;

-- =====================================================
-- STEP 7: COURSE SECTIONS (600)
-- =====================================================

DROP PROCEDURE IF EXISTS generate_sections;
DELIMITER $$

CREATE PROCEDURE generate_sections()
BEGIN
    DECLARE i INT DEFAULT 1;

    START TRANSACTION;

    WHILE i <= 600 DO

        INSERT INTO course_sections
        (
            course_id,instructor_id,room_id,
            semester,academic_year,section_no,
            max_students,schedule_days,schedule_time
        )
        VALUES
        (
            1 + FLOOR(RAND()*300),
            1 + FLOOR(RAND()*100),
            1 + FLOOR(RAND()*5),
            ELT(1+FLOOR(RAND()*3),'Fall','Spring','Summer'),
            2023 + FLOOR(RAND()*3),
            CONCAT('S',1+FLOOR(RAND()*9)),
            20 + FLOOR(RAND()*30),
            ELT(1+FLOOR(RAND()*4),'MW','TR','MWF','FS'),
            ELT(1+FLOOR(RAND()*4),'08:00','10:00','12:00','14:00')
        );

        SET i = i + 1;

    END WHILE;

    COMMIT;
END$$
DELIMITER ;

CALL generate_sections();
DROP PROCEDURE generate_sections;

-- =====================================================
-- STEP 8: ENROLLMENTS (50,000)
-- BATCH INSERT TO PREVENT TIMEOUT
-- =====================================================

DROP PROCEDURE IF EXISTS generate_enrollments;
DELIMITER $$

CREATE PROCEDURE generate_enrollments()
BEGIN
    DECLARE batch_no INT DEFAULT 1;
    DECLARE i INT;

    WHILE batch_no <= 5 DO

        START TRANSACTION;
        SET i = 1;

        WHILE i <= 10000 DO

            INSERT INTO enrollments
            (
                student_id, section_id, enroll_date,
                grade, attendance_percent, status
            )
            VALUES
            (
                1 + FLOOR(RAND()*10000),
                1 + FLOOR(RAND()*600),
                DATE_ADD('2023-01-01', INTERVAL FLOOR(RAND()*700) DAY),
                ELT(1+FLOOR(RAND()*7),
                    'A','B','C','D','F','I','W'),
                ROUND(60 + RAND()*40,2),
                ELT(1+FLOOR(RAND()*3),
                    'Enrolled','Dropped','Completed')
            );

            SET i = i + 1;

        END WHILE;

        COMMIT;

        SET batch_no = batch_no + 1;

    END WHILE;

END$$
DELIMITER ;

CALL generate_enrollments();
DROP PROCEDURE generate_enrollments;

-- =====================================================
-- STEP 9: HELPFUL RESEARCH INDEXES
-- =====================================================

CREATE INDEX idx_students_gpa_city ON students(gpa, city);
CREATE INDEX idx_students_dept_status ON students(dept_id, status);
CREATE INDEX idx_enrollments_student_grade ON enrollments(student_id, grade);
CREATE INDEX idx_sections_semester_year ON course_sections(semester, academic_year);

-- =====================================================
-- STEP 10: VERIFY COUNTS
-- =====================================================

SELECT 'departments' table_name, COUNT(*) rows_count FROM departments
UNION ALL
SELECT 'students', COUNT(*) FROM students
UNION ALL
SELECT 'instructors', COUNT(*) FROM instructors
UNION ALL
SELECT 'courses', COUNT(*) FROM courses
UNION ALL
SELECT 'classrooms', COUNT(*) FROM classrooms
UNION ALL
SELECT 'course_sections', COUNT(*) FROM course_sections
UNION ALL
SELECT 'enrollments', COUNT(*) FROM enrollments;

-- =====================================================
-- STEP 11: HELPFUL RESEARCH QUERIES
-- =====================================================

-- Slow join test
SELECT s.first_name, c.course_title
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN course_sections cs ON e.section_id = cs.section_id
JOIN courses c ON cs.course_id = c.course_id
WHERE s.gpa > 3.0;

-- Aggregate test
SELECT dept_id, AVG(gpa), COUNT(*)
FROM students
GROUP BY dept_id;

-- Sort test
SELECT * FROM students
ORDER BY gpa DESC
LIMIT 100;