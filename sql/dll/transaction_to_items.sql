CREATE TABLE `transaction_to_items` (
  `transaction_id` int NOT NULL,
  `cloth_id` int NOT NULL,
  `amount` int NOT NULL,
  PRIMARY KEY (`transaction_id`,`cloth_id`),
  KEY `cloth_id_idx` (`cloth_id`) /*!80000 INVISIBLE */,
  CONSTRAINT `cloth_id_fk` FOREIGN KEY (`cloth_id`) REFERENCES `cloths` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `transaction_id_fk` FOREIGN KEY (`transaction_id`) REFERENCES `transactions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
