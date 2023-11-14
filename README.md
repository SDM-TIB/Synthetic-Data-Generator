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

The SGD generates data that could be collected during the treatment process of breast cancer patients, including demographic, gynecologic, diagnostic, tumor-related, treatment, comorbidity, and family history data. To illustrate the output data, the following figure shows the Entity-Relationship diagram of the data generated when choosing the relational database as the output format. The other output formats generate equivalent data, using the corresponding formats.

The data dictionary is the following:
* patient
  * ehr: INTEGER
* tumor_tnm
* tumor_type
* tumor_grade
* drug
* chemoterapy_schema
* drug_chemoterapy_schema
* chemoterapy_cycle
* surgery
* radiotherapy
* comorbidity
* oral_drug
* family_history
* cui_description


