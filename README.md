[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

# Synthetic Data Generator (SDG)

The _Synthetic Data Generator_ (SDG) creates process-based data.
These data model the treatment of breast cancer patients following the distribution of values in a real breast cancer patient population.

## Parameters

* __number of patients__ - the number of patients that will be modeled
* __mutation probability__ - the mutation probability describes how likely it is for each datum to deviate from the treatment guidelines.

> [!NOTE]
> A mutation probability of 0.0 creates 'clean' data which complies with the treatment guidelines.

## Output Data Formats

On execution, SDG creates the same data set in three different formats.

* CSV
* RDF
* SQL (MySQL 8.1 dump)

## Data Generation

__Requirements:__
* Docker

There are two options for generating the data; one is using `docker-compose`.
After executing either of the available options, your generated data set can be found in `./data`.

__Option 1: With docker-compose__

If you want to use the `docker-compose` option, run the following commands:

```bash
docker-compose up -d --build
docker exec -it SDG bash -c "SDG -n {patients} -p {mutation_prob}"
docker-compose down -v
```

where
* `{patients}` is a placeholder for the number of patients
* `{mutation_prob}` is a placeholder for the mutation probability

This option is recommended if several data sets will be generated. The SDG creates the resulting files with the same name in all the executions, __do not forget to move your generated data before creating another data set!__

__Option 2: Without docker-compose__

If you do not want to use `docker-compose`, you can also execute:

```bash
./generate.sh {patients} {mutation_prob}
```

where
* `{patients}` is a placeholder for the number of patients
* `{mutation_prob}` is a placeholder for the mutation probability

Similar to option 1, `generate.sh` will build the Docker image, start a Docker container, execute the SDG, and stop and remove the Docker container again.
You can use this option if you do not have `docker-compose` installed or if you want to generate only one data set.

As in option 1, the SDG creates the resulting files with the same name in all the executions, __do not forget to move your generated data before creating another data set!__


## Output Data Description

The SGD generates data that could be collected during the treatment process of breast cancer patients, including demographic, gynecologic, diagnostic, tumor-related, treatment, comorbidity, and family history data. To illustrate the output data, the following figure shows the Entity-Relationship diagram of the data generated when choosing the relational database as the output format. Because of readibility reasons, only the key attributes have been included, the rest of attrbites are described in the data dictionaty below. The other output formats generate equivalent data, using the corresponding formats.

![Entity-Relationship diagram of the generated data](https://github.com/SDM-TIB/Synthetic-Data-Generator/blob/main/er-diagram-generated-data.jpg)

The data dictionary is the following:
* patient
  * ehr: INTEGER
  * birth_date: DATE
  * diagnosis_date: DATE
  * age_at_diagnosis: INTEGER
  * first_treatment_date: DATE
  * surgery_date: DATE
  * death_date: DATE / NULL (if the patient has not died)
  * age_at_death: INTEGER / NULL (if the patient has not died)
  * recurrence_year: INTEGER / NULL (if the patient has not relapsed)
  * neoadjuvant: yes / no
  * er_positive: 1 / 0
  * pr_positive: 1 / 0
  * her2_overall_positive: 1 / 0
  * ki67_percent_max_simp: INTEGER (ranging from 0 to 100)
  * menarche_age: INTEGER
  * menopause_age: INTEGER
  * pregnancy: INTEGER
  * abort: INTEGER
  * birth: INTEGER
  * caesarean: INTEGER
* tumor_tnm
  * ehr: INTEGER
  * n_tumor: INTEGER
  * t_prefix_y: 0
  * t_prefix: C / P
  * t_category: IS / 0 / 1 / 2 / 3 / 4
  * n_prefix_y: 0
  * n_prefix: C / P
  * n_category: 0 / 1 / 2 / 3
  * n_subcategory: MI / NULL
  * m_category: 0 / 1
  * t_prefix_y_after_neoadj: 1
  * t_prefix_after_neoadj: C / P / NULL (if not neoadjuvant)
  * t_category_after_neoadj: IS / 0 / 1 / 2 / 3 / 4 / NULL (if not neoadjuvant)
  * n_prefix_y_after_neoadj: 1
  * n_prefix_after_neoadj: C / P / NULL (if not neoadjuvant)
  * n_category_after_neoadj: 0 / 1 / 2 / 3 / NULL (if not neoadjuvant)
  * n_subcategory_after_neoadj: MI / NULL
  * m_category_after_neoadj: 0 / 1 / NULL (if not neoadjuvant)
  * n_tumor_type: INTEGER
  * n_tumor_grade: INTEGER
  * stage_diagnosis: 0 / IA / IB / IIA / IIB / IIIA / IIIB / IIIC / IV
  * stage_after_neo: 0 / IA / IB / IIA / IIB / IIIA / IIIB / IIIC / IV
* tumor_type
  * ehr: INTEGER
  * n_tumor_type: INTEGER
  * ductal: 1 / 0
  * lobular: 1 / 0
  * in_situ: 1 / 0
  * invasive: 1 / 0
  * associated_in_situ: 1 / 0
* tumor_grade
  * ehr: INTEGER
  * n_tumor_grade: INTEGER
  * grade: 1 / 2 / 3
* drug
  * id_drug: INTEGER
  * name: STRING
* chemoterapy_schema
  * id_schema: INTEGER
  * name: STRING
* drug_chemoterapy_schema
  * id_schema: INTEGER
  * id_drug: INTEGER
* chemoterapy_cycle
  * ehr: INTEGER
  * id_schema: INTEGER
  * date: DATE
  * cycle_number: INTEGER
* surgery
  * ehr: INTEGER
  * surgery: STRING
  * n_surgery: INTEGER
  * date_year: INTEGER
  * date_month: INTEGER
  * date_day: INTEGER
* radiotherapy
  * ehr: INTEGER
  * date_start: DATE
  * date_end: DATE
  * n_radiotherapy: INTEGER
  * dose_gy: FLOAT
* comorbidity
  * id: INTEGER
  * ehr: INTEGER
  * comorbidity: STRING
  * negated: 0 / 1
* oral_drug
  * ehr: INTEGER
  * drug: STRING
* family_history
  * ehr: INTEGER
  * cancer_cui: STRING


