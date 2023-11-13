#!/bin/env python3
# -*- coding: utf-8 -*-
"""
Synthetic Data Generator

Generates synthetic breast cancer data following the distribution in a real breast cancer patient population.

@author: Antonio Jesús Díaz-Honrubia
@author: Philipp D. Rohde
"""
import argparse
import csv
import datetime
import os
import time

import mysql.connector
import numpy as np
import pandas as pd
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from rdfizer import semantify

max_cycles_adjuvant = 20
mean_age_dx = 57
mean_menarche_age = 12.7819
std_menarche_age = 1.5889
mean_menopause_age = 49.2085
std_menopause_age = 4.8551
max_menopause_age = (60, 68)
mean_pregnancies = 2.0103
std_pregnancies = 1.5467
abort_prob = {0: 0.7330, 1: 0.1858, 2: 0.0516, 3: 0.0214, 4: 0.0082}
caesarean_prob = {0: 0.9128, 1: 0.0480, 2: 0.0310, 3: 0.0063, 4: 0.0019}

tumor_type_prob = {'PP': 0.1107, 'PN': 0.7574, 'NP': 0.0437, 'NN': 0.0882}
death_prob = {'PP': 0.0903, 'PN': 0.1234, 'NP': 0.1207, 'NN': 0.1679}
mean_days_alive = {'PP': 2241, 'PN': 1959, 'NP': 2016, 'NN': 959}
stage_dx_prob = {'0': 0.0846, 'IA': 0.3243, 'IB': 0.0432, 'IIA': 0.2260, 'IIB': 0.1179, 'IIIA': 0.0867, 'IIIB': 0.0151, 'IIIC': 0.0379, 'IV': 0.06423}
grade_prob = {'1': 0.2, '2': 0.6, '3': 0.2}
mean_ki67 = {'PP': 28.2891, 'PN': 16.6183, 'NP': 38.8101, 'NN': 50.2081}
surgery_prob = {'mastectomy': 0.5, 'partial mastectomy': 0.5}
stage_neo_prob = {  # Outer: stage at diagnosis, Inner: stage after neoadjuvant treatment
    '0': {'0': 1.0},
    'IA': {'0': 0.1, 'IA': 0.9},
    'IB': {'0': 0.1, 'IA': 0.9},
    'IIA': {'0': 0.0597, 'IA': 0.3134, 'IB': 0.0150, 'IIA': 0.3284, 'IIB': 0.0148, 'IIIA': 0.2388, 'IIIC': 0.0299},
    'IIB': {'0': 0.1, 'IA': 0.5, 'IIA': 0.1, 'IIB': 0.1, 'IIIA': 0.17, 'IV': 0.03},
    'IIIA': {'0': 0.0555, 'IA': 0.1055, 'IB': 0.1056, 'IIA': 0.1389, 'IIB': 0.1111, 'IIIA': 0.3756, 'IIIB': 0.0378, 'IV': 0.07},
    'IIIB': {'0': 0.0556, 'IA': 0.1055, 'IB': 0.1055, 'IIA': 0.1389, 'IIB': 0.1011, 'IIIA': 0.3656, 'IIIB': 0.0378, 'IV': 0.09},
    'IIIC': {'0': 0.0555, 'IA': 0.1056, 'IB': 0.1056, 'IIA': 0.1389, 'IIB': 0.1011, 'IIIA': 0.3655, 'IIIB': 0.0278, 'IV': 0.1},
    'IV': {'IV': 1.0}
}
hist_type_prob = {'ductal': 0.6276, 'lobular': 0.0932, 'other': 0.2792}
ass_in_situ_prob = {'0': 0.4885, '1': 0.5115}

days_to_radio = (28, 42)
radio_days_mean = 33.57
radio_days_std = 19.76
radio_days_range = (7, 60)
radio_gy_mean = 46.07
radio_gy_std = 8.35
radio_gy_range = (4, 70)

commorbidities_prob = {'autoimmune disease': 0.0366,
                       'cardiac insufficiency': 0.0160,
                       'diabetes': 0.0751,
                       'dislipemia': 0.1600,
                       'gastrointestinal disease': 0.0637,
                       'hta': 0.2438,
                       'insomnia': 0.0019,
                       'ischemic cardiopathology': 0.0187,
                       'liver disease': 0.0487,
                       'lung disease': 0.0432,
                       'musculoskeletal disease': 0.1203,
                       'other cardiopathology': 0.0475,
                       'psychiatric disorder': 0.0740,
                       'renal disease': 0.0191,
                       'smoker or ex-smoker': 0.3631,
                       'thyroid disease': 0.1453,
                       'transplant': 0.0012}
id_commorbidity = 0

smoker_or_ex_prob = {'ex-smoker': 0.5396, 'smoker': 0.4604}

oral_drug_prob = {'tamoxifen': 0.8124,
                  'letrozole': 0.4028,
                  'anastrozole': 0.1532,
                  'exemestane': 0.1170,
                  'goserelin': 0.1071,
                  'abemaciclib': 0.0090,
                  'alpelisib': 0.0039,
                  'capecitabine': 0.0826,
                  'everolimus': 0.0159,
                  'fulvestrant': 0.0727,
                  'megestrol acetate': 0.0284,
                  'olaparib': 0.0013,
                  'palbociclib': 0.0429,
                  'ribociclib': 0.0281,
                  'vinorelbine': 0.0232}

family_prob = {'C0678222': 0.1323,
               'C0684249': 0.0262,
               'C0699790': 0.0232,
               'C0699791': 0.0202,
               'C0600139': 0.0138,
               'C0029925': 0.0114,
               'C0023418': 0.0099,
               'C0024299': 0.0099,
               'C2239176': 0.0089,
               'C0025202': 0.0084,
               'C0235974': 0.0064,
               'C0740339': 0.0059,
               'C0699885': 0.0054,
               'C0153567': 0.0044,
               'C0476089': 0.0044,
               'C1378703': 0.0044,
               'C0549473': 0.0040,
               'C0595989': 0.0025,
               'C0007113': 0.0020,
               'C0205699': 0.0020,
               'C0699893': 0.0020,
               'C0026764': 0.0010,
               'C0346627': 0.0010,
               'C0751177': 0.0010,
               'C1261473': 0.0010,
               'C0151546': 0.0005,
               'C0153437': 0.0005,
               'C0153601': 0.0005,
               'C0279530': 0.0005,
               'C0677483': 0.0005}


def initialize_database(con: MySQLConnection, cur: MySQLCursor) -> None:
    """Creates all the tables in the database."""
    with open('table_structure.sql', 'r', encoding='utf8') as f:
        for _ in cur.execute(f.read(), multi=True):
            pass  # consume the results in order for the changes to be reflected
        con.commit()


def extract_one(probs: dict):
    r = np.random.rand()
    accumulated = 0.0
    for k in probs.keys():
        accumulated += probs[k]
        if r < accumulated:
            return k
    return list(probs.keys())[-1]


def calculate_age(born: datetime.date, current: datetime.date) -> int:
    return current.year - born.year - ((current.month, current.day) < (born.month, born.day))


def get_tnm(stage: str):
    if stage == '0':
        return 'IS', '0', None, '0'
    elif stage == 'IA':
        return '1', '0', None, '0'
    elif stage == 'IB':
        return ('1' if np.random.rand() < 0.78 else '0'), '1', 'MI', '0'
    elif stage == 'IIA':
        r = np.random.rand()
        if r < 0.3:
            return '0', '1', None, '0'
        elif r < 0.55:
            return '1', '1', None, '0'
        else:
            return '2', '0', None, '0'
    elif stage == 'IIB':
        if np.random.rand() < 0.85:
            return '2', '1', None, '0'
        else:
            return '3', '0', None, '0'
    elif stage == 'IIIA':
        if np.random.rand() < 0.2:
            return '3', '1', None, '0'
        else:
            return extract_one({'0': 0.5, '1': 0.1, '2': 0.3, '3': 0.1}), '2', None, '0'
    elif stage == 'IIIB':
        return '4', extract_one({'0': 0.1, '1': 0.4, '2': 0.5}), None, '0'
    elif stage == 'IIIC':
        return extract_one({'0': 0.45, '1': 0.1, '2': 0.25, '3': 0.15, '4': 0.05}), '3', None, '0'
    else:
        return extract_one({'0': 0.4, '1': 0.1, '2': 0.2, '3': 0.1, '4': 0.2}), extract_one({'0': 0.1, '1': 0.35, '2': 0.25, '3': 0.3}), None, '0'


def generate_data(ehr: int, cur: MySQLCursor, error_prob: float = 0.0):
    # Dx Age and tumor type
    age_dx = int(np.random.normal(mean_age_dx, 10))
    age_dx = age_dx if age_dx >= 20 else 20
    tumor_type = extract_one(tumor_type_prob)

    # Death
    death = np.random.rand() < death_prob[tumor_type]
    if np.random.rand() < error_prob:
        death = np.random.choice(15*[False] + [True])
    days_alive = int(np.random.normal(mean_days_alive[tumor_type], mean_days_alive[tumor_type]/7))
    days_alive = days_alive if days_alive >= 200 else 200
    if np.random.rand() < error_prob:
        days_alive += int(np.random.normal(700.0, 70.0) * np.random.choice([1, -1]))
    
    # Birthdate
    days_since_dx = np.random.randint(10, 500) + int(np.random.normal(1800, 100))
    days_since_dx = days_since_dx if days_since_dx >= 200 else 200
    days_since_dx = days_since_dx if not death else days_since_dx+days_alive
    days_since_birth = days_since_dx + age_dx*365 + np.random.randint(0, 365)
    birth_date = datetime.date.today() - datetime.timedelta(days=days_since_birth)
    if birth_date.month == 2 and birth_date.day > 28:
        birth_date = birth_date - datetime.timedelta(days=5)
    dx_date = datetime.date(birth_date.year + age_dx, birth_date.month, birth_date.day)
    dx_date = dx_date + datetime.timedelta(days=np.random.randint(0, 365))
    if np.random.rand() < error_prob:
        dx_date = dx_date + datetime.timedelta(days=int(np.random.normal(1500.0, 300.0) * np.random.choice([1, -1])))
    
    # Death date and age
    death_date = dx_date + datetime.timedelta(days=days_alive)
    age_death = calculate_age(birth_date, death_date)
    if not death:
        death_date = death_date + datetime.timedelta(days=365000)
    if np.random.rand() < error_prob:
        death_date = death_date + datetime.timedelta(days=int(np.random.normal(1500.0, 300.0) * np.random.choice([1, -1])))
    
    # Gynaecological antecedents
    menarche_age = int(np.random.normal(mean_menarche_age, std_menarche_age)+0.5)
    if np.random.rand() < error_prob:
        menarche_age = menarche_age + int(np.random.normal(6.0, 2.0) * np.random.choice([1, -1]))
    menopause_age = int(np.random.normal(mean_menopause_age, std_menopause_age)+0.5)
    if menopause_age >= max_menopause_age[0] and np.random.rand() < 0.6:
        menopause_age -= 30
    elif menopause_age >= max_menopause_age[1]:
        menopause_age -= 8
    menopause_pre = menopause_age < age_dx
    if menopause_age > age_death or menopause_age > calculate_age(birth_date, datetime.date.today()):
        menopause_age = None
    if np.random.rand() < error_prob:
        if pd.notna(menopause_age):
            menopause_age = menopause_age + int(np.random.normal(25.0, 4.0) * np.random.choice([1, -1]))
        else:
            menopause_age = int(np.random.normal(120.0, 10.0))
    if np.random.rand() < error_prob:
        menopause_pre = not menopause_pre
    
    pregnancies = int(np.random.normal(mean_pregnancies, std_pregnancies)+0.5)
    pregnancies = 0 if pregnancies < 0 else pregnancies
    births = aborts = caesareans = 0
    if pregnancies > 0:
        aborts = extract_one(abort_prob)
        aborts = pregnancies if aborts > pregnancies else aborts
        caesareans = extract_one(caesarean_prob)
        caesareans = pregnancies - aborts if caesareans > (pregnancies-aborts) else caesareans
        births = pregnancies - aborts - caesareans
    if np.random.rand() < error_prob:
        pregnancies = pregnancies + int(np.random.normal(6.0, 2.0) * np.random.choice([1, -1]))
    if np.random.rand() < error_prob:
        births = births + int(np.random.normal(6.0, 2.0) * np.random.choice([1, -1]))
    if np.random.rand() < error_prob:
        aborts = aborts + int(np.random.normal(6.0, 2.0) * np.random.choice([1, -1]))
    if np.random.rand() < error_prob:
        caesareans = caesareans + int(np.random.normal(6.0, 2.0) * np.random.choice([1, -1]))

    # Immunohistochemistry (IHC)
    er = tumor_type[0] == 'P'
    pr = tumor_type[0] == 'P'
    if er and pr and np.random.rand() < 0.25:
        if np.random.rand() < 0.5:
            er = False
        else:
            pr = False
    her2 = tumor_type[1] == 'P'
    ki67 = int(np.random.normal(mean_ki67[tumor_type], mean_ki67[tumor_type]/3))
    ki67 = ki67 if ki67 <= 100 else 100
    ki67 = ki67 if ki67 >= 0 else 0
    grade = extract_one(grade_prob)
    if tumor_type == 'PN':
        if np.random.rand() < 0.15 and int(grade) > 1:
            grade = str(int(grade)-1)
    elif tumor_type == 'NN':
        if np.random.rand() < 0.15 and int(grade) < 3:
            grade = str(int(grade)+1)
    if np.random.rand() < error_prob:
        ki67 = ki67 + int(np.random.normal(40.0, 8.0) * np.random.choice([1, -1]))
    if np.random.rand() < error_prob:
        er = not er
    if np.random.rand() < error_prob:
        pr = not pr
    
    # Stage
    stage_dx = extract_one(stage_dx_prob)
    stage_neo = extract_one(stage_neo_prob[stage_dx])
    t, n, mi, m = get_tnm(stage_dx)
    t_neo, n_neo, mi_neo, m_neo = get_tnm(stage_neo)
    
    # Other tumor-related data (stage, histological type, etc.)
    neoadjuvant = ((stage_dx == 'IA' or stage_dx == 'IB') and (tumor_type != 'PN')) or stage_dx[:2] == 'II'
    invasive = stage_dx != '0'
    hist_type = extract_one(hist_type_prob)
    ass_in_situ = extract_one(ass_in_situ_prob)
        
    # Neoadjuvant chemo
    ch_date = dx_date
    cycles = []
    if neoadjuvant:
        n_ciclos = np.random.randint(3, 6)
        if np.random.rand() < error_prob:
            n_ciclos = n_ciclos + np.random.randint(-7, 8)
            n_ciclos = n_ciclos if n_ciclos >= 0 else 0

        ch_date = ch_date + datetime.timedelta(days=np.random.randint(20, 32))
        if np.random.rand() < error_prob:
            ch_date = ch_date + (datetime.timedelta(days=np.random.randint(10, 20)) * np.random.choice([1, -1]))
        if tumor_type[1] == 'N':
            schema = 21
        elif stage_dx == 'IA' or stage_dx == 'IB':
            schema = np.random.choice([10, 27])
        else:
            schema = np.random.choice([10, 27, 20, 36, 43, 44, 51, 52, 53])
        if np.random.rand() < error_prob:
            schema = np.random.choice([10, 20, 43, 51, 9, 11, 25, 59, 63])
        
        for i in range(n_ciclos):
            cycles += [[ehr, schema, ch_date, i+1]]
            ch_date = ch_date + datetime.timedelta(days=21)
            if np.random.rand() < error_prob:
                ch_date = ch_date + (datetime.timedelta(days=np.random.randint(10, 20)) * np.random.choice([1, -1]))

    df_chemo = pd.DataFrame(cycles, columns=['ehr', 'id_schema', 'date', 'cycle_number'])

    # Surgery
    surgery_date = ch_date
    surgeries = []
    r = np.random.rand()
    if stage_dx != 'IV' or r < error_prob:
        if np.random.rand() < 0.8 or np.random.rand() >= error_prob:
            surgery_date = surgery_date + datetime.timedelta(days=np.random.randint(21, 35))
            if np.random.rand() < error_prob:
                surgery_date = surgery_date + (datetime.timedelta(days=np.random.randint(20, 35)) * np.random.choice([1, -1]))
            surgery_type = extract_one(surgery_prob)
            surgeries += [[ehr, surgery_type, 1, ch_date.year, ch_date.month, ch_date.day]]
            if np.random.rand() < 0.5:
                surgeries += [[ehr, 'sentinel lymph node biopsy', 1, ch_date.year, ch_date.month, ch_date.day]]
            if stage_dx[:2] == 'II':
                surgeries += [[ehr, 'lymphadenectomy', 1, ch_date.year, ch_date.month, ch_date.day]]
    
    df_surgeries = pd.DataFrame(surgeries, columns=['ehr', 'surgery', 'n_surgery', 'date_year', 'date_month', 'date_day'])

    # Adjuvant chemo
    ch_date = surgery_date
    cycles = []
    n_prev_cycles = len(df_chemo)
    
    if stage_dx != '0':
        n_ciclos = np.random.randint(3, max_cycles_adjuvant)
        if np.random.rand() < error_prob:
            n_ciclos = n_ciclos + np.random.randint(-7, 8)
            n_ciclos = n_ciclos if n_ciclos >= 0 else 0

        ch_date = ch_date + datetime.timedelta(days=np.random.randint(28, 38))
        if np.random.rand() < error_prob:
            ch_date = ch_date + (datetime.timedelta(days=np.random.randint(15, 35)) * np.random.choice([1, -1]))

        if tumor_type[1] == 'N':
            schema = 21
        elif stage_dx == 'IA' or stage_dx == 'IB':
            schema = np.random.choice([10, 27])
        elif stage_dx == 'IV':
            schema = 50
        else:
            schema = np.random.choice([10, 27, 20, 36, 43, 44, 51, 52, 53])
        if np.random.rand() < error_prob:
            schema = np.random.choice([10, 20, 43, 44, 50, 51, 9, 11, 25, 59, 63])
        for i in range(n_ciclos):
            cycles += [[ehr, schema, ch_date, i + 1 + n_prev_cycles]]
            ch_date = ch_date + datetime.timedelta(days=21)
            if np.random.rand() < error_prob:
                ch_date = ch_date + (datetime.timedelta(days=np.random.randint(10, 20)) * np.random.choice([1, -1]))
    
    df_chemo2 = pd.DataFrame(cycles, columns=['ehr', 'id_schema', 'date', 'cycle_number'])
    df_chemo = pd.concat([df_chemo, df_chemo2])
    df_chemo = df_chemo.drop_duplicates(subset=['ehr', 'id_schema', 'date'])
    
    first_chemo_date = None
    if len(df_chemo) > 0:
        first_chemo_date = df_chemo['date'].min()
        if np.random.rand() < error_prob:
            first_chemo_date = first_chemo_date + (datetime.timedelta(days=np.random.randint(50, 500)) * np.random.choice([1, -1]))
    
    first_surgery_date = None
    if len(df_surgeries) > 0:
        year = int(df_surgeries['date_year'].min())
        month = int(df_surgeries[df_surgeries['date_year'] == year]['date_month'].min())
        day = int(df_surgeries[(df_surgeries['date_year'] == year) & (df_surgeries['date_month'] == month)]['date_day'].min())
        first_surgery_date = datetime.date(year, month, day)
        if np.random.rand() < error_prob:
            first_surgery_date = first_surgery_date + (datetime.timedelta(days=np.random.randint(50, 500)) * np.random.choice([1, -1]))

    # Radiotherapy
    radio_start_date = ch_date + datetime.timedelta(days=np.random.randint(radio_days_range[0], radio_days_range[1]))
    radio_days = int(np.random.normal(radio_days_mean, radio_days_std) + 0.5)
    radio_days = radio_days if radio_days >= radio_days_range[0] else radio_days_range[0]
    radio_days = radio_days if radio_days <= radio_days_range[1] else radio_days_range[1]
    radio_end_date = radio_start_date + datetime.timedelta(days=radio_days)
    radio_gy = float(np.random.normal(radio_gy_mean, radio_gy_std) + 0.5)
    radio_gy = radio_gy if radio_gy >= radio_gy_range[0] else radio_days_range[0]
    radio_gy = radio_gy if radio_gy <= radio_gy_range[1] else radio_days_range[1]
    if np.random.rand() < error_prob:
        radio_start_date = radio_start_date + (datetime.timedelta(days=int(np.random.randint(20, 50) * np.random.choice([1, -1]))))
    if np.random.rand() < error_prob:
        radio_end_date = radio_end_date + (datetime.timedelta(days=int(np.random.randint(20, 50) * np.random.choice([1, -1]))))
    if np.random.rand() < error_prob:
        radio_gy = radio_gy + float(np.random.randint(20, 50) * np.random.choice([1, -1]))

    # Tumor prefix
    prefix_dx = 'C' if len(df_surgeries) == 0 or neoadjuvant else 'P'
    prefix_neo = 'C' if len(df_surgeries) == 0 else 'P'

    # Mutation relevant tumor info
    if error_prob > 0.0:
        if np.random.rand() < error_prob:
            stage_dx = np.random.choice(list(stage_dx_prob.keys()))
        if np.random.rand() < error_prob:
            stage_neo = np.random.choice(list(stage_dx_prob.keys()))
        if np.random.rand() < error_prob:
            neoadjuvant = not neoadjuvant
        if np.random.rand() < error_prob:
            t = np.random.choice(['0', '1', '2', '3', '4', 'IS'])
        if np.random.rand() < error_prob:
            n = np.random.choice(['0', '1', '2', '3'])
        if np.random.rand() < error_prob:
            mi = np.random.choice(['MI', None, None, None])
        if np.random.rand() < error_prob:
            m = np.random.choice(['0', '1'])
        if np.random.rand() < error_prob:
            t_neo = np.random.choice(['0', '1', '2', '3', '4', 'IS'])
        if np.random.rand() < error_prob:
            n_neo = np.random.choice(['0', '1', '2', '3'])
        if np.random.rand() < error_prob:
            mi_neo = np.random.choice(['MI', None, None, None])
        if np.random.rand() < error_prob:
            m_neo = np.random.choice(['0', '1'])
        if np.random.rand() < error_prob:
            invasive = np.random.choice([True, True, True, False])
        if np.random.rand() < error_prob:
            hist_type = np.random.choice(list(hist_type_prob.keys()))
        if np.random.rand() < error_prob:
            ass_in_situ = np.random.choice(list(ass_in_situ_prob.keys()))
        if np.random.rand() < error_prob:
            grade = np.random.choice(list(grade_prob.keys()))
        if np.random.rand() < error_prob:
            prefix_dx = np.random.choice(['C', 'P', 'P', 'P'])
        if np.random.rand() < error_prob:
            prefix_neo = np.random.choice(['C', 'P', 'P', 'P'])

    # Commorbidities
    global id_commorbidity
    commorbidities = []
    for c in commorbidities_prob.keys():
        id_commorbidity += 1
        if c != 'smoker or ex-smoker':
            present = 1 if np.random.rand() < commorbidities_prob[c] else 0
            if np.random.rand() < error_prob:
                present = np.random.choice([0, 1])
            commorbidities += [[id_commorbidity, ehr, c, present]]
        else:
            if np.random.rand() < commorbidities_prob[c]:
                smoker_or_ex = extract_one(smoker_or_ex_prob)
                present = 1 if smoker_or_ex == 'smoker' else 0
                if np.random.rand() < error_prob:
                    present = np.random.choice([0, 1])
                commorbidities += [[id_commorbidity, ehr, 'smoker', present]]
                id_commorbidity += 1
                present = 1 if smoker_or_ex != 'smoker' else 0
                if np.random.rand() < error_prob:
                    present = np.random.choice([0, 1])
                commorbidities += [[id_commorbidity, ehr, 'ex-smoker', present]]
            else:
                present = 0
                if np.random.rand() < error_prob:
                    present = np.random.choice([0, 1])
                commorbidities += [[id_commorbidity, ehr, 'smoker', present]]
                id_commorbidity += 1
                present = 0
                if np.random.rand() < error_prob:
                    present = np.random.choice([0, 1])
                commorbidities += [[id_commorbidity, ehr, 'ex-smoker', present]]
    df_commorbidities = pd.DataFrame(commorbidities, columns=['id', 'ehr', 'comorbidity', 'negated'])

    # Oral drugs
    oral_drug = []
    if er or pr:
        for d in oral_drug_prob.keys():
            if np.random.rand() < oral_drug_prob[d]:
                oral_drug += [[ehr, d]]
    df_oral_drug = pd.DataFrame(oral_drug, columns=['ehr', 'drug'])
    if (len(df_oral_drug) == 2 and np.random.rand() < 0.5) or (len(df_oral_drug) > 2 and np.random.rand() < 0.2):
        df_oral_drug = df_oral_drug.drop([np.random.randint(len(df_oral_drug))], axis=0)

    remove = []
    add = []
    for r in df_oral_drug.index:
        if np.random.rand() < error_prob:
            action = np.random.choice(['remove', 'add', 'mutate'])
            if action == 'remove' or action == 'mutate':
                remove += [r]
            if action == 'add' or action == 'mutate':
                add += [[ehr, np.random.choice(list(oral_drug_prob.keys()))]]
    df_oral_drug = df_oral_drug.drop(remove, axis=0)
    df_add = pd.DataFrame(add, columns=['ehr', 'drug'])
    df_oral_drug = pd.concat([df_oral_drug, df_add]).drop_duplicates()

    # Family history
    family = []
    for f in family_prob.keys():
        if np.random.rand() < family_prob[f]:
            family += [[ehr, f]]
    df_family = pd.DataFrame(family, columns=['ehr', 'cancer_cui'])

    remove = []
    add = []
    for r in df_family.index:
        if np.random.rand() < error_prob:
            action = np.random.choice(['remove', 'add', 'mutate'])
            if action == 'remove' or action == 'mutate':
                remove += [r]
            if action == 'add' or action == 'mutate':
                add += [[ehr, np.random.choice(list(family_prob.keys()))]]
    df_family = df_family.drop(remove, axis=0)
    df_add = pd.DataFrame(add, columns=['ehr', 'cancer_cui'])
    df_family = pd.concat([df_family, df_add]).drop_duplicates()

    # Data insertion
    sql = 'INSERT INTO patient(ehr, birth_date, diagnosis_date, age_at_diagnosis, first_treatment_date, surgery_date, death_date, age_at_death, er_positive, pr_positive, her2_overall_positive, ki67_percent_max_simp, neoadjuvant, menarche_age, menopause_pre, menopause_age, pregnancy, abort, birth, caesarean) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
    cur.execute(sql, (ehr, birth_date, dx_date, age_dx, first_chemo_date, first_surgery_date, death_date if death else None, age_death if death else None, 1 if er else 0, 1 if pr else 0, 1 if her2 else 0, ki67, 'yes' if neoadjuvant else 'no', menarche_age, menopause_pre, menopause_age, pregnancies, aborts, births, caesareans))

    if neoadjuvant:
        sql = 'INSERT INTO tumor_tnm(ehr, n_tumor_tnm, t_prefix_y, t_prefix, t_category, n_prefix_y, n_prefix, n_category, n_subcategory, m_category, t_prefix_y_after_neoadj, t_prefix_after_neoadj, t_category_after_neoadj, n_prefix_y_after_neoadj, n_prefix_after_neoadj, n_category_after_neoadj, n_subcategory_after_neoadj, m_category_after_neoadj, n_tumor_type, n_tumor_grade, stage_diagnosis, stage_after_neo) VALUES (%s'+', %s' * 21 + ');'
        cur.execute(sql, (ehr, 1, 0, prefix_dx, t, 0, prefix_dx, n, mi, m, 1, prefix_neo, t_neo, 1, prefix_neo, n_neo, mi_neo, m_neo, 1, 1, stage_dx, stage_neo))
    else:
        sql = 'INSERT INTO tumor_tnm(ehr, n_tumor_tnm, t_prefix_y, t_prefix, t_category, n_prefix_y, n_prefix, n_category, n_subcategory, m_category, n_tumor_type, n_tumor_grade, stage_diagnosis) VALUES (%s'+', %s' * 12 + ');'
        cur.execute(sql, (ehr, 1, 0, prefix_dx, t, 0, prefix_dx, n, mi, m, 1, 1, stage_dx))

    sql = 'INSERT INTO tumor_type VALUES (%s, %s, %s, %s, %s, %s, %s);'
    cur.execute(sql, (ehr, 1, 1 if hist_type == 'ductal' else None, 1 if hist_type == 'lobular' else None, 1 if not invasive else None, 1 if invasive else None, 1 if ass_in_situ == '1' else None))

    sql = 'INSERT INTO tumor_grade VALUES (%s, %s, %s);'
    cur.execute(sql, (ehr, 1, grade))

    sql = 'INSERT INTO chemoterapy_cycle VALUES (%s, %s, %s, %s);'
    cur.executemany(sql, df_chemo.values.tolist())

    sql = 'INSERT INTO surgery VALUES (%s, %s, %s, %s, %s, %s);'
    cur.executemany(sql, df_surgeries.values.tolist())

    sql = 'INSERT INTO radiotherapy VALUES (%s, %s, %s, %s, %s);'
    cur.execute(sql, (ehr, radio_start_date, radio_end_date, 1, radio_gy))

    sql = 'INSERT INTO comorbidity VALUES (%s, %s, %s, %s);'
    cur.executemany(sql, df_commorbidities.values.tolist())

    sql = 'INSERT INTO oral_drug VALUES (%s, %s);'
    cur.executemany(sql, df_oral_drug.values.tolist())

    sql = 'INSERT INTO family_history(ehr, cancer_cui) VALUES (%s, %s);'
    cur.executemany(sql, df_family.values.tolist())


def dump_csv(cur: MySQLCursor):
    db_cur.execute('show tables;')
    result = db_cur.fetchall()
    tables = [res[0] for res in result]

    os.makedirs('/data/csv/', exist_ok=True)

    for table in tables:
        cur.execute('SELECT * FROM ' + table)
        result = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        with open('/data/csv/' + table + '.csv', 'w', encoding='utf8') as fp:
            csv_file = csv.writer(fp, lineterminator='\n')
            csv_file.writerow(column_names)
            csv_file.writerows(result)


def open_db_connection(url: str, port: int, user: str, pwd: str, db_name: str) -> (MySQLConnection, MySQLCursor):
    tries = 1
    err = None
    while tries < 10:
        try:
            db_con = mysql.connector.connect(
                host=url,
                port=port,
                user=user,
                password=pwd,
                database=db_name
            )
            db_cur = db_con.cursor()
            return db_con, db_cur
        except mysql.connector.errors.InterfaceError as e:
            tries += 1
            err = e
            print('Could not connect to DB. Re-try in 5 seconds...')
            time.sleep(5)
    raise err


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Synthetic Data Generator')
    parser.add_argument('-n', metavar='number_patients', type=int, required=True,
                        help='Number of patients to model')
    parser.add_argument('-p', metavar='mutation_prob', type=float, required=True,
                        help='Mutation probability; in [0.0, 1.0]. Clean data will be generated with p=0.0.')
    args = parser.parse_args()

    n_patients = args.n
    error_prob_param = args.p

    db_con, db_cur = open_db_connection('localhost', 3306, 'root', 'paladin', 'synth')
    # db_con, db_cur = open_db_connection('localhost', 3400, 'root', 'paladin', 'bc')
    start = time.time()
    initialize_database(db_con, db_cur)
    print("Setting up the database:", time.time() - start)

    start_gen = time.time()
    for ehr in range(n_patients):
        generate_data(ehr+1, db_cur, error_prob=error_prob_param)
    print('Generating data:', time.time() - start_gen)

    db_con.commit()

    start_sql = time.time()
    os.system('mysqldump -uroot -ppaladin synth | gzip > /data/synth_data.sql.gz')
    print('Dumping database:', time.time() - start_sql)

    start_csv = time.time()
    dump_csv(db_cur)
    print('Dumping CSV:', time.time() - start_csv)

    rdfizer_config = {
        "default": {
            "main_directory": "."
        },
        "datasets": {
            "number_of_datasets": 1,
            "output_folder": "/data",
            "all_in_one_file": "yes",
            "remove_duplicate": "yes",
            "name": "synth_data",
            "enrichment": "yes",
            "large_file": "no",
            "ordered": "yes",
            "dbType": "mysql"
        },
        "dataset1": {
            "name": "synth_data",
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "paladin",
            "db": "synth",
            "mapping": "${default:main_directory}/mapping.ttl"
        }
    }
    semantify(rdfizer_config)

    db_cur.close()
    db_con.close()
    print("Finished generating the synthetic data. Total time:", time.time() - start)
