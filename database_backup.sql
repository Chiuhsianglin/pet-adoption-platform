-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: pet_adoption
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `adoption_applications`
--

DROP TABLE IF EXISTS `adoption_applications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `adoption_applications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pet_id` int NOT NULL,
  `applicant_id` int NOT NULL,
  `shelter_id` int DEFAULT NULL,
  `status` enum('draft','pending','submitted','document_review','home_visit_scheduled','home_visit_completed','under_evaluation','approved','rejected','completed','withdrawn') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'draft',
  `reviewed_by` int DEFAULT NULL,
  `reviewed_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `application_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `personal_info` json NOT NULL,
  `living_environment` json NOT NULL,
  `pet_experience` json NOT NULL,
  `review_notes` text COLLATE utf8mb4_unicode_ci,
  `submitted_at` datetime DEFAULT NULL,
  `home_visit_date` datetime DEFAULT NULL COMMENT '家訪日期',
  `home_visit_notes` text COLLATE utf8mb4_unicode_ci COMMENT '家訪記錄',
  `home_visit_document` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '家訪文件檔案路徑',
  `final_decision_notes` text COLLATE utf8mb4_unicode_ci COMMENT '最終決定備註（通過時的聯絡事項或拒絕原因）',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_adoption_applications_application_id` (`application_id`),
  KEY `fk_adoption_applications_reviewed_by_users` (`reviewed_by`),
  KEY `ix_adoption_applications_id` (`id`),
  KEY `ix_adoption_applications_applicant_id` (`applicant_id`),
  KEY `ix_adoption_applications_pet_id` (`pet_id`),
  KEY `ix_adoption_applications_status` (`status`),
  KEY `fk_application_shelter` (`shelter_id`),
  KEY `idx_adoption_applications_status` (`status`),
  KEY `idx_adoption_applications_created_at` (`created_at`),
  KEY `idx_adoption_applications_pet_status` (`pet_id`,`status`),
  CONSTRAINT `fk_adoption_applications_applicant_id_users` FOREIGN KEY (`applicant_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_adoption_applications_pet_id_pets` FOREIGN KEY (`pet_id`) REFERENCES `pets` (`id`),
  CONSTRAINT `fk_adoption_applications_reviewed_by_users` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_application_shelter` FOREIGN KEY (`shelter_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `adoption_applications`
--

LOCK TABLES `adoption_applications` WRITE;
/*!40000 ALTER TABLE `adoption_applications` DISABLE KEYS */;
INSERT INTO `adoption_applications` VALUES (1,3,4,2,'home_visit_scheduled',NULL,NULL,'2025-11-17 13:42:53','2025-11-27 08:45:46','APP20251117F430A3BC','{\"name\": \"林小毛\", \"email\": \"lin@gmail.com\", \"phone\": \"0909111222\", \"address\": \"桃園市中歷區中大路300號\", \"id_number\": \"F222333444\", \"occupation\": \"學生\", \"monthly_income\": 10000}','{\"has_yard\": false, \"other_pets\": [], \"space_size\": 10, \"housing_type\": \"apartment\", \"has_allergies\": false, \"family_members\": 1, \"environment_photos\": [{\"url\": \"https://pet-adoption-files.s3.amazonaws.com/pet_photo/d91648e1-1109-4e7d-9fe6-543f8e2f08d1.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=zFP2thqgdlbGO%2Fw1SlomqWjSAHc%3D&Expires=1763963284\", \"file_key\": \"pet_photo/d91648e1-1109-4e7d-9fe6-543f8e2f08d1.jpg\", \"file_url\": \"https://pet-adoption-files.s3.amazonaws.com/pet_photo/d91648e1-1109-4e7d-9fe6-543f8e2f08d1.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=zFP2thqgdlbGO%2Fw1SlomqWjSAHc%3D&Expires=1763963284\"}]}','{\"care_schedule\": \"安排~~~~~\", \"pet_knowledge\": \"了解~~~~~~\", \"emergency_fund\": 3000, \"veterinarian_info\": \"資訊~~\", \"previous_experience\": \"寵物經驗~~~~\"}',NULL,'2025-11-17 13:49:03','2025-11-27 16:47:00',NULL,NULL,NULL),(5,10,4,3,'document_review',NULL,NULL,'2025-11-17 23:15:08','2025-11-17 15:36:18','APP20251117A31CEE32','{\"name\": \"林小毛\", \"email\": \"lin@gmail.com\", \"phone\": \"0922222222\", \"address\": \"aaaaa\", \"id_number\": \"A222222222\", \"occupation\": \"aaaaa\", \"monthly_income\": 10000}','{\"has_yard\": false, \"other_pets\": [], \"space_size\": 10, \"housing_type\": \"apartment\", \"has_allergies\": false, \"family_members\": 1, \"environment_photos\": [{\"url\": \"https://pet-adoption-files.s3.amazonaws.com/pet_photo/577798e3-e2ae-4726-8e7e-edfa43c86d84.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=%2FKu40CUXvV%2BoXB5zftLylB5HGeY%3D&Expires=1763997290\", \"file_key\": \"pet_photo/577798e3-e2ae-4726-8e7e-edfa43c86d84.jpg\", \"file_url\": \"https://pet-adoption-files.s3.amazonaws.com/pet_photo/577798e3-e2ae-4726-8e7e-edfa43c86d84.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=%2FKu40CUXvV%2BoXB5zftLylB5HGeY%3D&Expires=1763997290\"}]}','{\"care_schedule\": \"aaaaa\", \"pet_knowledge\": \"aaaaa\", \"emergency_fund\": 1000, \"veterinarian_info\": \"aaaaa\", \"previous_experience\": \"aaaaa\"}',NULL,'2025-11-17 23:15:16',NULL,NULL,NULL,NULL),(6,2,4,2,'document_review',NULL,NULL,'2025-11-18 00:51:31','2025-11-29 12:59:13','APP20251118607FEAAA','{\"name\": \"林小毛\", \"email\": \"lin@gmail.com\", \"phone\": \"0922222222\", \"address\": \"地址des\", \"id_number\": \"A222222222\", \"occupation\": \"aa\", \"monthly_income\": 11}','{\"has_yard\": false, \"other_pets\": [], \"space_size\": 20, \"housing_type\": \"apartment\", \"has_allergies\": false, \"family_members\": 4, \"environment_photos\": [{\"url\": \"https://pet-adoption-files.s3.amazonaws.com/pet_photo/54d5ca97-27ed-4752-8ee7-c9491bc95553.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=pmxwWkGPE918FOMa9beBY1%2FbnW8%3D&Expires=1764003075\", \"file_key\": \"pet_photo/54d5ca97-27ed-4752-8ee7-c9491bc95553.jpg\", \"file_url\": \"https://pet-adoption-files.s3.amazonaws.com/pet_photo/54d5ca97-27ed-4752-8ee7-c9491bc95553.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=pmxwWkGPE918FOMa9beBY1%2FbnW8%3D&Expires=1764003075\"}]}','{\"care_schedule\": \"ewwewe\", \"pet_knowledge\": \"eeee\", \"emergency_fund\": 200, \"veterinarian_info\": \"ewew\", \"previous_experience\": \"aaaaaaaaa\"}',NULL,'2025-11-18 00:51:40',NULL,NULL,NULL,NULL),(7,9,4,3,'submitted',NULL,NULL,'2025-11-18 00:56:55','2025-11-18 00:57:02','APP202511181991E998','{\"name\": \"林小毛\", \"email\": \"lin@gmail.com\", \"phone\": \"0909232323\", \"address\": \"elkrhwr\", \"id_number\": \"A222222222\", \"occupation\": \"kejrl\", \"monthly_income\": 20000}','{\"has_yard\": false, \"other_pets\": [], \"space_size\": 19, \"housing_type\": \"apartment\", \"has_allergies\": false, \"family_members\": 3, \"environment_photos\": [{\"url\": \"https://pet-adoption-files.s3.amazonaws.com/pet_photo/4884f82d-7873-4480-8ade-3ded90c55b9e.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=1Bb6Q1IOAYxgjqXMpq0Y2UgLONY%3D&Expires=1764003396\", \"file_key\": \"pet_photo/4884f82d-7873-4480-8ade-3ded90c55b9e.jpg\", \"file_url\": \"https://pet-adoption-files.s3.amazonaws.com/pet_photo/4884f82d-7873-4480-8ade-3ded90c55b9e.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=1Bb6Q1IOAYxgjqXMpq0Y2UgLONY%3D&Expires=1764003396\"}]}','{\"care_schedule\": \"jklewjr\", \"pet_knowledge\": \"jlwehrl\", \"emergency_fund\": 3000, \"veterinarian_info\": \"kelwr\", \"previous_experience\": \"iehrilhrlwe\"}',NULL,'2025-11-18 00:57:03',NULL,NULL,NULL,NULL),(8,1,4,2,'approved',2,'2025-11-28 11:18:10','2025-11-18 12:25:38','2025-11-28 11:18:10','APP20251118EF858D32','{\"name\": \"林小毛\", \"email\": \"lin@gmail.com\", \"phone\": \"0987654334\", \"address\": \"1111\", \"id_number\": \"A123145535\", \"occupation\": \"2222\", \"monthly_income\": 8000}','{\"has_yard\": true, \"other_pets\": [], \"space_size\": 22354678, \"housing_type\": \"apartment\", \"has_allergies\": false, \"family_members\": 11234, \"environment_photos\": [{\"url\": \"https://pet-adoption-files.s3.amazonaws.com/pet_photo/e8695d1a-45ca-4ad7-812f-8eb61610b093.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=a%2BOYGnwl32iXZ9XMh1N9kO%2FC2rI%3D&Expires=1764044684\", \"file_key\": \"pet_photo/e8695d1a-45ca-4ad7-812f-8eb61610b093.jpg\", \"file_url\": \"https://pet-adoption-files.s3.amazonaws.com/pet_photo/e8695d1a-45ca-4ad7-812f-8eb61610b093.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=a%2BOYGnwl32iXZ9XMh1N9kO%2FC2rI%3D&Expires=1764044684\"}]}','{\"care_schedule\": \"隨便\", \"pet_knowledge\": \"super\", \"emergency_fund\": 10000, \"veterinarian_info\": \"11\", \"previous_experience\": \"1234\"}',NULL,'2025-11-18 12:25:52','2025-11-29 16:33:00','1128測試3','home_visit_document/bd548b8d-e69a-469c-9e45-ae2f8bcb5632.pdf','1128通過'),(9,11,4,2,'draft',NULL,NULL,'2025-11-27 15:33:26','2025-11-27 15:33:26','APP20251127219724F1','{}','{}','{}',NULL,NULL,NULL,NULL,NULL,NULL),(10,16,4,2,'draft',NULL,NULL,'2025-11-27 15:48:55','2025-11-27 16:02:25','APP20251127D8C653CF','{\"name\": \"林小毛\", \"email\": \"lin@gmail.com\", \"phone\": \"0911222333\", \"address\": \"\", \"id_number\": \"\", \"occupation\": \"\", \"monthly_income\": 0}','{\"has_yard\": false, \"other_pets\": [], \"space_size\": 0, \"housing_type\": \"apartment\", \"has_allergies\": false, \"family_members\": 1}','{\"care_schedule\": \"\", \"pet_knowledge\": \"\", \"emergency_fund\": 0, \"veterinarian_info\": \"\", \"previous_experience\": \"\"}',NULL,NULL,NULL,NULL,NULL,NULL),(11,11,7,2,'draft',NULL,NULL,'2025-11-27 15:51:14','2025-11-27 15:51:14','APP202511277F7B1D4B','{\"name\": \"Chen Test\", \"email\": \"chen@gmail.com\", \"phone\": \"0912345678\", \"address\": \"??????\", \"id_number\": \"A123456789\", \"occupation\": \"???\", \"monthly_income\": 60000}','{\"has_yard\": false, \"other_pets\": [], \"space_size\": 60, \"housing_type\": \"apartment\", \"has_allergies\": false, \"family_members\": 3}','{\"care_schedule\": \"??????\", \"pet_knowledge\": \"??????\", \"emergency_fund\": 20000, \"veterinarian_info\": \"??????\", \"previous_experience\": \"????\"}',NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `adoption_applications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `application_documents`
--

DROP TABLE IF EXISTS `application_documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `application_documents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `application_id` int NOT NULL,
  `document_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `file_url` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_key` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_size` int NOT NULL,
  `mime_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `file_hash` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `security_scan_status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'pending',
  `scan_result` text COLLATE utf8mb4_unicode_ci,
  `original_filename` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `stored_filename` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `file_path` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `uploaded_by` int NOT NULL,
  `uploaded_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('PENDING','REVIEWING','APPROVED','REJECTED','RESUBMISSION_REQUIRED') COLLATE utf8mb4_unicode_ci NOT NULL,
  `reviewed_by` int DEFAULT NULL,
  `reviewed_at` datetime DEFAULT NULL,
  `review_notes` text COLLATE utf8mb4_unicode_ci,
  `is_safe` tinyint(1) DEFAULT NULL,
  `version` int DEFAULT NULL,
  `is_current_version` tinyint(1) DEFAULT NULL,
  `replaced_by_id` int DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_application_documents_id` (`id`),
  KEY `ix_application_documents_application_id` (`application_id`),
  KEY `fk_application_documents_reviewed_by_users` (`reviewed_by`),
  KEY `fk_application_documents_uploaded_by_users` (`uploaded_by`),
  KEY `fk_application_documents_replaced_by_id_application_documents` (`replaced_by_id`),
  CONSTRAINT `fk_application_documents_application_id_adoption_applications` FOREIGN KEY (`application_id`) REFERENCES `adoption_applications` (`id`),
  CONSTRAINT `fk_application_documents_replaced_by_id_application_documents` FOREIGN KEY (`replaced_by_id`) REFERENCES `application_documents` (`id`),
  CONSTRAINT `fk_application_documents_reviewed_by_users` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_application_documents_uploaded_by_users` FOREIGN KEY (`uploaded_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `application_documents`
--

LOCK TABLES `application_documents` WRITE;
/*!40000 ALTER TABLE `application_documents` DISABLE KEYS */;
INSERT INTO `application_documents` VALUES (1,1,'income','收入證明.jpg','https://pet-adoption-files.s3.ap-southeast-2.amazonaws.com/applications/1/documents/20251117_135912_收入證明.jpg','applications/1/documents/20251117_135912_收入證明.jpg',34288,'image/jpeg','2025-11-17 13:59:14',NULL,'pending',NULL,'收入證明.jpg',NULL,'applications/1/documents/20251117_135912_收入證明.jpg',4,'2025-11-17 13:59:14','PENDING',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(2,1,'identity','身分證明.jpg','https://pet-adoption-files.s3.ap-southeast-2.amazonaws.com/applications/1/documents/20251117_135918_身分證明.jpg','applications/1/documents/20251117_135918_身分證明.jpg',31936,'image/jpeg','2025-11-17 13:59:20',NULL,'pending',NULL,'身分證明.jpg',NULL,'applications/1/documents/20251117_135918_身分證明.jpg',4,'2025-11-17 13:59:20','PENDING',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(3,1,'residence','居住證明.jpg','https://pet-adoption-files.s3.ap-southeast-2.amazonaws.com/applications/1/documents/20251117_135924_居住證明.jpg','applications/1/documents/20251117_135924_居住證明.jpg',209553,'image/jpeg','2025-11-17 13:59:26',NULL,'pending',NULL,'居住證明.jpg',NULL,'applications/1/documents/20251117_135924_居住證明.jpg',4,'2025-11-17 13:59:26','PENDING',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(4,7,'income','收入證明.jpg','https://pet-adoption-files.s3.ap-southeast-2.amazonaws.com/applications/7/documents/20251118_005732_收入證明.jpg','applications/7/documents/20251118_005732_收入證明.jpg',34288,'image/jpeg','2025-11-18 00:57:35',NULL,'pending',NULL,'收入證明.jpg',NULL,'applications/7/documents/20251118_005732_收入證明.jpg',4,'2025-11-18 00:57:35','PENDING',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(5,7,'identity','身分證明.jpg','https://pet-adoption-files.s3.ap-southeast-2.amazonaws.com/applications/7/documents/20251118_005739_身分證明.jpg','applications/7/documents/20251118_005739_身分證明.jpg',31936,'image/jpeg','2025-11-18 00:57:41',NULL,'pending',NULL,'身分證明.jpg',NULL,'applications/7/documents/20251118_005739_身分證明.jpg',4,'2025-11-18 00:57:41','PENDING',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(6,7,'residence','居住證明.jpg','https://pet-adoption-files.s3.ap-southeast-2.amazonaws.com/applications/7/documents/20251118_005746_居住證明.jpg','applications/7/documents/20251118_005746_居住證明.jpg',209553,'image/jpeg','2025-11-18 00:57:49',NULL,'pending',NULL,'居住證明.jpg',NULL,'applications/7/documents/20251118_005746_居住證明.jpg',4,'2025-11-18 00:57:49','PENDING',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(7,8,'income','收入證明.jpg','https://pet-adoption-files.s3.ap-southeast-2.amazonaws.com/applications/8/documents/20251118_122647_收入證明.jpg','applications/8/documents/20251118_122647_收入證明.jpg',34288,'image/jpeg','2025-11-18 12:26:49',NULL,'pending',NULL,'收入證明.jpg',NULL,'applications/8/documents/20251118_122647_收入證明.jpg',4,'2025-11-18 12:26:49','PENDING',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(8,8,'identity','身分證明.jpg','https://pet-adoption-files.s3.ap-southeast-2.amazonaws.com/applications/8/documents/20251118_122654_身分證明.jpg','applications/8/documents/20251118_122654_身分證明.jpg',31936,'image/jpeg','2025-11-18 12:26:56',NULL,'pending',NULL,'身分證明.jpg',NULL,'applications/8/documents/20251118_122654_身分證明.jpg',4,'2025-11-18 12:26:56','PENDING',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(9,8,'residence','測試.pdf','https://pet-adoption-files.s3.ap-southeast-2.amazonaws.com/applications/8/documents/20251118_122701_測試.pdf','applications/8/documents/20251118_122701_測試.pdf',18948,'application/pdf','2025-11-18 12:27:03',NULL,'pending',NULL,'測試.pdf',NULL,'applications/8/documents/20251118_122701_測試.pdf',4,'2025-11-18 12:27:03','PENDING',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `application_documents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat_messages`
--

DROP TABLE IF EXISTS `chat_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `room_id` int NOT NULL COMMENT '聊天室ID',
  `sender_id` int NOT NULL COMMENT '發送者ID',
  `message_type` enum('TEXT','IMAGE','FILE','PET_CARD') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '訊息類型',
  `content` text COLLATE utf8mb4_unicode_ci COMMENT '文字內容',
  `file_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'S3檔案URL',
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '檔案名稱',
  `file_size` int DEFAULT NULL COMMENT '檔案大小(bytes)',
  `is_read` tinyint(1) NOT NULL COMMENT '是否已讀',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_room_id` (`room_id`),
  KEY `idx_sender_id` (`sender_id`),
  KEY `ix_chat_messages_id` (`id`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_is_read` (`is_read`),
  KEY `idx_room_created` (`room_id`,`created_at`),
  CONSTRAINT `fk_chat_messages_room_id_chat_rooms` FOREIGN KEY (`room_id`) REFERENCES `chat_rooms` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_chat_messages_sender_id_users` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_messages`
--

LOCK TABLES `chat_messages` WRITE;
/*!40000 ALTER TABLE `chat_messages` DISABLE KEYS */;
INSERT INTO `chat_messages` VALUES (1,1,4,'PET_CARD','詢問關於 lucky 的領養資訊',NULL,NULL,NULL,0,'2025-11-17 03:49:29'),(2,1,4,'TEXT','好可愛',NULL,NULL,NULL,0,'2025-11-17 03:51:25'),(3,5,4,'TEXT','你好！我想詢問有關多多的資訊~',NULL,NULL,NULL,1,'2025-11-28 23:59:52'),(4,5,2,'TEXT','你好～',NULL,NULL,NULL,1,'2025-11-29 20:41:24'),(5,5,2,'IMAGE',NULL,'https://pet-adoption-files.s3.amazonaws.com/chat/80604b23-8902-48f8-99bd-0b47d5d5a6f3.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=ajMhezmee4TVwurCzCMvqLdyKDk%3D&Expires=1765024901','80604b23-8902-48f8-99bd-0b47d5d5a6f3.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=ajMhezmee4TVwurCzCMvqLdyKDk%3D&Expires=1765024901',0,1,'2025-11-29 20:41:45'),(6,5,2,'FILE',NULL,'https://pet-adoption-files.s3.amazonaws.com/chat/ebb0018a-0386-4061-9c6d-d69c8e5acc03.pdf?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=nV3iPXNh8WPLL59ClLAaz%2FHhikQ%3D&Expires=1765025447','測試.pdf',18948,1,'2025-11-29 20:50:51'),(7,5,4,'TEXT','嗨',NULL,NULL,NULL,1,'2025-11-29 22:28:11'),(8,5,4,'TEXT','測試未讀通知',NULL,NULL,NULL,1,'2025-11-29 22:37:44'),(9,5,4,'IMAGE',NULL,'https://dveld8gbmt3v4.cloudfront.net/chat/324c53eb-578a-4ad2-b7b8-f6c1c737f59c.webp','324c53eb-578a-4ad2-b7b8-f6c1c737f59c.webp',0,0,'2025-11-30 20:03:23');
/*!40000 ALTER TABLE `chat_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat_rooms`
--

DROP TABLE IF EXISTS `chat_rooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_rooms` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '申請者ID',
  `shelter_id` int NOT NULL COMMENT '收容所ID',
  `pet_id` int NOT NULL COMMENT '寵物ID',
  `last_message_at` datetime DEFAULT NULL COMMENT '最後訊息時間',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_room` (`user_id`,`shelter_id`,`pet_id`),
  KEY `ix_chat_rooms_id` (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_shelter_id` (`shelter_id`),
  KEY `idx_pet_id` (`pet_id`),
  KEY `idx_last_message_at` (`last_message_at`),
  CONSTRAINT `fk_chat_rooms_pet_id_pets` FOREIGN KEY (`pet_id`) REFERENCES `pets` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_chat_rooms_shelter_id_users` FOREIGN KEY (`shelter_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_chat_rooms_user_id_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_rooms`
--

LOCK TABLES `chat_rooms` WRITE;
/*!40000 ALTER TABLE `chat_rooms` DISABLE KEYS */;
INSERT INTO `chat_rooms` VALUES (1,4,2,3,'2025-11-17 03:51:25','2025-11-17 03:49:29','2025-11-17 03:51:25'),(2,4,2,16,NULL,'2025-11-28 20:33:08','2025-11-28 20:33:08'),(3,4,2,11,NULL,'2025-11-28 23:36:44','2025-11-28 23:36:44'),(4,4,3,6,NULL,'2025-11-28 23:46:13','2025-11-28 23:46:13'),(5,4,2,5,'2025-11-30 12:03:23','2025-11-28 23:53:45','2025-11-30 20:03:23');
/*!40000 ALTER TABLE `chat_rooms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comment_likes`
--

DROP TABLE IF EXISTS `comment_likes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comment_likes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `comment_id` int NOT NULL COMMENT '留言ID',
  `user_id` int NOT NULL COMMENT '按讚者ID',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_comment_user_like` (`comment_id`,`user_id`),
  KEY `idx_comment_id` (`comment_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `ix_comment_likes_id` (`id`),
  CONSTRAINT `fk_comment_likes_comment_id_post_comments` FOREIGN KEY (`comment_id`) REFERENCES `post_comments` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_comment_likes_user_id_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comment_likes`
--

LOCK TABLES `comment_likes` WRITE;
/*!40000 ALTER TABLE `comment_likes` DISABLE KEYS */;
/*!40000 ALTER TABLE `comment_likes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `community_posts`
--

DROP TABLE IF EXISTS `community_posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `community_posts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '發文者ID',
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `post_type` enum('question','share') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'share' COMMENT '貼文類型',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否已刪除',
  PRIMARY KEY (`id`),
  KEY `ix_community_posts_created_at` (`created_at`),
  KEY `ix_community_posts_id` (`id`),
  KEY `ix_community_posts_post_type` (`post_type`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_is_deleted` (`is_deleted`),
  KEY `idx_community_posts_created_at` (`created_at`),
  KEY `idx_community_posts_user_deleted` (`user_id`,`is_deleted`),
  CONSTRAINT `fk_community_posts_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `community_posts`
--

LOCK TABLES `community_posts` WRITE;
/*!40000 ALTER TABLE `community_posts` DISABLE KEYS */;
INSERT INTO `community_posts` VALUES (1,2,'今天帶我家毛孩去公園玩，牠超開心的！看到其他狗狗都會興奮地搖尾巴 🐕💕','share','2025-11-17 10:47:17','2025-11-17 02:50:39',0),(2,2,'請問大家都是怎麼幫狗狗洗澡的呢？我家的狗狗很怕水，每次洗澡都像打仗一樣... 有什麼好方法可以讓牠放鬆嗎？','question','2025-11-17 10:47:17','2025-11-17 02:49:41',0),(3,3,'我家的橘貓又在曬太陽了 😸☀️ 每天最喜歡做的事就是找個舒服的地方睡覺，真是太療癒了！','share','2025-11-17 10:47:17','2025-11-17 02:55:16',0),(4,3,'分享一下我家貓咪的新玩具！牠超愛這個逗貓棒，可以玩一整天 🎣🐱','share','2025-11-17 10:47:17','2025-11-17 02:56:43',0),(5,3,'想請教各位貓奴們，你們都用什麼貓砂呢？我最近在考慮換豆腐砂，不知道好不好用？','question','2025-11-17 10:47:17','2025-11-17 02:58:19',0),(6,2,'1129測試發文 \r\n編輯測試\r\n測試2','question','2025-11-29 20:56:50','2025-11-29 22:01:32',1);
/*!40000 ALTER TABLE `community_posts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `notification_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `link` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `type` enum('application','message','system','reminder') COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_read` tinyint(1) DEFAULT NULL,
  `action_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `metadata` json DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_notifications_id` (`id`),
  KEY `ix_notifications_notification_type` (`notification_type`),
  KEY `idx_notifications_user_created` (`user_id`,`created_at`),
  KEY `idx_notifications_user_read` (`user_id`,`is_read`),
  CONSTRAINT `fk_notifications_user_id_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (1,3,'新讚','林小毛 按讚了你的貼文','POST_LIKE','/community/5','application',1,NULL,NULL,'2025-11-17 14:43:48',NULL),(2,1,'測試通知','這是測試訊息','POST_LIKE','/community/1','application',1,NULL,NULL,'2025-11-17 14:45:57',NULL),(4,3,'新讚','毛星球之家 按讚了你的貼文','POST_LIKE','/community/5','application',1,NULL,NULL,'2025-11-17 14:49:44',NULL),(6,3,'新讚','毛星球之家 按讚了你的貼文','POST_LIKE','/community/4','application',1,NULL,NULL,'2025-11-17 14:56:52',NULL),(7,3,'新讚','毛星球之家 按讚了你的貼文','POST_LIKE','/community/3','application',1,NULL,NULL,'2025-11-17 14:59:40',NULL),(8,3,'新留言','毛星球之家 在你的貼文留言','POST_COMMENT','/community/5','application',1,NULL,NULL,'2025-11-17 15:06:18',NULL),(11,4,'請補充申請文件','您的申請文件（申請編號 #5）尚未上傳完整。請至「我的申請」頁面上傳所需文件，以便我們進行審核。感謝您的配合！','APPLICATION_STATUS','/applications/5/documents','application',1,NULL,NULL,'2025-11-17 15:42:12',NULL),(13,3,'收到新的領養申請','林小毛 提交了一份領養申請，申請領養 虎斑（申請編號 #7）。請盡快審核此申請。','APPLICATION_STATUS','/adoptions/applications/7','application',0,NULL,NULL,'2025-11-18 00:57:03',NULL),(14,4,'請補充申請文件','您的申請文件（申請編號 #6）尚未上傳完整。請至「我的申請」頁面上傳所需文件，以便我們進行審核。感謝您的配合！','APPLICATION_STATUS','/applications/6/documents','application',1,NULL,NULL,'2025-11-18 00:58:18',NULL),(16,4,'家訪已安排','家訪時間：2025年11月28日 16:33',NULL,NULL,'application',1,NULL,NULL,'2025-11-27 08:33:57',NULL),(17,4,'家訪已安排','家訪時間：2025年11月28日 16:42',NULL,NULL,'application',1,NULL,NULL,'2025-11-27 08:42:24',NULL),(18,4,'家訪已安排','家訪時間：2025年11月27日 16:47',NULL,NULL,'application',1,NULL,NULL,'2025-11-27 08:45:46',NULL),(19,4,'家訪已安排','家訪時間：2025年11月29日 16:33',NULL,NULL,'application',1,NULL,NULL,'2025-11-28 08:37:52',NULL),(20,4,'家訪已安排','家訪時間：2025年11月30日 16:33',NULL,NULL,'application',1,NULL,NULL,'2025-11-28 11:04:11',NULL),(21,4,'家訪時間已更改','新時間：2025年11月29日 16:33',NULL,NULL,'application',1,NULL,NULL,'2025-11-28 11:07:33',NULL),(22,4,'家訪已完成','您的領養申請家訪已完成，我們正在進行評估。',NULL,NULL,'application',1,NULL,NULL,'2025-11-28 11:09:08',NULL),(23,4,'家訪已完成','您的領養申請家訪已完成，我們正在進行評估。',NULL,NULL,'application',1,NULL,NULL,'2025-11-28 11:10:59',NULL),(24,4,'領養申請已通過','恭喜！申請已通過，請聯繫收容所安排領養手續。',NULL,NULL,'application',1,NULL,NULL,'2025-11-28 11:18:10',NULL),(25,4,'請補充文件','您的申請文件（申請編號 #APP20251118607FEAAA）尚未上傳完整。請至「我的申請」頁面上傳所需文件，以便我們進行審核。感謝您的配合！',NULL,NULL,'application',1,NULL,NULL,'2025-11-28 11:36:24',NULL),(26,4,'請補充文件','您的申請文件（申請編號 #6）尚未上傳完整。請至「我的申請」頁面上傳所需文件，以便我們進行審核。感謝您的配合！',NULL,NULL,'application',1,NULL,NULL,'2025-11-29 12:59:13',NULL),(27,1,'新的貼文檢舉','用戶 林小毛 檢舉了一則貼文','SYSTEM','/community/3','application',1,NULL,NULL,'2025-11-30 17:56:04',NULL);
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `password_history`
--

DROP TABLE IF EXISTS `password_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `password_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_password_history_id` (`id`),
  KEY `ix_password_history_user_id` (`user_id`),
  CONSTRAINT `fk_password_history_user_id_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `password_history`
--

LOCK TABLES `password_history` WRITE;
/*!40000 ALTER TABLE `password_history` DISABLE KEYS */;
INSERT INTO `password_history` VALUES (1,1,'$2b$12$GDxmwHGbeECahhTSnOVd3OyI8IEbHBm/mgWzV/lW2LTJcPWATNmkC','2025-11-16 15:06:41'),(2,2,'$2b$12$cu7siScBqlHwP8uYwaO2s.Sq6ech6/DMARa.rgBx38DGvndY9Zfq.','2025-11-16 15:08:10'),(3,3,'$2b$12$OhIJhcivWM.Ogl0LXUxviOu0nx5d5eEYSHPQK1Qb7Dmi80YDIFZ1m','2025-11-16 15:11:30'),(4,4,'$2b$12$.UCxpj9k53lXU4gENmFDz.KJ4SanaHXWfKWTAGzn1a2i8nzww.56K','2025-11-17 03:06:59'),(5,5,'$2b$12$FhEt5YcID.GRYxJELSfDMODjKWmd1wB5k6zk/XSo9OMTa2GTkKsp6','2025-11-24 17:25:56'),(6,6,'$2b$12$7Ks365dgbR2w.PXRK.xGyOxlNhFhGYmUlz5RJ.kmXfL/xmz0pQrb6','2025-11-25 03:58:24'),(7,6,'$2b$12$xUmfs6bL/FD6hWxy43JWW.KS8ke6bLpBywC.83H3sFYVf.KyyrZ2C','2025-11-26 15:45:54'),(8,6,'$2b$12$UuD4txmNsCWpbKAFEaZyAeZXCQl00UN6N95ws4fXMEsS317nMet1i','2025-11-26 15:50:15'),(9,4,'$2b$12$xL3lET5F2RcQDzHPwhLedOCHGM7GE8m5gFUECstR5dg3OdZ.TsEju','2025-11-26 15:52:42'),(10,7,'$2b$12$zwVkB4IaP0mAUZ.WZOc0c./erE52YjxZGGxoqeuHS3nPFN41mMo.O','2025-11-26 15:53:38'),(11,8,'$2b$12$EYjF7HeU6w49TP1wZLTB5uxqnIi0uMNdLzxoS2tb74eDP5TNvfQkm','2025-11-30 15:07:44');
/*!40000 ALTER TABLE `password_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pet_photos`
--

DROP TABLE IF EXISTS `pet_photos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pet_photos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pet_id` int NOT NULL,
  `file_url` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_key` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_primary` tinyint(1) DEFAULT NULL,
  `caption` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `upload_order` int DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_pet_photos_pet_id` (`pet_id`),
  KEY `ix_pet_photos_id` (`id`),
  CONSTRAINT `fk_pet_photos_pet_id_pets` FOREIGN KEY (`pet_id`) REFERENCES `pets` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pet_photos`
--

LOCK TABLES `pet_photos` WRITE;
/*!40000 ALTER TABLE `pet_photos` DISABLE KEYS */;
INSERT INTO `pet_photos` VALUES (2,1,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/f4b9207a-b4dd-4a5b-a616-f5a6462c2518.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=kr4a6f%2F60e%2BTujKOQWgEqGTLkkU%3D&Expires=1763948240','pet_photo/f4b9207a-b4dd-4a5b-a616-f5a6462c2518.jpg',0,NULL,1,'2025-11-17 09:37:39'),(3,1,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/f36724ce-58bf-483f-beb7-64f06c6cf0f8.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=GScqBHhGMo%2BgCUtuvZMgdaKYZmE%3D&Expires=1763948596','pet_photo/f36724ce-58bf-483f-beb7-64f06c6cf0f8.jpg',0,NULL,1,'2025-11-17 09:46:25'),(4,11,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/d65956c7-036b-4b9e-b0d8-f8ab8f69d917.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=gTsZTIUMYdzd5aoUM6%2BAxSAjfxs%3D&Expires=1763949199','pet_photo/d65956c7-036b-4b9e-b0d8-f8ab8f69d917.jpg',1,NULL,0,'2025-11-17 09:55:09'),(5,11,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/0bd71486-bb1f-488a-90da-b3b880114b64.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=cVWksSF2KA0KAYgdVv3mxiJfhyU%3D&Expires=1763949216','pet_photo/0bd71486-bb1f-488a-90da-b3b880114b64.jpg',0,NULL,1,'2025-11-17 09:55:09'),(6,11,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/b2052646-7aaa-4570-9dab-b3a2fe99668a.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=s4quii6ArLSDCIOkAENKzTRuS8k%3D&Expires=1763949230','pet_photo/b2052646-7aaa-4570-9dab-b3a2fe99668a.jpg',0,NULL,2,'2025-11-17 09:55:09'),(7,11,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/ace0d0df-47c7-4e36-b202-c7341ffae524.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=wYt8KGcmOpdg5tydBCMnal%2FDblc%3D&Expires=1763949235','pet_photo/ace0d0df-47c7-4e36-b202-c7341ffae524.jpg',0,NULL,3,'2025-11-17 09:55:09'),(8,11,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/5fac2e74-fdb7-4602-8baf-b0b1fa2ad8bf.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=y5zn4vWOt3kgWiIiaKExKDxOiJU%3D&Expires=1763949252','pet_photo/5fac2e74-fdb7-4602-8baf-b0b1fa2ad8bf.jpg',0,NULL,4,'2025-11-17 09:55:09'),(9,11,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/3035424b-6b0f-4063-a543-0418b634c3c6.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=DhUMmNF1Rc67teQ8XChX7mBtORI%3D&Expires=1763949269','pet_photo/3035424b-6b0f-4063-a543-0418b634c3c6.jpg',0,NULL,5,'2025-11-17 09:55:09'),(10,2,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/2b57d8dd-30f0-42dc-b1e8-bcebbfba633d.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=lULf33lQjQ0uRiMUUQJ6%2FRMkap0%3D&Expires=1763949440','pet_photo/2b57d8dd-30f0-42dc-b1e8-bcebbfba633d.jpg',1,NULL,0,'2025-11-17 09:57:36'),(11,3,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/df2ff6ef-f5b7-4537-bbb4-a1b4e54fd170.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=fmOVw8k6YbcazzBjLQIa5l%2BwMpI%3D&Expires=1763949623','pet_photo/df2ff6ef-f5b7-4537-bbb4-a1b4e54fd170.jpg',1,NULL,0,'2025-11-17 10:01:05'),(12,3,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/1f95f185-8fbd-4564-8d9a-9e60a04dce57.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=qGqB%2B1rkPJBuZtAjDOispsM2c%2B4%3D&Expires=1763949635','pet_photo/1f95f185-8fbd-4564-8d9a-9e60a04dce57.jpg',0,NULL,1,'2025-11-17 10:01:05'),(13,4,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/1ac020a5-56e5-4389-8f65-989ef76354ca.png?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=RvQ5UiVg41C2%2BtXTuwHYlVXVGak%3D&Expires=1763949711','pet_photo/1ac020a5-56e5-4389-8f65-989ef76354ca.png',1,NULL,0,'2025-11-17 10:02:05'),(14,5,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/6bc4aac4-1198-4f9f-83c0-128f38c23fa6.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=bJ2fLUM9Tt4YZhUaC2%2FaFXGbER0%3D&Expires=1763949850','pet_photo/6bc4aac4-1198-4f9f-83c0-128f38c23fa6.jpg',1,NULL,0,'2025-11-17 10:04:23'),(15,6,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/5af7b52a-c58c-42ee-8715-3f90b8d8ffbb.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=kNmED4eYoqIg%2FPTsSFn9f9vhZ2A%3D&Expires=1763950148','pet_photo/5af7b52a-c58c-42ee-8715-3f90b8d8ffbb.jpg',1,NULL,0,'2025-11-17 10:09:41'),(16,7,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/ddc293ec-fa98-497f-8c9e-ae90f70cc22b.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=eSIH%2F55Tgh3u0jAOvHC03vcQwqM%3D&Expires=1763950598','pet_photo/ddc293ec-fa98-497f-8c9e-ae90f70cc22b.jpg',1,NULL,0,'2025-11-17 10:18:04'),(17,8,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/8fa35f1e-a810-47f2-b1d9-8384e978f022.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=g04d0noxQOUYOayo6jMFGbdUcxQ%3D&Expires=1763950718','pet_photo/8fa35f1e-a810-47f2-b1d9-8384e978f022.jpg',1,NULL,0,'2025-11-17 10:18:48'),(18,9,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/51f40ec9-c071-48f8-9bd8-da01badc06cf.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=BejqAmNuwArQF24u7zXX50mOTPA%3D&Expires=1763950760','pet_photo/51f40ec9-c071-48f8-9bd8-da01badc06cf.jpg',1,NULL,0,'2025-11-17 10:19:36'),(19,10,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/66fe13db-799e-4c83-a535-c144840d7c27.jpeg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=mzFl0jmStn76JgVcNO%2BiZ5VLnt0%3D&Expires=1763950832','pet_photo/66fe13db-799e-4c83-a535-c144840d7c27.jpeg',1,NULL,0,'2025-11-17 10:20:40'),(21,16,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/4253653f-d9c8-44ba-932d-48cb48dccd72.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=Gt7%2FsgIXArjLaTWxb2vnWJHJcts%3D&Expires=1764782886','pet_photo/4253653f-d9c8-44ba-932d-48cb48dccd72.jpg',1,NULL,0,'2025-11-27 01:29:36'),(22,16,'https://pet-adoption-files.s3.amazonaws.com/pet_photo/b1d04dce-211b-418f-87ba-2d03d40a8888.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=xGV0GldZaIAR5vT0YFyvkMN1QEk%3D&Expires=1764782903','pet_photo/b1d04dce-211b-418f-87ba-2d03d40a8888.jpg',0,NULL,1,'2025-11-27 01:29:36');
/*!40000 ALTER TABLE `pet_photos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pets`
--

DROP TABLE IF EXISTS `pets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `species` enum('dog','cat','bird','rabbit','hamster','fish','reptile','other') COLLATE utf8mb4_unicode_ci NOT NULL,
  `breed` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `age_years` int DEFAULT NULL,
  `age_months` int DEFAULT NULL,
  `gender` enum('male','female','unknown') COLLATE utf8mb4_unicode_ci NOT NULL,
  `size` enum('small','medium','large','extra_large') COLLATE utf8mb4_unicode_ci NOT NULL,
  `weight_kg` float DEFAULT NULL,
  `color` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `medical_info` text COLLATE utf8mb4_unicode_ci,
  `behavioral_info` text COLLATE utf8mb4_unicode_ci,
  `special_needs` text COLLATE utf8mb4_unicode_ci,
  `adoption_fee` decimal(10,2) DEFAULT NULL,
  `status` enum('draft','pending_review','available','pending','adopted','unavailable','rejected') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'draft',
  `shelter_id` int NOT NULL,
  `microchip_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `vaccination_status` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `spayed_neutered` tinyint(1) DEFAULT NULL,
  `house_trained` tinyint(1) DEFAULT NULL,
  `good_with_kids` tinyint(1) DEFAULT NULL,
  `good_with_pets` tinyint(1) DEFAULT NULL,
  `energy_level` enum('low','medium','high') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_by` int NOT NULL,
  `version` int NOT NULL DEFAULT '1',
  `last_modified_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_pets_id` (`id`),
  KEY `ix_pets_species` (`species`),
  KEY `ix_pets_status` (`status`),
  KEY `ix_pets_created_by` (`created_by`),
  KEY `ix_pets_last_modified_by` (`last_modified_by`),
  KEY `idx_pets_status` (`status`),
  KEY `idx_pets_shelter_id` (`shelter_id`),
  CONSTRAINT `fk_pets_shelter_id_users` FOREIGN KEY (`shelter_id`) REFERENCES `users` (`id`),
  CONSTRAINT `pets_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  CONSTRAINT `pets_ibfk_2` FOREIGN KEY (`last_modified_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pets`
--

LOCK TABLES `pets` WRITE;
/*!40000 ALTER TABLE `pets` DISABLE KEYS */;
INSERT INTO `pets` VALUES (1,'小白','dog','柴犬',2023,8,'male','medium',10.5,'白色','活潑可愛的小柴犬，喜歡和人玩耍，非常親人。已完成基本訓練，會坐下、握手等指令。','已完成所有疫苗接種，健康狀況良好','溫和親人，適合家庭飼養，與小孩相處融洽',NULL,3000.00,'adopted',2,NULL,'已完成',1,1,1,1,'high','2025-11-16 15:29:58','2025-11-28 19:18:10',2,1,NULL),(2,'橘子','cat','橘貓',2024,5,'male','medium',4.5,'橘色','可愛的小橘貓，喜歡曬太陽和睡覺。個性溫和，會用貓砂，適合新手飼養。','已結紮，疫苗齊全','親人不怕生，喜歡被撫摸',NULL,2000.00,'available',2,NULL,'已完成',1,1,1,1,'medium','2025-11-16 15:29:58','2025-11-17 13:03:58',2,1,NULL),(3,'lucky','dog','黃金獵犬',2025,2,'female','large',28,'金黃色','年輕的黃金獵犬，很活潑喜歡散步和游泳。','健康良好，已完成所有疫苗','穩重溫和，非常適合有小孩的家庭',NULL,4000.00,'available',2,NULL,'已完成',1,1,1,1,'medium','2025-11-16 15:29:58','2025-11-17 13:41:39',2,1,NULL),(4,'小黑','cat','米克斯',2025,3,'female','small',3.2,'黑色','年輕活潑的小黑貓，眼睛大大的很可愛。喜歡玩逗貓棒，晚上會陪主人睡覺。','已完成基礎疫苗，準備結紮','活潑好動，適合喜歡互動的家庭',NULL,1500.00,'available',2,NULL,'進行中',0,1,1,1,'high','2025-11-16 15:29:58','2025-11-17 13:03:58',2,1,NULL),(5,'多多','dog','貴賓犬',2021,11,'male','small',5.8,'咖啡色','聰明的貴賓犬，會很多才藝。非常黏人，適合需要陪伴的家庭。毛髮需要定期修剪。','健康狀況良好，已結紮','聰明易訓練，喜歡學習新把戲','需定期美容',3500.00,'available',2,NULL,'已完成',1,1,1,1,'medium','2025-11-16 15:29:58','2025-11-17 13:03:58',2,1,NULL),(6,'阿福','dog','台灣土狗',2023,11,'male','medium',15,'黃色帶黑','忠心的台灣土狗，曾經是流浪犬，現在非常珍惜有家的機會。個性穩重，適合看家。','已完成體檢和疫苗，健康良好','忠誠護主，需要有經驗的飼主',NULL,2500.00,'available',3,NULL,'已完成',1,1,1,0,'medium','2025-11-16 15:29:58','2025-11-17 13:03:58',3,1,NULL),(7,'咪咪','cat','波斯貓',2023,11,'female','medium',4,'白色','優雅的波斯貓，毛髮柔軟蓬鬆。喜歡安靜的環境，是完美的室內寵物。','已結紮，疫苗完整','個性溫和安靜，適合公寓飼養','需每日梳毛',3000.00,'available',3,NULL,'已完成',1,1,1,1,'low','2025-11-16 15:29:58','2025-11-17 13:03:58',3,1,NULL),(8,'布丁','dog','柯基犬',2024,8,'female','small',11,'棕白相間','可愛的短腿柯基，走路搖搖擺擺超可愛。個性活潑開朗，是開心果一枚。','健康活潑，疫苗齊全','活潑好動，需要足夠的運動空間',NULL,4500.00,'available',3,NULL,'已完成',1,1,1,1,'high','2025-11-16 15:29:58','2025-11-17 13:03:58',3,1,NULL),(9,'虎斑','cat','美國短毛貓',2022,5,'male','medium',5.5,'銀色虎斑','帥氣的虎斑貓，有著漂亮的條紋。個性獨立但也喜歡撒嬌，是理想的伴侶。','已結紮，健康檢查良好','獨立自主，適合上班族',NULL,2500.00,'available',3,NULL,'已完成',1,1,1,1,'medium','2025-11-16 15:29:58','2025-11-17 13:03:58',3,1,NULL),(10,'巧克力','dog','拉布拉多',2023,5,'male','large',30,'巧克力色','溫柔的大狗狗，喜歡游泳和戶外活動。對人非常友善，是最佳的家庭寵物。','健康狀況優良，已完成所有疫苗','溫和友善，適合有院子的家庭',NULL,4000.00,'available',3,NULL,'已完成',1,1,1,1,'high','2025-11-16 15:29:58','2025-11-17 13:03:58',3,1,NULL),(11,'阿寶','dog','博美',2018,11,'female','small',2.7,'棕色','愛吃、愛睡、愛吃肉，傻傻的','很健康，有定期打疫苗',NULL,NULL,0.00,'available',2,NULL,'True',0,1,1,1,'medium','2025-11-17 09:55:05','2025-11-17 13:03:58',2,1,NULL),(16,'測試','dog','aa',2024,2,'male','medium',2,'aa','aa',NULL,'aa','aa',NULL,'available',2,'11','這裡沒改到嗎',1,1,0,0,'low','2025-11-27 01:18:31','2025-11-27 01:30:54',2,1,NULL);
/*!40000 ALTER TABLE `pets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `post_comments`
--

DROP TABLE IF EXISTS `post_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `post_comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `post_id` int NOT NULL,
  `user_id` int NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_post_comments_post_id` (`post_id`),
  KEY `ix_post_comments_id` (`id`),
  KEY `idx_is_deleted` (`is_deleted`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_post_comments_post_id` (`post_id`),
  KEY `idx_post_comments_post_deleted` (`post_id`,`is_deleted`),
  CONSTRAINT `fk_post_comments_post_id_community_posts` FOREIGN KEY (`post_id`) REFERENCES `community_posts` (`id`),
  CONSTRAINT `fk_post_comments_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `post_comments`
--

LOCK TABLES `post_comments` WRITE;
/*!40000 ALTER TABLE `post_comments` DISABLE KEYS */;
INSERT INTO `post_comments` VALUES (1,3,2,'胖橘好可愛',0,'2025-11-17 14:53:52','2025-11-17 14:53:52'),(2,5,2,'我也想知道！',0,'2025-11-17 15:06:17','2025-11-17 15:06:17'),(3,6,4,'阿寶好可愛✨',0,'2025-11-29 21:25:27','2025-11-29 21:25:27'),(4,6,4,'阿寶好可愛',0,'2025-11-29 21:27:17','2025-11-29 21:27:17'),(5,6,4,'阿寶好可愛',1,'2025-11-29 21:29:59','2025-11-29 21:29:59'),(6,1,4,'可愛',0,'2025-11-30 00:40:01','2025-11-30 00:40:01'),(7,2,4,'好難好難',0,'2025-11-30 17:31:29','2025-11-30 17:31:29'),(8,1,4,'測試',0,'2025-11-30 17:36:46','2025-11-30 17:36:46'),(9,2,4,'通知測試',0,'2025-11-30 18:17:17','2025-11-30 18:17:17'),(10,2,4,'通知',0,'2025-11-30 18:23:45','2025-11-30 18:23:45'),(11,2,4,'final',0,'2025-11-30 18:26:10','2025-11-30 18:26:10'),(12,2,4,'final2',0,'2025-11-30 18:26:47','2025-11-30 18:26:47'),(13,1,4,'test',0,'2025-11-30 18:31:47','2025-11-30 18:31:47');
/*!40000 ALTER TABLE `post_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `post_likes`
--

DROP TABLE IF EXISTS `post_likes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `post_likes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `post_id` int NOT NULL,
  `user_id` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_post_likes_id` (`id`),
  KEY `ix_post_likes_post_id` (`post_id`),
  KEY `ix_post_likes_user_id` (`user_id`),
  KEY `idx_post_likes_post_id` (`post_id`),
  KEY `idx_post_likes_user_post` (`user_id`,`post_id`),
  CONSTRAINT `fk_post_likes_post_id_community_posts` FOREIGN KEY (`post_id`) REFERENCES `community_posts` (`id`),
  CONSTRAINT `fk_post_likes_user_id_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `post_likes`
--

LOCK TABLES `post_likes` WRITE;
/*!40000 ALTER TABLE `post_likes` DISABLE KEYS */;
INSERT INTO `post_likes` VALUES (12,6,2,'2025-11-29 21:56:31'),(13,1,4,'2025-11-30 00:42:01'),(14,2,4,'2025-11-30 18:14:51');
/*!40000 ALTER TABLE `post_likes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `post_photos`
--

DROP TABLE IF EXISTS `post_photos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `post_photos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `post_id` int NOT NULL COMMENT '貼文ID',
  `file_key` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'S3檔案key',
  `display_order` int NOT NULL COMMENT '顯示順序',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_post_photos_id` (`id`),
  KEY `idx_post_id` (`post_id`),
  CONSTRAINT `fk_post_photos_post_id_community_posts` FOREIGN KEY (`post_id`) REFERENCES `community_posts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `post_photos`
--

LOCK TABLES `post_photos` WRITE;
/*!40000 ALTER TABLE `post_photos` DISABLE KEYS */;
INSERT INTO `post_photos` VALUES (9,2,'community/posts/2/a2625acf-b7ad-42c2-9fdc-605183ac84f3.jpg',1,'2025-11-17 10:49:40'),(10,1,'community/posts/1/6bc95e7f-90c3-4b5c-b297-0aafd14ed897.jpg',2,'2025-11-17 10:50:39'),(12,3,'community/posts/3/4cac4632-8971-41db-927c-41d8cdf785af.jpg',3,'2025-11-17 10:55:06'),(13,3,'community/posts/3/086dff3e-c5cc-4786-823e-efec17dbb501.jpg',4,'2025-11-17 10:55:16'),(14,4,'community/posts/4/4c0efd66-3d0b-4a85-96b5-91bb23e61822.jpeg',1,'2025-11-17 10:56:43'),(15,5,'community/posts/5/abcdb519-225e-4ca8-b8a8-b5df7a2482b6.jpg',2,'2025-11-17 10:58:19'),(16,6,'https://pet-adoption-files.s3.amazonaws.com/community/3bc7bb58-32db-4cd1-b604-755b6421d551.jpg?AWSAccessKeyId=AKIAZZDVSOVDPC3CAFX6&Signature=ECXpcZmgV1OA06SItCvpIxmWPnQ%3D&Expires=1765025810',0,'2025-11-29 20:56:50');
/*!40000 ALTER TABLE `post_photos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `post_reports`
--

DROP TABLE IF EXISTS `post_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `post_reports` (
  `id` int NOT NULL AUTO_INCREMENT,
  `post_id` int NOT NULL,
  `reporter_id` int NOT NULL,
  `reason` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_post_reports_id` (`id`),
  KEY `ix_post_reports_post_id` (`post_id`),
  KEY `ix_post_reports_reporter_id` (`reporter_id`),
  CONSTRAINT `post_reports_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `community_posts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `post_reports_ibfk_2` FOREIGN KEY (`reporter_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `post_reports`
--

LOCK TABLES `post_reports` WRITE;
/*!40000 ALTER TABLE `post_reports` DISABLE KEYS */;
INSERT INTO `post_reports` VALUES (1,1,4,'檢舉測試阿阿','2025-11-30 17:40:28'),(2,2,4,'測試2','2025-11-30 17:46:44'),(3,3,4,'檢舉通知測試','2025-11-30 17:56:04');
/*!40000 ALTER TABLE `post_reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_favorites`
--

DROP TABLE IF EXISTS `user_favorites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_favorites` (
  `user_id` int NOT NULL,
  `pet_id` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`pet_id`),
  KEY `fk_user_favorites_pet_id_pets` (`pet_id`),
  KEY `idx_user_favorites_created_at` (`created_at`),
  CONSTRAINT `fk_user_favorites_pet_id_pets` FOREIGN KEY (`pet_id`) REFERENCES `pets` (`id`),
  CONSTRAINT `fk_user_favorites_user_id_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_favorites`
--

LOCK TABLES `user_favorites` WRITE;
/*!40000 ALTER TABLE `user_favorites` DISABLE KEYS */;
INSERT INTO `user_favorites` VALUES (1,1,'2025-11-17 11:17:02'),(6,1,'2025-11-25 12:01:40'),(4,3,'2025-11-25 12:02:35'),(4,1,'2025-11-27 00:25:55');
/*!40000 ALTER TABLE `user_favorites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role` enum('admin','adopter','shelter') COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT NULL,
  `address_line1` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin@gmail.com','$2b$12$GDxmwHGbeECahhTSnOVd3OyI8IEbHBm/mgWzV/lW2LTJcPWATNmkC','管理員',NULL,'admin',1,0,NULL,'2025-11-16 15:06:41','2025-11-16 15:14:08'),(2,'shelter@gmail.com','$2b$12$cu7siScBqlHwP8uYwaO2s.Sq6ech6/DMARa.rgBx38DGvndY9Zfq.','毛星球之家',NULL,'shelter',1,0,NULL,'2025-11-16 15:08:10','2025-11-18 06:21:47'),(3,'dogcat@gmail.com','$2b$12$OhIJhcivWM.Ogl0LXUxviOu0nx5d5eEYSHPQK1Qb7Dmi80YDIFZ1m','汪喵星球',NULL,'shelter',1,0,NULL,'2025-11-16 15:11:30','2025-11-17 15:33:13'),(4,'lin@gmail.com','$2b$12$xL3lET5F2RcQDzHPwhLedOCHGM7GE8m5gFUECstR5dg3OdZ.TsEju','林小毛','0911222333','adopter',1,0,'新北市板橋區','2025-11-17 03:06:59','2025-11-26 15:52:42'),(5,'test_v2_auth@example.com','$2b$12$FhEt5YcID.GRYxJELSfDMODjKWmd1wB5k6zk/XSo9OMTa2GTkKsp6','V2 Auth User',NULL,'adopter',1,0,NULL,'2025-11-24 17:25:56','2025-11-24 17:25:56'),(6,'v2test@example.com','$2b$12$UuD4txmNsCWpbKAFEaZyAeZXCQl00UN6N95ws4fXMEsS317nMet1i','V2 Test User','0922-333-444','adopter',1,0,'New Taipei City, Banqiao District, Test Road 789','2025-11-25 03:58:24','2025-11-26 15:50:15'),(7,'chen@gmail.com','$2b$12$zwVkB4IaP0mAUZ.WZOc0c./erE52YjxZGGxoqeuHS3nPFN41mMo.O','陳小毛',NULL,'adopter',1,0,NULL,'2025-11-26 15:53:38','2025-11-26 15:53:38'),(8,'hsu@gmail.com','$2b$12$EYjF7HeU6w49TP1wZLTB5uxqnIi0uMNdLzxoS2tb74eDP5TNvfQkm','許小毛',NULL,'adopter',1,0,NULL,'2025-11-30 15:07:44','2025-11-30 15:07:44');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'pet_adoption'
--

--
-- Dumping routines for database 'pet_adoption'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-01 22:15:23
