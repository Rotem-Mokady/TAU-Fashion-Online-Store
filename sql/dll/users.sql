CREATE TABLE `users` (
  `email` varchar(30) NOT NULL,
  `username` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL,
  `is_manager` tinyint(1) NOT NULL DEFAULT '0',
  `gender` varchar(10) NOT NULL DEFAULT 'Unknown',
  `birth_date` datetime DEFAULT NULL,
  `faculty` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`email`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
