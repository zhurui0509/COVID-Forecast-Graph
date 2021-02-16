#### This is the code to triplify the EconomicTracker  ####

import rdflib
import csv 
import pandas as pd
import pickle
import json
import requests


#from qwikidata.sparql  import return_sparql_query_results

from rdflib.namespace import CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL, \
                           PROF, PROV, RDF, RDFS, SDO, SH, SKOS, SOSA, SSN, TIME, \
                           VOID, XMLNS, XSD
from rdflib import Namespace
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from datetime import datetime, timedelta
import os
from glob import glob

SOSA = SSN

today = datetime.today()
today_str = today.strftime("%Y-%m-%d") # dd/mm/YY




def FIPS_normalizer(FIPS_old, state_N, county_N):
    #state_N : 1 or 2  --> example: 6 or 06 for California (for most of cases it is always 2)
    #county_N: 4 or 5  --> example: 6083 or 06083 for Santa Barbara County (for most cases, it is alwasys 5)
    FIPS_len = len(FIPS_old)
    if FIPS_len < 3:
        if state_N == 1:
            if FIPS_old[0] == '0':
                FIPS_new = FIPS_old[1:]
            else:
                FIPS_new = FIPS_old
        else:
            if FIPS_len == 1:
                FIPS_new = '0'+FIPS_old
            else:
                FIPS_new = FIPS_old
    else:
        if county_N == 4:
            if FIPS_old[0] == '0':
                FIPS_new = FIPS_old[1:]
            else:
                FIPS_new = FIPS_old
        else:
            if FIPS_len == 4:
                FIPS_new = '0'+FIPS_old
            else:
                FIPS_new = FIPS_old
    return FIPS_new 

def loadCSV(fileName, column_list):
    #header = ['year','month','day','cityid','spend_acf','spend_aer','spend_all','spend_apg','spend_grf','spend_hcs','spend_tws']
    header = column_list
    data = pd.read_csv(fileName)
    data = data[header]

    result = [list(row) for row in data.values]
    return result

def numeric_conversion(value):
    if value == ".":
        value = 0
    elif '.' in str(value):
        value = str(value).replace('.', '0.')
    return value

def triplify_econ_stats_collection(city, time, members, graph, subject):
    econ = Namespace("http://econ.geog.ucsb.edu/lod/economy/")
    covid_instant = Namespace("http://covid.geog.ucsb.edu/lod/instant/")
    covid_place =Namespace("http://covid.geog.ucsb.edu/lod/place/")

    graph.add((subject, RDF.type, econ['StatsCollection']))
    graph.add((subject, SOSA.hasFeatureOfInterest, covid_place[city]))
    graph.add((subject, SOSA.phenomenonTime, covid_instant[time]))

    for member in members:
        graph.add((subject, SOSA.hasMember, member))

    #graph.add((subject,  SOSA.observedProperty, econ_obs_property['spend_'+obs_property]))
    #graph.add((subject, covid['point'], Literal(float(point_value)))) ### the predicate can be sosa:hasSimpleResult

def triplify_obs_instances(obs_property, point_value, graph, subject):
    econ = Namespace("http://econ.geog.ucsb.edu/lod/economy/")
    econ_obs_property = Namespace("http://econ.geog.ucsb.edu/lod/observedproperty/") 

    graph.add((subject, RDF.type, econ['Stats']))
    graph.add((subject, SOSA.observedProperty, econ_obs_property[obs_property]))
    graph.add((subject, econ['point'], Literal(float(point_value)))) ### the predicate can be sosa:hasSimpleResult


def triplify_obs_property(obs_property, label, graph):
    econ_obs_property = Namespace("http://econ.geog.ucsb.edu/lod/observedproperty/") 

    subject = econ_obs_property[obs_property]
    graph.add((subject, RDF.type, SOSA.ObservableProperty))
    graph.add((subject, RDFS.label, Literal(label)))

def triplify_economy(source_name, data_file, column_list, temporal_resolution, source_stat_label, obs_prop_label_dic):
    ## columne_list: (we only considers state and national level)
    ## Examples:
    ## State - year,month,day,statefips,spend_acf,spend_aer,spend_all,spend_apg,spend_grf,spend_hcs,spend_tws,spend_all_inchigh,spend_all_inclow,spend_all_incmiddle
    ## National - year, month, day, spend_acf, spend_aer, spend_all, spend_apg, spend_grf, spend_hcs, spend_tws, spend_all_inchigh, spend_all_inclow, spend_all_incmiddle
    ## (not considered for now) County - year,month,day,countyfips,spend_all
    ## temporal_resolution: weekly, daily
    source_name_lower = source_name.lower() # lower is to put into the url

    covid_instant = Namespace("http://covid.geog.ucsb.edu/lod/instant/")
    covid_interval = Namespace("http://covid.geog.ucsb.edu/lod/interval/")

    covid_place =Namespace("http://covid.geog.ucsb.edu/lod/place/")

    econ = Namespace("http://econ.geog.ucsb.edu/lod/economy/")
    econ_obs_property = Namespace("http://econ.geog.ucsb.edu/lod/observedproperty/") 

    econ_source = Namespace("http://econ.geog.ucsb.edu/lod/" +source_name_lower+"/")
    econ_source_stat_collection = Namespace("http://econ.geog.ucsb.edu/lod/" +source_name_lower+"_stat_collection/" )
    econ_source_stat = Namespace("http://econ.geog.ucsb.edu/lod/"  + source_name_lower + "_stat/")
    
    econ_g = Graph()
    econ_g.bind('econ', econ)
    econ_g.bind('econ-obs-property', econ_obs_property)

    econ_g.bind('covid-place', covid_place)
    econ_g.bind('covid-instant', covid_instant)
    econ_g.bind('covid-interval', covid_interval)
    econ_g.bind('econ-'+source_name_lower, econ_source)
    econ_g.bind('econ-'+source_name_lower+'-stat-collection', econ_source_stat_collection)
    econ_g.bind('econ-'+source_name_lower+'-stat', econ_source_stat)

    econ_g.bind('rdf', RDF)
    econ_g.bind('rdfs', RDFS)
    econ_g.bind('xsd', XSD)
    econ_g.bind('owl', OWL)
    econ_g.bind('time', TIME)
    econ_g.bind('sosa', SOSA)

    data_dir = '../EconomicTracker/data/'

    data_df = pd.read_csv(data_dir + data_file)
    data_df= data_df.applymap(lambda x: str(numeric_conversion(x)))

    data_list = data_df.values.tolist()

    output = data_file.replace(" - ", "_")
    output = '../output_economy/'+output.replace(".csv", ".ttl")


    # step1: build the EconomicTracker level observation collection 
    if 'statefips' in column_list: ## for state-level
        econTracker_url = 'state-'+temporal_resolution
        
    else: ## for national-level 
        econTracker_url = 'national-'+ temporal_resolution

    econ_g.add((econ_source[econTracker_url], RDF.type, econ['EconomicTracker']))
    econ_g.add((econ_source[econTracker_url], SOSA.resultTime, Literal(today_str)))
    econ_g.add((econ_source[econTracker_url], RDFS.label, Literal(source_stat_label)))

    if '_' in source_name:
        source_name_list = source_name.split('_')
        for source_name_item in source_name_list:
            econ_g.add((econ_source[econTracker_url], SOSA.madeBySensor, econ[source_name_item]))
    else:
        econ_g.add((econ_source[econTracker_url], SOSA.madeBySensor, econ[source_name]))

    # step2: build the StatsCollection level observation collection 
    date_list = []
    
    for item in data_list:
        year = item[0]
        month = item [1]
        day = item[2]
        date = datetime(int(year), int(month), int(day))
        date = date.strftime("%Y-%m-%d")
        date_list.append(date)

        if 'statefips' in column_list:
            place_id = FIPS_normalizer(str(item[3]), 2, 5)
            #place_url = str(date)+'-'+source_name_lower+'-state-'+temporal_resolution'-'+str(place_id)
            place_url = str(date)+'-state-'+temporal_resolution+'-'+str(place_id)
        else: 
            place_id = 'US'
            #place_url = str(date)+'-'+source_name_lower+'-national-'+temporal_resolution'-US'
            place_url = str(date)+'-national-'+temporal_resolution+'-US'

        statsCollection_url = econ_source_stat_collection[place_url]
        econ_g.add((econ_source[econTracker_url], SOSA.hasMember, statsCollection_url))

        # step3: build the Stats level observations
        statsCollection_members = []

        for variable in obs_prop_label_dic:
            try:
                variable_index = column_list.index(variable)
                value = item[variable_index]

                variable_url = place_url + '-' + variable
                stats_url = econ_source_stat[variable_url]

                statsCollection_members.append(stats_url)

                triplify_obs_instances(variable, value, econ_g, stats_url)
            except:
                continue
                #print('%s is not in the list for this data' %(variable))



        triplify_econ_stats_collection(place_id, date, statsCollection_members, econ_g, statsCollection_url)

    # step 4: build the observed property tripes
    for var, des in obs_prop_label_dic.items():
        triplify_obs_property(var, des, econ_g)

    # step 5: build the time instances --> it might not be necessary as the covid-19 prediction already has it 
    date_set = set(date_list)
    if temporal_resolution =='daily':
        for date_item in date_list:
            #econ_g.add(covid_instant[date_time], RDF.type, covid['Instant'] )
            econ_g.add((covid_instant[str(date_item)], RDF.type, TIME.Instant ))
            econ_g.add((covid_instant[str(date_item)], TIME.inXSDDateTime, Literal(date_item) ))
    else:
        for date_item in date_list:
            end = datetime.strptime(date_item, '%Y-%m-%d')
            start = end - timedelta(days=6)
            end = end.strftime('%Y-%m-%d')
            start = start.strftime('%Y-%m-%d')
            end_str = end +'-weekly'

            econ_g.add((covid_instant[str(start)], RDF.type, TIME.Instant))
            econ_g.add((covid_instant[str(start)], TIME.inXSDDateTime, Literal(start)))
            econ_g.add((covid_instant[str(end)], RDF.type, TIME.Instant))
            econ_g.add((covid_instant[str(end)], TIME.inXSDDateTime, Literal(end)))

            econ_g.add((covid_interval[end_str], RDF.type, TIME.Interval))
            econ_g.add((covid_interval[end_str], TIME.hasBeginning, covid_instant[start]))
            econ_g.add((covid_interval[end_str], TIME.hasEnd, covid_instant[end]))
            


    econ_g.serialize(destination=output, format='turtle')
    print('Finished triplifying')



def main():

    # #### Triplify Affinity Data #######
    # print('Start triplifying Affinity')
    # source_name = 'Affinity'
    # data_file = ["Affinity - State - Daily.csv", 'Affinity - National - Daily.csv']
    # column_list_state = ['year','month','day','statefips','freq','spend_acf','spend_aer','spend_all','spend_apg','spend_grf','spend_hcs',
    # 'spend_tws','spend_all_inchigh','spend_all_inclow','spend_all_incmiddle']
    # column_list_national = ['year', 'month', 'day', 'freq','spend_acf', 'spend_aer', 'spend_all', 'spend_apg', 'spend_grf', 'spend_hcs', 
    # 'spend_tws', 'spend_all_inchigh', 'spend_all_inclow', 'spend_all_incmiddle']
    
    # source_stat_label_state = 'State level aggregated and anonymized purchase data from consumer credit and debit card spending. Spending is reported based on the ZIP code where the cardholder lives, not the ZIP code where transactions occurred.'
    # source_stat_label_national = 'National level aggregated and anonymized purchase data from consumer credit and debit card spending. Spending is reported based on the ZIP code where the cardholder lives, not the ZIP code where transactions occurred.'

    # temporal_resolution = 'daily'

    # obs_prop_label_dic ={'spend_acf': "Seasonally adjusted credit/debit card spending relative to January 4-31 2020 in accomodation and food service (ACF) MCCs, 7 day moving average, 7 day moving average.",
    #                     'spend_aer': "Seasonally adjusted credit/debit card spending relative to January 4-31 2020 in arts, entertainment, and recreation (AER) MCCs, 7 day moving average",
    #                     'spend_all': "Seasonally adjusted credit/debit card spending relative to January 4-31 2020 in all merchant category codes (MCC), 7 day moving average.",
    #                     'spend_apg': "Seasonally adjusted credit/debit card spending relative to January 4-31 2020 in general merchandise stores (GEN) and apparel and accessories (AAP) MCCs, 7 day moving average.",
    #                     'spend_grf': "Seasonally adjusted credit/debit card spending relative to January 4-31 2020 in grocery and food store (GRF) MCCs, 7 day moving average.",
    #                     'spend_hcs': "Seasonally adjusted credit/debit card spending relative to January 4-31 2020 in health care and social assistance (HCS) MCCs, 7 day moving average.",
    #                     'spend_tws': "Seasonally adjusted credit/debit card spending relative to January 4-31 2020 in transportation and warehousing (TWS) MCCs, 7 day moving average.",
    #                     'spend_all_inchigh': "Seasonally adjusted credit/debit card spending by consumers living in ZIP codes with high (top quartile) median income, relative to January 4-31 2020 in all merchant category codes (MCC), 7 day moving average.",
    #                     'spend_all_inclow': "Seasonally adjusted credit/debit card spending by consumers living in ZIP codes with middle (middle two quartiles) median income, relative to January 4-31 2020 in all merchant category codes (MCC), 7 day moving average.",
    #                     'spend_all_incmiddle': "Seasonally adjusted credit/debit card spending by consumers living in ZIP codes with low (bottom quartiles) median income, relative to January 4-31 2020 in all merchant category codes (MCC), 7 day moving average."}
    
    # triplify_economy(source_name, data_file[0], column_list_state, temporal_resolution, source_stat_label_state, obs_prop_label_dic)
    # triplify_economy(source_name, data_file[1], column_list_national, temporal_resolution, source_stat_label_national, obs_prop_label_dic)

    # ###### Triplify Burning Glass Data 
    # print('Start triplifying Burning Glass')
    # source_name = 'BurningGlass'
    # data_file = ["Burning Glass - National - Weekly.csv", 'Burning Glass - State - Weekly.csv']
    # column_list_state = ['year', 'month',  'day_endofweek',  'statefips',  'bg_posts', 'bg_posts_ss30', 'bg_posts_ss55',
    #  'bg_posts_ss60', 'bg_posts_ss65', 'bg_posts_ss70', 'bg_posts_jz1','bg_posts_jzgrp12','bg_posts_jz2', 'bg_posts_jz3', 'bg_posts_jzgrp345', 'bg_posts_jz4','bg_posts_jz5']
    # column_list_national = ['year', 'month',  'day_endofweek', 'bg_posts', 'bg_posts_ss30', 'bg_posts_ss55',
    #  'bg_posts_ss60', 'bg_posts_ss65', 'bg_posts_ss70', 'bg_posts_jz1','bg_posts_jzgrp12','bg_posts_jz2', 'bg_posts_jz3', 'bg_posts_jzgrp345', 'bg_posts_jz4','bg_posts_jz5']
    # source_stat_label_state = "State level weekly count of new job postings, sourced from over 40,000 online job boards. New job postings are defined as those that have not had a duplicate posting for at least 60 days prior."
    # source_stat_label_national = "National level state level weekly count of new job postings, sourced from over 40,000 online job boards. New job postings are defined as those that have not had a duplicate posting for at least 60 days prior."

    # temporal_resolution = 'weekly' 

    # obs_prop_label_dic = {"bg_posts": "Average level of job postings relative to January 4-31 2020.",
    #                 "bg_posts_ss30": 'Average level of job postings relative to January 4-31 2020 in manufacturing (NAICS supersector 30).',
    #                 "bg_posts_ss55": 'Average level of job postings relative to January 4-31 2020 in financial activities (NAICS supersector 55).',
    #                 "bg_posts_ss60": 'Average level of job postings relative to January 4-31 2020 in professional and business services (NAICS supersector 60).',
    #                 "bg_posts_ss65": 'Average level of job postings relative to January 4-31 2020 in education and health services (NAICS supersector 65).',
    #                 "bg_posts_ss70": 'Average level of job postings relative to January 4-31 2020 in leisure and hospitality (NAICS supersector 70).',
    #                 "bg_posts_jz1": 'Average level of job postings relative to January 4-31 2020 requiring little/no preparation (ONET jobzone level 1).',
    #                 "bg_posts_jz2": 'Average level of job postings relative to January 4-31 2020 requiring some preparation (ONET jobzone level 2).',
    #                 'bg_posts_jz3': 'Average level of job postings relative to January 4-31 2020 requiring medium preparation (ONET jobzone level 3).',
    #                 'bg_posts_jz4': 'Average level of job postings relative to January 4-31 2020 requiring considerable preparation (ONET jobzone level 4).',
    #                 'bg_posts_jz5': 'Average level of job postings relative to January 4-31 2020 requiring extensive preparation (ONET jobzone level 5).',
    #                 'bg_posts_jzgrp12': 'Average level of job postings relative to January 4-31 2020 requiring low preparation (ONET jobzone levels 1 and 2).',
    #                 'bg_posts_jzgrp345': 'Average level of job postings relative to January 4-31 2020 requiring high preparation (ONET jobzone levels 3, 4 and 5).'}

    # triplify_economy(source_name, data_file[0], column_list_national, temporal_resolution, source_stat_label_national, obs_prop_label_dic)
    # triplify_economy(source_name, data_file[1], column_list_state, temporal_resolution, source_stat_label_state, obs_prop_label_dic)

   

   ######## Triplify Womply Data  (opening data - both Merchants and Revenue)  ###############

    print('Start triplifying Womply data')
    source_name = 'WomplyMerchants'
    data_file = ["Womply - National - Daily.csv", 'Womply - State - Daily.csv']
    column_list_state = ['year','month','day','statefips','merchants_all','merchants_inchigh','merchants_inclow','merchants_incmiddle','merchants_ss40','merchants_ss60','merchants_ss65','merchants_ss70',
                        'revenue_all','revenue_inchigh','revenue_inclow','revenue_incmiddle','revenue_ss40','revenue_ss60','revenue_ss65','revenue_ss70']
    column_list_national = ['year', 'month', 'day merchants_all', 'merchants_inchigh', 'merchants_inclow','merchants_incmiddle','merchants_ss40', 'merchants_ss60',  
                            'merchants_ss65', 'merchants_ss70',  'revenue_all', 'revenue_inchigh', 'revenue_inclow', 'revenue_incmiddle', 'revenue_ss40','revenue_ss60', 'revenue_ss65','revenue_ss70']
    source_stat_label_state = "State level number of small businesses open, as defined by having had at least one transaction in the previous 3 days."
    source_stat_label_national = "National level number of small businesses open, as defined by having had at least one transaction in the previous 3 days."

    temporal_resolution = 'daily' 

    obs_prop_label_dic = {"merchants_all": "Percent change in number of small businesses open calculated as a seven-day moving average seasonally adjusted and indexed to January 4-31 2020.",
"merchants_inchigh": "Percent change in number of small businesses open calculated as a seven-day moving average seasonally adjusted and indexed to January 4-31 2020 in high income (quartile 4 of median income) ZIP codes.",
"merchants_incmiddle": "Percent change in number of small businesses open calculated as a seven-day moving average seasonally adjusted and indexed to January 4-31 2020 in middle income (quartiles 2 & 3 of median income) ZIP codes.",
"merchants_inclow": "Percent change in number of small businesses open calculated as a seven-day moving average seasonally adjusted and indexed to January 4-31 2020 in low income (quartile 1 of median income) ZIP codes.",
"merchants_ss40": "Percent change in number of small businesses open calculated as a seven-day moving average seasonally adjusted and indexed to January 4-31 2020 in transportation (NAICS supersector 40).",
"merchants_ss60": "Percent change in number of small businesses open calculated as a seven-day moving average seasonally adjusted and indexed to January 4-31 2020 in professional and business services (NAICS supersector 60).",
"merchants_ss65": "Percent change in number of small businesses open calculated as a seven-day moving average seasonally adjusted and indexed to January 4-31 2020 in education and health services (NAICS supersector 65).",
"merchants_ss70": "Percent change in number of small businesses open calculated as a seven-day moving average seasonally adjusted and indexed to January 4-31 2020 in leisure and hospitality (NAICS supersector 70).",
"revenue_all": "Percent change in net revenue for small businesses, calculated as a seven-day moving average, seasonally adjusted, and indexed to January 4-31 2020.",
"revenue_inchigh": "Percent change in net revenue for small businesses, calculated as a seven-day moving average, seasonally adjusted, and indexed to January 4-31 2020 in high income (quartile 4 of median income) zipcodes.",
"revenue_incmiddle": "Percent change in net revenue for small businesses, calculated as a seven-day moving average, seasonally adjusted, and indexed to January 4-31 2020 in middle income (quartiles 2 & 3 of median income) zipcodes.",
"revenue_inclow": "Percent change in net revenue for small businesses, calculated as a seven-day moving average, seasonally adjusted, and indexed to January 4-31 2020 in low income (quartile 1 of median income) zipcodes.",
"revenue_ss40": "Percent change in net revenue for small businesses, calculated as a seven-day moving average, seasonally adjusted, and indexed to January 4-31 2020 in transportation (NAICS supersector 40).",
"revenue_ss60": "Percent change in net revenue for small businesses, calculated as a seven-day moving average, seasonally adjusted, and indexed to January 4-31 2020 in professional and business services (NAICS supersector 60).",
"revenue_ss65": "Percent change in net revenue for small businesses, calculated as a seven-day moving average, seasonally adjusted, and indexed to January 4-31 2020 in education and health services (NAICS supersector 65).",
"revenue_ss70": "Percent change in net revenue for small businesses, calculated as a seven-day moving average, seasonally adjusted, and indexed to January 4-31 2020 in leisure and hospitality (NAICS supersector 70)."}

    triplify_economy(source_name, data_file[0], column_list_national, temporal_resolution, source_stat_label_national, obs_prop_label_dic)
    triplify_economy(source_name, data_file[1], column_list_state, temporal_resolution, source_stat_label_state, obs_prop_label_dic)



  

   # ######## Triplify Womply Merchants Data  (opening data)
   #  print('Start triplifying Womply Merchants')
   #  source_name = 'WomplyMerchants'
   #  data_file = ["Womply Merchants - National - Daily.csv", 'Womply Merchants - State - Daily.csv']
   #  column_list_state = ['year','month','day','statefips','merchants_all','merchants_ss40','merchants_ss60','merchants_ss65','merchants_ss70']
   #  column_list_national = ['year','month','day','merchants_all','merchants_ss40','merchants_ss60','merchants_ss65','merchants_ss70']
   #  source_stat_label_state = "State level number of small businesses open, as defined by having had at least one transaction in the previous 3 days."
   #  source_stat_label_national = "National level Number of small businesses open, as defined by having had at least one transaction in the previous 3 days."

   #  temporal_resolution = 'daily' 

   #  obs_prop_label_dic = {"merchants_all": "Percent change in number of small businesses open calculated as a seven-day moving average seasonally adjusted and indexed to January 4-31 2020.",
   #                       "merchants_ss40": "Percent change in number of small businesses open calculated as a seven-day moving average seasonally adjusted and indexed to January 4-31 2020 in transportation (NAICS supersector 40).",
   #                      "merchants_ss60": "Percent change in number of small businesses open calculated as a seven-day moving average seasonally adjusted and indexed to January 4-31 2020 in professional and business services (NAICS supersector 60).",
   #                      "merchants_ss65": "Percent change in number of small businesses open calculated as a seven-day moving average seasonally adjusted and indexed to January 4-31 2020 in education and health services (NAICS supersector 65).",
   #                      "merchants_ss70": "Percent change in number of small businesses open calculated as a seven-day moving average seasonally adjusted and indexed to January 4-31 2020 in leisure and hospitality (NAICS supersector 70)."}

   #  triplify_economy(source_name, data_file[0], column_list_national, temporal_resolution, source_stat_label_national, obs_prop_label_dic)
   #  triplify_economy(source_name, data_file[1], column_list_state, temporal_resolution, source_stat_label_state, obs_prop_label_dic)

   # ######## Triplify Womply Revenue Data  (revenue data)
   #  print('Start triplifying Womply Revenue')
   #  source_name = 'WomplyRevenue'
   #  data_file = ["Womply Revenue - National - Daily.csv", 'Womply Revenue - State - Daily.csv']
   #  column_list_state = ['year','month','day','statefips', 'revenue_all','revenue_ss40','revenue_ss60','revenue_ss65','revenue_ss70']
   #  column_list_national = ['year','month','day','merchants_all','revenue_all','revenue_ss40','revenue_ss60','revenue_ss65','revenue_ss70']
   #  source_stat_label_state = "State level small business transactions and revenue data aggregated from several credit card processors. Transactions and revenue are reported based on the ZIP code where the business is located."
   #  source_stat_label_national = "National level Small business transactions and revenue data aggregated from several credit card processors. Transactions and revenue are reported based on the ZIP code where the business is located."

   #  temporal_resolution = 'daily' 

   #  obs_prop_label_dic = {"merchants_all": "Percent change in net revenue for small businesses, calculated as a seven-day moving average, seasonally adjusted, and indexed to January 4-31 2020.",
   #                       "merchants_ss40": "Percent change in net revenue for small businesses, calculated as a seven-day moving average, seasonally adjusted, and indexed to January 4-31 2020 in transportation (NAICS supersector 40).",
   #                      "merchants_ss60": "Percent change in net revenue for small businesses, calculated as a seven-day moving average, seasonally adjusted, and indexed to January 4-31 2020 in professional and business services (NAICS supersector 60).",
   #                      "merchants_ss65": "Percent change in net revenue for small businesses, calculated as a seven-day moving average, seasonally adjusted, and indexed to January 4-31 2020 in education and health services (NAICS supersector 65).",
   #                      "merchants_ss70": "Percent change in net revenue for small businesses, calculated as a seven-day moving average, seasonally adjusted, and indexed to January 4-31 2020 in leisure and hospitality (NAICS supersector 70)."}

   #  triplify_economy(source_name, data_file[0], column_list_national, temporal_resolution, source_stat_label_national, obs_prop_label_dic)
   #  triplify_economy(source_name, data_file[1], column_list_state, temporal_resolution, source_stat_label_state, obs_prop_label_dic)

    ######## Triplify  Paychex, Intuit, Earnin and Kronos (employment)
    print('Start triplifying Employment')
    source_name = 'Aychex_Intuit_Earnin_Kronos'
    data_file = ["Employment Combined - National - Daily.csv", 'Employment Combined - State - Daily.csv']
    column_list_state = ['year','month','day','statefips','emp_combined','emp_combined_inclow','emp_combined_incmiddle','emp_combined_inchigh',
    'emp_combined_ss40','emp_combined_ss60','emp_combined_ss65','emp_combined_ss70']
    column_list_national = ['year', 'month', 'day', 'emp_combined', 'emp_combined_inclow', 'emp_combined_incmiddle', 'emp_combined_inchigh',
    'emp_combined_ss40', 'emp_combined_ss60','emp_combined_ss65',  'emp_combined_ss70',  'emp_combined_inclow_advance']
    source_stat_label_state = "State level number of active employees, aggregating information from multiple data providers. This series is based on firm-level payroll data from Paychex and Intuit, worker-level data on employment and earnings from Earnin, and firm-level timesheet data from Kronos."
    source_stat_label_national = "National level number of active employees, aggregating information from multiple data providers. This series is based on firm-level payroll data from Paychex and Intuit, worker-level data on employment and earnings from Earnin, and firm-level timesheet data from Kronos."
    
    temporal_resolution = 'daily' 

    obs_prop_label_dic = {'emp_combined': 'Employment level for all workers.',
                        'emp_combined_inclow': 'Employment level for workers in the bottom quartile of the income distribution (incomes approximately under $27,000).',
                        'emp_combined_incmiddle': 'Employment level for workers in the middle two quartiles of the income distribution (incomes approximately $27,000 to $60,000).',
                        'emp_combined_inchigh': 'Employment level for workers in the top quartile of the income distribution (incomes approximately over $60,000).',
                        'emp_combined_ss40': 'Employment level for workers in trade, transportation and utilities (NAICS supersector 40).',
                        'emp_combined_ss60': 'Employment level for workers in professional and business services (NAICS supersector 60).',
                        'emp_combined_ss65': 'Employment level for workers in education and health services (NAICS supersector 65).',
                        'emp_combined_ss70': 'Employment level for workers in leisure and hospitality (NAICS supersector 70).',
                        'emp_combined_inclow_advance': 'Indicator (0 or 1) for whether emp_combined_inclow is a forecasted employment level based on timecard data from Kronos.'}

    triplify_economy(source_name, data_file[0], column_list_national, temporal_resolution, source_stat_label_national, obs_prop_label_dic)
    triplify_economy(source_name, data_file[1], column_list_state, temporal_resolution, source_stat_label_state, obs_prop_label_dic)


if __name__ == "__main__":
    main()
