CREATE TABLE `cloths` (
  `id` int NOT NULL,
  `name` varchar(45) NOT NULL,
  `sex` varchar(10) NOT NULL,
  `path` varchar(200) NOT NULL,
  `price` decimal(10,0) NOT NULL,
  `inventory` int NOT NULL,
  `campaign` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`,`name`,`sex`,`path`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
