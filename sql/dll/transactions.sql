CREATE TABLE `transactions` (
  `id` bigint NOT NULL,
  `user_mail` varchar(30) NOT NULL,
  `cloth_id` int NOT NULL,
  `amount` int NOT NULL,
  `purchase_time` datetime NOT NULL,
  PRIMARY KEY (`id`,`user_mail`,`cloth_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
