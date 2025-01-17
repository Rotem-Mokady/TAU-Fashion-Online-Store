CREATE TABLE `transactions` (
  `id` int NOT NULL,
  `user_mail` varchar(30) NOT NULL,
  `purchase_time` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_mail_idx` (`user_mail`) /*!80000 INVISIBLE */,
  CONSTRAINT `user_mail` FOREIGN KEY (`user_mail`) REFERENCES `users` (`email`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
