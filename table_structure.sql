/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;

--
-- Function to transform strings into URIs
--
DROP FUNCTION IF EXISTS to_uri;
CREATE FUNCTION to_uri(a VARCHAR(255))
RETURNS VARCHAR(255) DETERMINISTIC
BEGIN
  DECLARE val VARCHAR(255);
  IF a = '' THEN
     SET val = NULL;
  ELSE
     SET val = CONCAT('http://research.tib.eu/paladin/entity/', REPLACE(CONCAT(UCASE(LEFT(a, 1)), SUBSTRING(a, 2)), ' ', '_'));
  END IF;
  RETURN val;
END ;

--
-- Function to transform '0' and '1' to 'No' and 'Yes', respectively
--
DROP FUNCTION IF EXISTS to_bool_uri;
CREATE FUNCTION to_bool_uri(a BIT(1))
RETURNS VARCHAR(255) DETERMINISTIC
BEGIN
  DECLARE val VARCHAR(3);
  IF a = 1 THEN
     SET val = 'Yes';
  ELSE
     SET val = 'No';
  END IF;
  RETURN to_uri(val);
END ;

--
-- Capitalize first letter of every word
--
DROP FUNCTION IF EXISTS CAP_FIRST;
CREATE FUNCTION CAP_FIRST (input VARCHAR(255))
RETURNS VARCHAR(255) DETERMINISTIC
BEGIN
  DECLARE len INT;
  DECLARE i INT;

  SET len   = CHAR_LENGTH(input);
  SET input = LOWER(input);
  SET i = 0;

  WHILE (i < len) DO
    IF (MID(input,i,1) = ' ' OR i = 0) THEN
      IF (i < len) THEN
        SET input = CONCAT(
          LEFT(input,i),
          UPPER(MID(input,i + 1,1)),
          RIGHT(input,len - i - 1)
		);
      END IF;
    END IF;
    SET i = i + 1;
  END WHILE;
  RETURN input;
END ;

--
-- Split string function
--
DROP FUNCTION IF EXISTS SPLIT_STR;
CREATE FUNCTION SPLIT_STR(x VARCHAR(255), delim VARCHAR(12), pos INT)
RETURNS VARCHAR(255) DETERMINISTIC
RETURN CAP_FIRST(REPLACE(SUBSTRING(SUBSTRING_INDEX(x, delim, pos), LENGTH(SUBSTRING_INDEX(x, delim, pos -1)) + 1), delim, ''));

--
-- Table structure for table `chemoterapy_cycle`
--

DROP TABLE IF EXISTS `chemoterapy_cycle`;
CREATE TABLE `chemoterapy_cycle` (
  `ehr` int NOT NULL,
  `id_schema` int NOT NULL,
  `date` date NOT NULL,
  `cycle_number` int DEFAULT NULL,
  PRIMARY KEY (`ehr`,`id_schema`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `chemoterapy_schema`
--

DROP TABLE IF EXISTS `chemoterapy_schema`;
CREATE TABLE `chemoterapy_schema` (
  `id_schema` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_schema`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `chemoterapy_schema`
--

LOCK TABLES `chemoterapy_schema` WRITE;
/*!40000 ALTER TABLE `chemoterapy_schema` DISABLE KEYS */;
INSERT INTO `chemoterapy_schema` VALUES (1,'CICLOFOSFAMIDA + DOXORRUBICINA'),(2,'DOXORRUBICINA'),(3,'PACLITAXEL'),(4,'DOCETAXEL'),(5,'CICLOFOSFAMIDA'),(6,'DOCETAXEL + CICLOFOSFAMIDA + DOXORRUBICINA'),(7,'DOCETAXEL + CARBOPLATINO'),(8,'DOCETAXEL + CICLOFOSFAMIDA'),(9,'PERTUZUMAB'),(10,'TRASTUZUMAB + PERTUZUMAB'),(11,'DOCETAXEL + PERTUZUMAB'),(12,'TRASTUZUMAB + DOCETAXEL + PERTUZUMAB'),(13,'CARBOPLATINO'),(14,'BMS-986178'),(15,'PACLITAXEL + CARBOPLATINO'),(16,'NIVOLUMAB + BMS-986178'),(17,'AVASTIN'),(18,'PACLITAXEL + AVASTIN'),(19,'NIVOLUMAB'),(20,'TRASTUZUMAB + PACLITAXEL + PERTUZUMAB'),(21,'EPIRUBICINA + CICLOFOSFAMIDA + FLUOROURACILO'),(22,'TRASTUZUMAB + DOCETAXEL + CARBOPLATINO'),(23,'EPIRUBICINA + CICLOFOSFAMIDA'),(24,'PACLITAXEL + DOCETAXEL'),(25,'PACLITAXEL + PERTUZUMAB'),(26,'DOCETAXEL + DEXAMETASONA'),(27,'TRASTUZUMAB'),(28,'NAB-PACLITAXEL'),(29,'GEMCITABINA + CARBOPLATINO'),(30,'GEMCITABINA'),(31,'PACLITAXEL + BEVACIZUMAB'),(32,'BEVACIZUMAB'),(33,'DOCETAXEL + DOXORRUBICINA'),(34,'ERIBULINA'),(35,'CAELYX'),(36,'TRASTUZUMAB + PACLITAXEL'),(37,'CISPLATINO'),(38,'UTEFOS + CISPLATINO'),(39,'UTEFOS'),(40,'DEXAMETASONA'),(41,'EPIRUBICINA + FLUOROURACILO'),(42,'CICLOFOSFAMIDA + DOXORRUBICINA + FLUOROURACILO'),(43,'TRASTUZUMAB + DOCETAXEL + DEXAMETASONA + CARBOPLATINO'),(44,'TRASTUZUMAB + CICLOFOSFAMIDA + FLUOROURACILO + PERTUZUMAB + EPIRUBICINA'),(45,'ATEZOLIZUMAB + PACLITAXEL'),(46,'ATEZOLIZUMAB'),(47,'TRASTUZUMAB + PACLITAXEL + DOXORRUBICINA + PERTUZUMAB'),(48,'BLEOMICINA + VINCRISTINA'),(49,'PACLITAXEL + DEXAMETASONA'),(50,'CAPECITABINA'),(51,'TRASTUZUMAB + CAPECITABINA'),(52,'TRASTUZUMAB + PERTUZUMAB + CAPECITABINA'),(53,'TRASTUZUMAB + CARBOPLATINO'),(54,'TRASTUZUMAB + CARBOPLATINO + PERTUZUMAB'),(55,'BLEOMICINA + ETOPOSIDO + CISPLATINO'),(56,'ETOPOSIDO + CARBOPLATINO'),(57,'ETOPOSIDO + CISPLATINO'),(58,'ETOPOSIDO'),(59,'PACLITAXEL + DOCETAXEL + PERTUZUMAB'),(60,'METOTREXATO + ERIBULINA'),(61,'DEPOCYTE + AVASTIN'),(62,'DEPOCYTE'),(63,'CARBOPLATINO + PERTUZUMAB'),(64,'FLUOROURACILO'),(65,'GEMCITABINA + PM060184'),(66,'TRASTUZUMAB + PACLITAXEL + CARBOPLATINO');
/*!40000 ALTER TABLE `chemoterapy_schema` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comorbidity`
--

DROP TABLE IF EXISTS `comorbidity`;
CREATE TABLE `comorbidity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ehr` varchar(50) NOT NULL,
  `comorbidity` varchar(250) DEFAULT NULL,
  `negated` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `cui_description`
--

DROP TABLE IF EXISTS `cui_description`;
CREATE TABLE `cui_description` (
  `cui` char(8) NOT NULL,
  `description` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`cui`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `oral_drug_type`
--

LOCK TABLES `cui_description` WRITE;
/*!40000 ALTER TABLE `cui_description` DISABLE KEYS */;
INSERT INTO `cui_description` VALUES ('C0007113','Rectal carcinoma'),('C0023418','Leukemia'),('C0024299','Lymphoma'),('C0025202','Melanoma'),('C0026764','Multiple myeloma'),('C0029925','Ovarian carcinoma'),('C0151546','Oral cavity carcinoma'),('C0153437','Malignant neoplasm of cecum'),('C0153567','Uterine cancer'),('C0153601','Malignant neoplasm of penis'),('C0205699','Carcinomatosis'),('C0235974','Pancreatic carcinoma'),('C0279530','Malignant bone neoplasm'),('C0346627','Intestinal cancer'),('C0476089','Endometrial carcinoma'),('C0549473','Thyroid carcinoma'),('C0595989','Carcinoma of larynx'),('C0600139','Prostate carcinoma'),('C0677483','Carcinoma testes'),('C0678222','Breast carcinoma'),('C0684249','Carcinoma of lung'),('C0699790','Colon carcinoma'),('C0699791','Stomach carcinoma'),('C0699885','Carcinoma of bladder'),('C0699893','Skin carcinoma'),('C0740339','Throat cancer'),('C0751177','Cancer of head'),('C1261473','Sarcoma'),('C1378703','Renal carcinoma'),('C2239176','Liver carcinoma');
/*!40000 ALTER TABLE `cui_description` ENABLE KEYS */;
UNLOCK TABLES;

CREATE INDEX cui_desc ON `cui_description` (`description`) USING HASH;

--
-- Table structure for table `drug`
--

DROP TABLE IF EXISTS `drug`;
CREATE TABLE `drug` (
  `id_drug` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_drug`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `drug`
--

LOCK TABLES `drug` WRITE;
/*!40000 ALTER TABLE `drug` DISABLE KEYS */;
INSERT INTO `drug` VALUES (1,'TRASTUZUMAB'),(2,'VINCRISTINA'),(3,'ATEZOLIZUMAB'),(4,'NIVOLUMAB'),(5,'CICLOFOSFAMIDA'),(6,'CAELYX'),(7,'CAPECITABINA'),(8,'PM060184'),(9,'METOTREXATO'),(10,'DEXAMETASONA'),(11,'FLUOROURACILO'),(12,'UTEFOS'),(13,'AVASTIN'),(14,'PERTUZUMAB'),(15,'DOXORRUBICINA'),(16,'NAB-PACLITAXEL'),(17,'CARBOPLATINO'),(18,'GEMCITABINA'),(19,'BMS-986178'),(20,'CISPLATINO'),(21,'PACLITAXEL'),(22,'BEVACIZUMAB'),(23,'BLEOMICINA'),(24,'DEPOCYTE'),(25,'ERIBULINA'),(26,'EPIRUBICINA'),(27,'DOCETAXEL'),(28,'ETOPOSIDO');
/*!40000 ALTER TABLE `drug` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `drug_chemoterapy_schema`
--

DROP TABLE IF EXISTS `drug_chemoterapy_schema`;
CREATE TABLE `drug_chemoterapy_schema` (
  `id_schema` int NOT NULL,
  `id_drug` int NOT NULL,
  PRIMARY KEY (`id_schema`,`id_drug`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `family_history`
--

DROP TABLE IF EXISTS `family_history`;
CREATE TABLE `family_history` (
  `ehr` int NOT NULL,
  `cancer_cui` char(8) NOT NULL,
  `family_cui` char(8) DEFAULT NULL,
  `count` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `oral_drug`
--

DROP TABLE IF EXISTS `oral_drug`;
CREATE TABLE `oral_drug` (
  `ehr` int NOT NULL,
  `drug` varchar(20) NOT NULL,
  PRIMARY KEY (`ehr`,`drug`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `oral_drug_type`
--

DROP TABLE IF EXISTS `oral_drug_type`;
CREATE TABLE `oral_drug_type` (
    `drug` varchar(20) NOT NULL,
    `drug_type` varchar(20) NOT NULL,
    PRIMARY KEY (`drug`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `oral_drug_type`
--

LOCK TABLES `oral_drug_type` WRITE;
/*!40000 ALTER TABLE `oral_drug_type` DISABLE KEYS */;
INSERT INTO `oral_drug_type` VALUES ('tamoxifen','HormonalTherapy'),('letrozole','HormonalTherapy'),('anastrozole','HormonalTherapy'),('exemestane','HormonalTherapy'),('goserelin','HormonalTherapy'),('abemaciclib','TargetedTherapy'),('alpelisib','TargetedTherapy'),('capecitabine','Chemotherapy'),('everolimus','TargetedTherapy'),('fulvestrant','HormonalTherapy'),('megestrol acetate','HormonalTherapy'),('olaparib','TargetedTherapy'),('palbociclib','TargetedTherapy'),('ribociclib','TargetedTherapy'),('vinorelbine','Chemotherapy');
/*!40000 ALTER TABLE `oral_drug_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patient`
--

DROP TABLE IF EXISTS `patient`;
CREATE TABLE `patient` (
  `ehr` int NOT NULL,
  `birth_date` date DEFAULT NULL,
  `diagnosis_date` date DEFAULT NULL,
  `age_at_diagnosis` int DEFAULT NULL,
  `first_treatment_date` date DEFAULT NULL,
  `surgery_date` date DEFAULT NULL,
  `death_date` date DEFAULT NULL,
  `age_at_death` int DEFAULT NULL,
  `recurrence_year` int DEFAULT NULL,
  `neoadjuvant` varchar(60) DEFAULT NULL,
  `er_positive` bit(1) DEFAULT NULL,
  `pr_positive` bit(1) DEFAULT NULL,
  `her2_overall_positive` bit(1) DEFAULT NULL,
  `ki67_percent_max_simp` int DEFAULT NULL,
  `menarche_age` int DEFAULT NULL,
  `menopause_pre` bit(1) DEFAULT NULL,
  `menopause_age` int DEFAULT NULL,
  `pregnancy` int DEFAULT NULL,
  `abort` int DEFAULT NULL,
  `birth` int DEFAULT NULL,
  `caesarean` int DEFAULT NULL,
  PRIMARY KEY (`ehr`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `radiotherapy`
--

DROP TABLE IF EXISTS `radiotherapy`;
CREATE TABLE `radiotherapy` (
  `ehr` int NOT NULL,
  `date_start` date NOT NULL,
  `date_end` date DEFAULT NULL,
  `n_radiotherapy` int DEFAULT NULL,
  `dose_gy` float DEFAULT NULL,
  PRIMARY KEY (`ehr`,`date_start`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `surgery`
--

DROP TABLE IF EXISTS `surgery`;
CREATE TABLE `surgery` (
  `ehr` int NOT NULL,
  `surgery` varchar(50) NOT NULL,
  `n_surgery` int NOT NULL,
  `date_year` int DEFAULT NULL,
  `date_month` int DEFAULT NULL,
  `date_day` int DEFAULT NULL,
  PRIMARY KEY (`ehr`,`surgery`,`n_surgery`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `tumor_grade`
--

DROP TABLE IF EXISTS `tumor_grade`;
CREATE TABLE `tumor_grade` (
  `ehr` int NOT NULL,
  `n_tumor_grade` int NOT NULL,
  `grade` int DEFAULT NULL,
  PRIMARY KEY (`ehr`,`n_tumor_grade`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `tumor_tnm`
--

DROP TABLE IF EXISTS `tumor_tnm`;
CREATE TABLE `tumor_tnm` (
  `ehr` int NOT NULL,
  `n_tumor_tnm` int NOT NULL,
  `t_prefix_y` bit(1) DEFAULT NULL,
  `t_prefix` varchar(5) DEFAULT NULL,
  `t_category` varchar(5) DEFAULT NULL,
  `n_prefix_y` bit(1) DEFAULT NULL,
  `n_prefix` varchar(5) DEFAULT NULL,
  `n_category` varchar(5) DEFAULT NULL,
  `n_subcategory` varchar(5) DEFAULT NULL,
  `m_category` varchar(5) DEFAULT NULL,
  `t_prefix_y_after_neoadj` bit(1) DEFAULT NULL,
  `t_prefix_after_neoadj` varchar(5) DEFAULT NULL,
  `t_category_after_neoadj` varchar(5) DEFAULT NULL,
  `n_prefix_y_after_neoadj` bit(1) DEFAULT NULL,
  `n_prefix_after_neoadj` varchar(5) DEFAULT NULL,
  `n_category_after_neoadj` varchar(5) DEFAULT NULL,
  `n_subcategory_after_neoadj` varchar(5) DEFAULT NULL,
  `m_category_after_neoadj` varchar(5) DEFAULT NULL,
  `n_tumor_type` int DEFAULT NULL,
  `n_tumor_grade` int DEFAULT NULL,
  `stage_diagnosis` varchar(20) DEFAULT NULL,
  `stage_after_neo` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`ehr`,`n_tumor_tnm`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `tumor_type`
--

DROP TABLE IF EXISTS `tumor_type`;
CREATE TABLE `tumor_type` (
  `ehr` int NOT NULL,
  `n_tumor_type` int NOT NULL,
  `ductal` bit(1) DEFAULT NULL,
  `lobular` bit(1) DEFAULT NULL,
  `in_situ` bit(1) DEFAULT NULL,
  `invasive` bit(1) DEFAULT NULL,
  `associated_in_situ` bit(1) DEFAULT NULL,
  PRIMARY KEY (`ehr`,`n_tumor_type`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*!40101 SET character_set_client = @saved_cs_client */;
