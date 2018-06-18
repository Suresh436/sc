-- MySQL dump 10.13  Distrib 5.7.22, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: sync4life
-- ------------------------------------------------------
-- Server version	5.7.22-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `direct_messages`
--

DROP TABLE IF EXISTS `direct_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `direct_messages` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `message` text,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `direct_messages`
--

LOCK TABLES `direct_messages` WRITE;
/*!40000 ALTER TABLE `direct_messages` DISABLE KEYS */;
/*!40000 ALTER TABLE `direct_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insta_user_contact`
--

DROP TABLE IF EXISTS `insta_user_contact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `insta_user_contact` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `total_followers` bigint(20) DEFAULT NULL,
  `total_followings` bigint(20) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `total_likes` bigint(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insta_user_contact`
--

LOCK TABLES `insta_user_contact` WRITE;
/*!40000 ALTER TABLE `insta_user_contact` DISABLE KEYS */;
/*!40000 ALTER TABLE `insta_user_contact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment_details`
--

DROP TABLE IF EXISTS `payment_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payment_details` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `subscription_id` int(11) DEFAULT NULL,
  `amount` varchar(45) DEFAULT NULL,
  `payment_status` varchar(45) DEFAULT NULL,
  `payment_date` datetime DEFAULT NULL,
  `billing_aggrement_id` varchar(45) DEFAULT NULL,
  `payment_token` varchar(45) DEFAULT NULL,
  `payment_mode` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_details`
--

LOCK TABLES `payment_details` WRITE;
/*!40000 ALTER TABLE `payment_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payments` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `payment_detail_id` bigint(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proxy_ips`
--

DROP TABLE IF EXISTS `proxy_ips`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `proxy_ips` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip_address` varchar(45) NOT NULL,
  `port` int(10) NOT NULL,
  `username` varchar(45) DEFAULT NULL,
  `password` varchar(45) DEFAULT NULL,
  `country` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proxy_ips`
--

LOCK TABLES `proxy_ips` WRITE;
/*!40000 ALTER TABLE `proxy_ips` DISABLE KEYS */;
INSERT INTO `proxy_ips` VALUES (1,'104.171.146.204',60000,'wolfgramm','rN7rdcnx5W','US'),(2,'104.171.146.205',60000,'wolfgramm','rN7rdcnx5W','US'),(3,'104.171.146.206',60000,'wolfgramm','rN7rdcnx5W','US'),(4,'104.171.146.207',60000,'wolfgramm','rN7rdcnx5W','US'),(5,'104.171.146.208',60000,'wolfgramm','rN7rdcnx5W','US'),(6,'104.171.146.209',60000,'wolfgramm','rN7rdcnx5W','US'),(7,'104.171.146.210',60000,'wolfgramm','rN7rdcnx5W','US'),(8,'104.171.146.211',60000,'wolfgramm','rN7rdcnx5W','US'),(9,'104.171.146.212',60000,'wolfgramm','rN7rdcnx5W','US'),(10,'104.171.146.213',60000,'wolfgramm','rN7rdcnx5W','US'),(11,'104.171.146.214',60000,'wolfgramm','rN7rdcnx5W','US'),(12,'104.171.146.215',60000,'wolfgramm','rN7rdcnx5W','US'),(13,'104.171.146.216',60000,'wolfgramm','rN7rdcnx5W','US'),(14,'104.171.146.217',60000,'wolfgramm','rN7rdcnx5W','US'),(15,'104.171.146.218',60000,'wolfgramm','rN7rdcnx5W','US'),(16,'104.171.146.219',60000,'wolfgramm','rN7rdcnx5W','US'),(17,'104.171.146.220',60000,'wolfgramm','rN7rdcnx5W','US'),(18,'104.171.146.221',60000,'wolfgramm','rN7rdcnx5W','US'),(19,'104.171.146.222',60000,'wolfgramm','rN7rdcnx5W','US'),(20,'104.171.146.223',60000,'wolfgramm','rN7rdcnx5W','US'),(21,'104.171.146.224',60000,'wolfgramm','rN7rdcnx5W','US'),(22,'104.171.146.225',60000,'wolfgramm','rN7rdcnx5W','US'),(23,'104.171.146.226',60000,'wolfgramm','rN7rdcnx5W','US'),(24,'104.171.146.227',60000,'wolfgramm','rN7rdcnx5W','US'),(25,'104.171.146.228',60000,'wolfgramm','rN7rdcnx5W','US'),(26,'104.171.146.229',60000,'wolfgramm','rN7rdcnx5W','US'),(27,'104.171.146.230',60000,'wolfgramm','rN7rdcnx5W','US'),(28,'104.171.146.231',60000,'wolfgramm','rN7rdcnx5W','US'),(29,'104.171.146.232',60000,'wolfgramm','rN7rdcnx5W','US'),(30,'104.171.146.234',60000,'wolfgramm','rN7rdcnx5W','US'),(31,'104.171.146.235',60000,'wolfgramm','rN7rdcnx5W','US'),(32,'104.171.146.236',60000,'wolfgramm','rN7rdcnx5W','US'),(33,'104.171.146.237',60000,'wolfgramm','rN7rdcnx5W','US'),(34,'104.171.146.238',60000,'wolfgramm','rN7rdcnx5W','US'),(35,'104.171.146.239',60000,'wolfgramm','rN7rdcnx5W','US'),(36,'104.171.146.240',60000,'wolfgramm','rN7rdcnx5W','US'),(37,'104.171.146.241',60000,'wolfgramm','rN7rdcnx5W','US'),(38,'104.171.146.242',60000,'wolfgramm','rN7rdcnx5W','US'),(39,'104.171.146.243',60000,'wolfgramm','rN7rdcnx5W','US'),(40,'104.171.146.244',60000,'wolfgramm','rN7rdcnx5W','US'),(41,'104.171.146.245',60000,'wolfgramm','rN7rdcnx5W','US'),(42,'104.171.146.246',60000,'wolfgramm','rN7rdcnx5W','US'),(43,'104.171.146.247',60000,'wolfgramm','rN7rdcnx5W','US'),(44,'104.171.146.248',60000,'wolfgramm','rN7rdcnx5W','US'),(45,'104.171.146.249',60000,'wolfgramm','rN7rdcnx5W','US'),(46,'104.171.146.250',60000,'wolfgramm','rN7rdcnx5W','US'),(47,'104.171.146.251',60000,'wolfgramm','rN7rdcnx5W','US'),(48,'104.171.146.252',60000,'wolfgramm','rN7rdcnx5W','US'),(49,'104.171.146.253',60000,'wolfgramm','rN7rdcnx5W','US'),(50,'104.171.146.254',60000,'wolfgramm','rN7rdcnx5W','US'),(51,'104.171.154.2',60000,'wolfgramm','rN7rdcnx5W','US'),(52,'104.171.154.3',60000,'wolfgramm','rN7rdcnx5W','US'),(53,'104.171.154.4',60000,'wolfgramm','rN7rdcnx5W','US'),(54,'104.171.154.5',60000,'wolfgramm','rN7rdcnx5W','US'),(55,'104.171.154.6',60000,'wolfgramm','rN7rdcnx5W','US'),(56,'104.171.154.7',60000,'wolfgramm','rN7rdcnx5W','US'),(57,'104.171.154.8',60000,'wolfgramm','rN7rdcnx5W','US'),(58,'104.171.154.9',60000,'wolfgramm','rN7rdcnx5W','US'),(59,'104.171.154.10',60000,'wolfgramm','rN7rdcnx5W','US'),(60,'104.171.154.11',60000,'wolfgramm','rN7rdcnx5W','US'),(61,'104.171.154.12',60000,'wolfgramm','rN7rdcnx5W','US'),(62,'104.171.154.13',60000,'wolfgramm','rN7rdcnx5W','US'),(63,'104.171.154.14',60000,'wolfgramm','rN7rdcnx5W','US'),(64,'104.171.154.15',60000,'wolfgramm','rN7rdcnx5W','US'),(65,'104.171.154.16',60000,'wolfgramm','rN7rdcnx5W','US'),(66,'104.171.154.17',60000,'wolfgramm','rN7rdcnx5W','US'),(67,'104.171.154.18',60000,'wolfgramm','rN7rdcnx5W','US'),(68,'104.171.154.19',60000,'wolfgramm','rN7rdcnx5W','US'),(69,'104.171.154.20',60000,'wolfgramm','rN7rdcnx5W','US'),(70,'104.171.154.21',60000,'wolfgramm','rN7rdcnx5W','US'),(71,'104.171.154.22',60000,'wolfgramm','rN7rdcnx5W','US'),(72,'104.171.154.23',60000,'wolfgramm','rN7rdcnx5W','US'),(73,'104.171.154.24',60000,'wolfgramm','rN7rdcnx5W','US'),(74,'104.171.154.25',60000,'wolfgramm','rN7rdcnx5W','US'),(75,'104.171.154.26',60000,'wolfgramm','rN7rdcnx5W','US'),(76,'104.171.154.27',60000,'wolfgramm','rN7rdcnx5W','US'),(77,'104.171.154.28',60000,'wolfgramm','rN7rdcnx5W','US'),(78,'104.171.154.29',60000,'wolfgramm','rN7rdcnx5W','US'),(79,'104.171.154.30',60000,'wolfgramm','rN7rdcnx5W','US'),(80,'104.171.154.31',60000,'wolfgramm','rN7rdcnx5W','US'),(81,'104.171.154.32',60000,'wolfgramm','rN7rdcnx5W','US'),(82,'104.171.154.33',60000,'wolfgramm','rN7rdcnx5W','US'),(83,'104.171.154.34',60000,'wolfgramm','rN7rdcnx5W','US'),(84,'104.171.154.35',60000,'wolfgramm','rN7rdcnx5W','US'),(85,'104.171.154.36',60000,'wolfgramm','rN7rdcnx5W','US'),(86,'104.171.154.37',60000,'wolfgramm','rN7rdcnx5W','US'),(87,'104.171.154.38',60000,'wolfgramm','rN7rdcnx5W','US'),(88,'104.171.154.39',60000,'wolfgramm','rN7rdcnx5W','US'),(89,'104.171.154.40',60000,'wolfgramm','rN7rdcnx5W','US'),(90,'104.171.154.41',60000,'wolfgramm','rN7rdcnx5W','US'),(91,'104.171.154.42',60000,'wolfgramm','rN7rdcnx5W','US'),(92,'104.171.154.43',60000,'wolfgramm','rN7rdcnx5W','US'),(93,'104.171.154.44',60000,'wolfgramm','rN7rdcnx5W','US'),(94,'104.171.154.45',60000,'wolfgramm','rN7rdcnx5W','US'),(95,'104.171.154.46',60000,'wolfgramm','rN7rdcnx5W','US'),(96,'104.171.154.47',60000,'wolfgramm','rN7rdcnx5W','US'),(97,'104.171.154.48',60000,'wolfgramm','rN7rdcnx5W','US'),(98,'104.171.154.49',60000,'wolfgramm','rN7rdcnx5W','US'),(99,'104.171.154.50',60000,'wolfgramm','rN7rdcnx5W','US'),(100,'104.171.154.51',60000,'wolfgramm','rN7rdcnx5W','US'),(101,'104.171.154.52',60000,'wolfgramm','rN7rdcnx5W','US'),(102,'104.171.154.53',60000,'wolfgramm','rN7rdcnx5W','US'),(103,'104.171.154.54',60000,'wolfgramm','rN7rdcnx5W','US'),(104,'104.171.154.55',60000,'wolfgramm','rN7rdcnx5W','US'),(105,'104.171.154.56',60000,'wolfgramm','rN7rdcnx5W','US'),(106,'104.171.154.57',60000,'wolfgramm','rN7rdcnx5W','US'),(107,'104.171.154.58',60000,'wolfgramm','rN7rdcnx5W','US'),(108,'104.171.154.59',60000,'wolfgramm','rN7rdcnx5W','US'),(109,'104.171.154.60',60000,'wolfgramm','rN7rdcnx5W','US'),(110,'104.171.154.61',60000,'wolfgramm','rN7rdcnx5W','US'),(111,'104.171.154.62',60000,'wolfgramm','rN7rdcnx5W','US'),(112,'104.171.154.63',60000,'wolfgramm','rN7rdcnx5W','US'),(113,'104.171.154.64',60000,'wolfgramm','rN7rdcnx5W','US'),(114,'104.171.154.65',60000,'wolfgramm','rN7rdcnx5W','US'),(115,'104.171.154.66',60000,'wolfgramm','rN7rdcnx5W','US'),(116,'104.171.154.67',60000,'wolfgramm','rN7rdcnx5W','US'),(117,'104.171.154.68',60000,'wolfgramm','rN7rdcnx5W','US'),(118,'104.171.154.69',60000,'wolfgramm','rN7rdcnx5W','US'),(119,'104.171.154.70',60000,'wolfgramm','rN7rdcnx5W','US'),(120,'104.171.154.71',60000,'wolfgramm','rN7rdcnx5W','US'),(121,'104.171.154.72',60000,'wolfgramm','rN7rdcnx5W','US'),(122,'104.171.154.73',60000,'wolfgramm','rN7rdcnx5W','US'),(123,'104.171.154.74',60000,'wolfgramm','rN7rdcnx5W','US'),(124,'104.171.154.75',60000,'wolfgramm','rN7rdcnx5W','US'),(125,'104.171.154.76',60000,'wolfgramm','rN7rdcnx5W','US'),(126,'104.171.154.77',60000,'wolfgramm','rN7rdcnx5W','US'),(127,'104.171.154.78',60000,'wolfgramm','rN7rdcnx5W','US'),(128,'104.171.154.79',60000,'wolfgramm','rN7rdcnx5W','US'),(129,'104.171.154.80',60000,'wolfgramm','rN7rdcnx5W','US'),(130,'104.171.154.81',60000,'wolfgramm','rN7rdcnx5W','US'),(131,'104.171.154.82',60000,'wolfgramm','rN7rdcnx5W','US'),(132,'104.171.154.83',60000,'wolfgramm','rN7rdcnx5W','US'),(133,'104.171.154.84',60000,'wolfgramm','rN7rdcnx5W','US'),(134,'104.171.154.85',60000,'wolfgramm','rN7rdcnx5W','US'),(135,'104.171.154.86',60000,'wolfgramm','rN7rdcnx5W','US'),(136,'104.171.154.87',60000,'wolfgramm','rN7rdcnx5W','US'),(137,'104.171.154.88',60000,'wolfgramm','rN7rdcnx5W','US'),(138,'104.171.154.89',60000,'wolfgramm','rN7rdcnx5W','US'),(139,'104.171.154.90',60000,'wolfgramm','rN7rdcnx5W','US'),(140,'104.171.154.91',60000,'wolfgramm','rN7rdcnx5W','US'),(141,'104.171.154.92',60000,'wolfgramm','rN7rdcnx5W','US'),(142,'104.171.154.93',60000,'wolfgramm','rN7rdcnx5W','US'),(143,'104.171.154.94',60000,'wolfgramm','rN7rdcnx5W','US'),(144,'104.171.154.95',60000,'wolfgramm','rN7rdcnx5W','US'),(145,'104.171.154.96',60000,'wolfgramm','rN7rdcnx5W','US'),(146,'104.171.154.97',60000,'wolfgramm','rN7rdcnx5W','US'),(147,'104.171.154.98',60000,'wolfgramm','rN7rdcnx5W','US'),(148,'104.171.154.99',60000,'wolfgramm','rN7rdcnx5W','US'),(149,'104.171.154.100',60000,'wolfgramm','rN7rdcnx5W','US'),(150,'104.171.154.101',60000,'wolfgramm','rN7rdcnx5W','US'),(151,'104.171.154.102',60000,'wolfgramm','rN7rdcnx5W','US'),(152,'104.171.154.103',60000,'wolfgramm','rN7rdcnx5W','US'),(153,'104.171.154.104',60000,'wolfgramm','rN7rdcnx5W','US'),(154,'104.171.154.105',60000,'wolfgramm','rN7rdcnx5W','US'),(155,'104.171.154.106',60000,'wolfgramm','rN7rdcnx5W','US'),(156,'104.171.154.107',60000,'wolfgramm','rN7rdcnx5W','US'),(157,'104.171.154.108',60000,'wolfgramm','rN7rdcnx5W','US'),(158,'104.171.154.109',60000,'wolfgramm','rN7rdcnx5W','US'),(159,'104.171.154.110',60000,'wolfgramm','rN7rdcnx5W','US'),(160,'104.171.154.111',60000,'wolfgramm','rN7rdcnx5W','US'),(161,'104.171.154.112',60000,'wolfgramm','rN7rdcnx5W','US'),(162,'104.171.154.113',60000,'wolfgramm','rN7rdcnx5W','US'),(163,'104.171.154.114',60000,'wolfgramm','rN7rdcnx5W','US'),(164,'104.171.154.115',60000,'wolfgramm','rN7rdcnx5W','US'),(165,'104.171.154.116',60000,'wolfgramm','rN7rdcnx5W','US'),(166,'104.171.154.117',60000,'wolfgramm','rN7rdcnx5W','US'),(167,'104.171.154.118',60000,'wolfgramm','rN7rdcnx5W','US'),(168,'104.171.154.119',60000,'wolfgramm','rN7rdcnx5W','US'),(169,'104.171.154.120',60000,'wolfgramm','rN7rdcnx5W','US'),(170,'104.171.154.121',60000,'wolfgramm','rN7rdcnx5W','US'),(171,'104.171.154.122',60000,'wolfgramm','rN7rdcnx5W','US'),(172,'104.171.154.123',60000,'wolfgramm','rN7rdcnx5W','US'),(173,'104.171.154.124',60000,'wolfgramm','rN7rdcnx5W','US'),(174,'104.171.154.125',60000,'wolfgramm','rN7rdcnx5W','US'),(175,'104.171.154.126',60000,'wolfgramm','rN7rdcnx5W','US'),(176,'104.171.154.127',60000,'wolfgramm','rN7rdcnx5W','US'),(177,'104.171.154.128',60000,'wolfgramm','rN7rdcnx5W','US'),(178,'104.171.154.129',60000,'wolfgramm','rN7rdcnx5W','US'),(179,'104.171.154.130',60000,'wolfgramm','rN7rdcnx5W','US'),(180,'104.171.154.131',60000,'wolfgramm','rN7rdcnx5W','US'),(181,'104.171.154.132',60000,'wolfgramm','rN7rdcnx5W','US'),(182,'104.171.154.133',60000,'wolfgramm','rN7rdcnx5W','US'),(183,'104.171.154.134',60000,'wolfgramm','rN7rdcnx5W','US'),(184,'104.171.154.135',60000,'wolfgramm','rN7rdcnx5W','US'),(185,'104.171.154.136',60000,'wolfgramm','rN7rdcnx5W','US'),(186,'104.171.154.137',60000,'wolfgramm','rN7rdcnx5W','US'),(187,'104.171.154.138',60000,'wolfgramm','rN7rdcnx5W','US'),(188,'104.171.154.139',60000,'wolfgramm','rN7rdcnx5W','US'),(189,'104.171.154.140',60000,'wolfgramm','rN7rdcnx5W','US'),(190,'104.171.154.141',60000,'wolfgramm','rN7rdcnx5W','US'),(191,'104.171.154.142',60000,'wolfgramm','rN7rdcnx5W','US'),(192,'104.171.154.143',60000,'wolfgramm','rN7rdcnx5W','US'),(193,'104.171.154.144',60000,'wolfgramm','rN7rdcnx5W','US'),(194,'104.171.154.145',60000,'wolfgramm','rN7rdcnx5W','US'),(195,'104.171.154.146',60000,'wolfgramm','rN7rdcnx5W','US'),(196,'104.171.154.147',60000,'wolfgramm','rN7rdcnx5W','US'),(197,'104.171.154.148',60000,'wolfgramm','rN7rdcnx5W','US'),(198,'104.171.154.149',60000,'wolfgramm','rN7rdcnx5W','US'),(199,'104.171.154.150',60000,'wolfgramm','rN7rdcnx5W','US'),(200,'104.171.154.151',60000,'wolfgramm','rN7rdcnx5W','US'),(201,'104.171.154.152',60000,'wolfgramm','rN7rdcnx5W','US'),(202,'104.171.154.153',60000,'wolfgramm','rN7rdcnx5W','US'),(203,'104.171.154.154',60000,'wolfgramm','rN7rdcnx5W','US'),(204,'104.171.154.155',60000,'wolfgramm','rN7rdcnx5W','US'),(205,'104.171.154.156',60000,'wolfgramm','rN7rdcnx5W','US'),(206,'104.171.154.157',60000,'wolfgramm','rN7rdcnx5W','US'),(207,'104.171.154.158',60000,'wolfgramm','rN7rdcnx5W','US'),(208,'104.171.154.159',60000,'wolfgramm','rN7rdcnx5W','US'),(209,'104.171.154.160',60000,'wolfgramm','rN7rdcnx5W','US'),(210,'104.171.154.161',60000,'wolfgramm','rN7rdcnx5W','US'),(211,'104.171.154.162',60000,'wolfgramm','rN7rdcnx5W','US'),(212,'104.171.154.163',60000,'wolfgramm','rN7rdcnx5W','US'),(213,'104.171.154.164',60000,'wolfgramm','rN7rdcnx5W','US'),(214,'104.171.154.165',60000,'wolfgramm','rN7rdcnx5W','US'),(215,'104.171.154.166',60000,'wolfgramm','rN7rdcnx5W','US'),(216,'104.171.154.167',60000,'wolfgramm','rN7rdcnx5W','US'),(217,'104.171.154.168',60000,'wolfgramm','rN7rdcnx5W','US'),(218,'104.171.154.169',60000,'wolfgramm','rN7rdcnx5W','US'),(219,'104.171.154.170',60000,'wolfgramm','rN7rdcnx5W','US'),(220,'104.171.154.171',60000,'wolfgramm','rN7rdcnx5W','US'),(221,'104.171.154.172',60000,'wolfgramm','rN7rdcnx5W','US'),(222,'104.171.154.173',60000,'wolfgramm','rN7rdcnx5W','US'),(223,'104.171.154.174',60000,'wolfgramm','rN7rdcnx5W','US'),(224,'104.171.154.175',60000,'wolfgramm','rN7rdcnx5W','US'),(225,'104.171.154.176',60000,'wolfgramm','rN7rdcnx5W','US'),(226,'104.171.154.177',60000,'wolfgramm','rN7rdcnx5W','US'),(227,'104.171.154.178',60000,'wolfgramm','rN7rdcnx5W','US'),(228,'104.171.154.179',60000,'wolfgramm','rN7rdcnx5W','US'),(229,'104.171.154.180',60000,'wolfgramm','rN7rdcnx5W','US'),(230,'104.171.154.181',60000,'wolfgramm','rN7rdcnx5W','US'),(231,'104.171.154.182',60000,'wolfgramm','rN7rdcnx5W','US'),(232,'104.171.154.183',60000,'wolfgramm','rN7rdcnx5W','US'),(233,'104.171.154.184',60000,'wolfgramm','rN7rdcnx5W','US'),(234,'104.171.154.185',60000,'wolfgramm','rN7rdcnx5W','US'),(235,'104.171.154.186',60000,'wolfgramm','rN7rdcnx5W','US'),(236,'104.171.154.187',60000,'wolfgramm','rN7rdcnx5W','US'),(237,'104.171.154.188',60000,'wolfgramm','rN7rdcnx5W','US'),(238,'104.171.154.189',60000,'wolfgramm','rN7rdcnx5W','US'),(239,'104.171.154.190',60000,'wolfgramm','rN7rdcnx5W','US'),(240,'104.171.154.191',60000,'wolfgramm','rN7rdcnx5W','US'),(241,'104.171.154.192',60000,'wolfgramm','rN7rdcnx5W','US'),(242,'104.171.154.193',60000,'wolfgramm','rN7rdcnx5W','US'),(243,'104.171.154.194',60000,'wolfgramm','rN7rdcnx5W','US'),(244,'104.171.154.195',60000,'wolfgramm','rN7rdcnx5W','US'),(245,'104.171.154.196',60000,'wolfgramm','rN7rdcnx5W','US'),(246,'104.171.154.197',60000,'wolfgramm','rN7rdcnx5W','US'),(247,'104.171.154.198',60000,'wolfgramm','rN7rdcnx5W','US'),(248,'104.171.154.199',60000,'wolfgramm','rN7rdcnx5W','US'),(249,'104.171.154.200',60000,'wolfgramm','rN7rdcnx5W','US'),(250,'104.171.154.201',60000,'wolfgramm','rN7rdcnx5W','US'),(251,'104.171.154.202',60000,'wolfgramm','rN7rdcnx5W','US'),(252,'104.171.154.203',60000,'wolfgramm','rN7rdcnx5W','US'),(253,'104.171.154.204',60000,'wolfgramm','rN7rdcnx5W','US'),(254,'104.171.154.205',60000,'wolfgramm','rN7rdcnx5W','US'),(255,'104.171.154.206',60000,'wolfgramm','rN7rdcnx5W','US'),(256,'104.171.154.207',60000,'wolfgramm','rN7rdcnx5W','US'),(257,'104.171.154.208',60000,'wolfgramm','rN7rdcnx5W','US'),(258,'104.171.154.209',60000,'wolfgramm','rN7rdcnx5W','US'),(259,'104.171.154.210',60000,'wolfgramm','rN7rdcnx5W','US'),(260,'104.171.154.211',60000,'wolfgramm','rN7rdcnx5W','US'),(261,'104.171.154.212',60000,'wolfgramm','rN7rdcnx5W','US'),(262,'104.171.154.213',60000,'wolfgramm','rN7rdcnx5W','US'),(263,'104.171.154.214',60000,'wolfgramm','rN7rdcnx5W','US'),(264,'104.171.154.215',60000,'wolfgramm','rN7rdcnx5W','US'),(265,'104.171.154.216',60000,'wolfgramm','rN7rdcnx5W','US'),(266,'104.171.154.217',60000,'wolfgramm','rN7rdcnx5W','US'),(267,'104.171.154.218',60000,'wolfgramm','rN7rdcnx5W','US'),(268,'104.171.154.219',60000,'wolfgramm','rN7rdcnx5W','US'),(269,'104.171.154.220',60000,'wolfgramm','rN7rdcnx5W','US'),(270,'104.171.154.221',60000,'wolfgramm','rN7rdcnx5W','US'),(271,'104.171.154.222',60000,'wolfgramm','rN7rdcnx5W','US'),(272,'104.171.154.223',60000,'wolfgramm','rN7rdcnx5W','US'),(273,'104.171.154.224',60000,'wolfgramm','rN7rdcnx5W','US'),(274,'104.171.154.225',60000,'wolfgramm','rN7rdcnx5W','US'),(275,'104.171.154.226',60000,'wolfgramm','rN7rdcnx5W','US'),(276,'104.171.154.227',60000,'wolfgramm','rN7rdcnx5W','US'),(277,'104.171.154.228',60000,'wolfgramm','rN7rdcnx5W','US'),(278,'104.171.154.229',60000,'wolfgramm','rN7rdcnx5W','US'),(279,'104.171.154.230',60000,'wolfgramm','rN7rdcnx5W','US'),(280,'104.171.154.231',60000,'wolfgramm','rN7rdcnx5W','US'),(281,'104.171.154.232',60000,'wolfgramm','rN7rdcnx5W','US'),(282,'104.171.154.233',60000,'wolfgramm','rN7rdcnx5W','US'),(283,'104.171.154.234',60000,'wolfgramm','rN7rdcnx5W','US'),(284,'104.171.154.235',60000,'wolfgramm','rN7rdcnx5W','US'),(285,'104.171.154.236',60000,'wolfgramm','rN7rdcnx5W','US'),(286,'104.171.154.237',60000,'wolfgramm','rN7rdcnx5W','US'),(287,'104.171.154.238',60000,'wolfgramm','rN7rdcnx5W','US'),(288,'104.171.154.239',60000,'wolfgramm','rN7rdcnx5W','US'),(289,'104.171.154.240',60000,'wolfgramm','rN7rdcnx5W','US'),(290,'104.171.154.241',60000,'wolfgramm','rN7rdcnx5W','US'),(291,'104.171.154.242',60000,'wolfgramm','rN7rdcnx5W','US'),(292,'104.171.154.243',60000,'wolfgramm','rN7rdcnx5W','US'),(293,'104.171.154.244',60000,'wolfgramm','rN7rdcnx5W','US'),(294,'104.171.154.245',60000,'wolfgramm','rN7rdcnx5W','US'),(295,'104.171.154.246',60000,'wolfgramm','rN7rdcnx5W','US'),(296,'104.171.154.247',60000,'wolfgramm','rN7rdcnx5W','US'),(297,'104.171.154.248',60000,'wolfgramm','rN7rdcnx5W','US'),(298,'104.171.154.249',60000,'wolfgramm','rN7rdcnx5W','US'),(299,'104.171.154.250',60000,'wolfgramm','rN7rdcnx5W','US'),(300,'104.171.154.251',60000,'wolfgramm','rN7rdcnx5W','US');
/*!40000 ALTER TABLE `proxy_ips` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `settings` (
  `id` bigint(20) NOT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  `speed` varchar(45) DEFAULT NULL,
  `follow_limit` varchar(45) DEFAULT NULL,
  `follow_private_accounts` varchar(45) DEFAULT NULL,
  `has_profile_pictures` varchar(45) DEFAULT NULL,
  `only_bussiness_accounts` varchar(45) DEFAULT NULL,
  `min_post_limits` varchar(45) DEFAULT NULL,
  `max_post_limits` varchar(45) CHARACTER SET latin1 COLLATE latin1_bin DEFAULT NULL,
  `min_following_limits` varchar(45) DEFAULT NULL,
  `max_following_limits` varchar(45) DEFAULT NULL,
  `min_follower_limits` varchar(45) DEFAULT NULL,
  `max_follower_limits` varchar(45) DEFAULT NULL,
  `unfollow_speed` varchar(45) DEFAULT NULL,
  `unfollow_limit` varchar(45) DEFAULT NULL,
  `unfollow_source` varchar(45) DEFAULT NULL,
  `engagement_speed` varchar(45) DEFAULT NULL,
  `engagement_source` varchar(45) DEFAULT NULL,
  `engagement_min_like_limits` varchar(45) DEFAULT NULL,
  `engagement_max_like_limits` varchar(45) DEFAULT NULL,
  `settingscol` varchar(45) DEFAULT NULL,
  `sleep_only_business_accounts` varchar(45) DEFAULT NULL,
  `sleep_start_time` varchar(45) DEFAULT NULL,
  `sleep_duration` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `settings`
--

LOCK TABLES `settings` WRITE;
/*!40000 ALTER TABLE `settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscriptions`
--

DROP TABLE IF EXISTS `subscriptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subscriptions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subscription_name` varchar(45) DEFAULT NULL,
  `subscription_price` double(10,2) DEFAULT NULL,
  `subscription_id` varchar(45) DEFAULT NULL,
  `subscription_details` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `status` tinyint(4) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscriptions`
--

LOCK TABLES `subscriptions` WRITE;
/*!40000 ALTER TABLE `subscriptions` DISABLE KEYS */;
/*!40000 ALTER TABLE `subscriptions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `target_account_followers`
--

DROP TABLE IF EXISTS `target_account_followers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `target_account_followers` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `target_account_id` bigint(20) NOT NULL,
  `follower_id` bigint(20) NOT NULL,
  `username` varchar(45) DEFAULT NULL,
  `request_sent` tinyint(1) NOT NULL DEFAULT '0',
  `followback` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `target_account_followers`
--

LOCK TABLES `target_account_followers` WRITE;
/*!40000 ALTER TABLE `target_account_followers` DISABLE KEYS */;
/*!40000 ALTER TABLE `target_account_followers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `target_accounts`
--

DROP TABLE IF EXISTS `target_accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `target_accounts` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `insta_id` bigint(11) NOT NULL,
  `user_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `actions` int(11) NOT NULL,
  `followbacks` int(11) NOT NULL,
  `next_max_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `type` int(2) NOT NULL DEFAULT '0',
  `is_added` tinyint(1) NOT NULL,
  `profile_image` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `target_accounts`
--

LOCK TABLES `target_accounts` WRITE;
/*!40000 ALTER TABLE `target_accounts` DISABLE KEYS */;
/*!40000 ALTER TABLE `target_accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_details`
--

DROP TABLE IF EXISTS `user_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_details` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(10) unsigned NOT NULL,
  `user_insta_id` bigint(11) NOT NULL,
  `full_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `profile_picture` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_follows` int(5) NOT NULL,
  `user_followed_by` int(5) NOT NULL,
  `total_media` bigint(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_details`
--

LOCK TABLES `user_details` WRITE;
/*!40000 ALTER TABLE `user_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `first_name` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `access_token` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `client_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `remember_token` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `saved_target_accounts` tinyint(1) DEFAULT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `user_ip` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `proxy_ip_id` int(11) DEFAULT NULL,
  `payment_status` int(3) DEFAULT NULL,
  `address1` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address2` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `city` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `state` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `zipcode` int(6) DEFAULT NULL,
  `cron_status` tinyint(4) DEFAULT '1',
  `user_type` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(4) DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-06-15 16:02:20
