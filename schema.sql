DROP DATABASE IF EXISTS research_buddy;

CREATE DATABASE research_buddy;

USE research_buddy;

CREATE TABLE `departments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(35) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `accounts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(35) NOT NULL,
  `password` varchar(35) NOT NULL,
  `first` varchar(35) NOT NULL,
  `last` varchar(35) NOT NULL,
  `email` varchar(35) NOT NULL,
  `resume` varchar(35) DEFAULT NULL,
  `linkedin` varchar(35) DEFAULT NULL,
  `department_id` int(11) NOT NULL,
  `status` varchar(9) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `account` (`username`,`password`),
  KEY `departments_id` (`department_id`),
  CONSTRAINT `departments_id` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_status` CHECK (`status` in ('admin','professor','student'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `admin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  CONSTRAINT `admin_id` FOREIGN KEY (`id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `professors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `website` varchar(35) DEFAULT NULL,
  `status` varchar(9) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `professor_id` FOREIGN KEY (`id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_status` CHECK (`status` in ('assistant','associate','full'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `students` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` varchar(13) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `student_id` FOREIGN KEY (`id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_status` CHECK (`status` in ('undergraduate','graduate'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `projects` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(35) NOT NULL,
  `description` varchar(35) NOT NULL,
  `department_id` int(11) NOT NULL,
  `link` varchar(35) NOT NULL,
  `professor_id` int(11) NOT NULL,
  `status` varchar(9) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `projects_professor_id` (`professor_id`),
  KEY `projects_department_id` (`department_id`),
  CONSTRAINT `projects_department_id` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `projects_professor_id` FOREIGN KEY (`professor_id`) REFERENCES `professors` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_status` CHECK (`status` in ('open','closed','paused'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `projects_students` (
  `student_id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  PRIMARY KEY (`student_id`,`project_id`),
  KEY `projectsrel_project_id` (`project_id`),
  CONSTRAINT `projectsrel_project_id` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `projectsrel_student_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `status_codes` (
  `id` int(11) NOT NULL,
  `account` varchar(35) NOT NULL,
  `code` int(4) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `status_codes` (`id`, `account`, `code`) VALUES ('1', 'admin', '1234');
INSERT INTO 'departments' ('id', 'name') VALUES ('1', 'College of Agriculture'),
('2', 'College of Arts and Sciences'),
('3', 'College of Business'),
('4', 'College of Education'),
('5', 'College of Engineering'),
('6', 'College of Health Sciences'),
('7', 'College of Law'),
('8', 'College of Medicine'),
('9', 'College of Pharmacy'),
('10', 'College of Public Health');