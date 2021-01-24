#### This is the code to triplify the EconomicTracker  ####

import rdflib
import csv 
import pandas as pd
import pickle
import json
import requests
import datetime


#from qwikidata.sparql  import return_sparql_query_results

from rdflib.namespace import CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL, \
                           PROF, PROV, RDF, RDFS, SDO, SH, SKOS, SOSA, SSN, TIME, \
                           VOID, XMLNS, XSD
from rdflib import Namespace
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from datetime import datetime
import os
from glob import glob

today = datetime.today()

# dd/mm/YY
today_str = today.strftime("%Y-%m-%d")

covid = Namespace("http://covid.geog.ucsb.edu/lod/ontology/")
covid_spending = Namespace("http://covid.geog.ucsb.edu/lod/spending/")
covid_instant = Namespace("http://covid.geog.ucsb.edu/lod/instant/")
covid_place =Namespace("http://covid.geog.ucsb.edu/lod/place/")
econ = Namespace("http://econ.geog.ucsb.edu/lod/economy/")
econ_model = Namespace("http://covid.geog.ucsb.edu/lod/economic-model/")
econ_obs_property = Namespace("http://covid.geog.ucsb.edu/lod/econ_obs_property/") 
econ_spending = Namespace("http://covid.geog.ucsb.edu/lod/spending/")  ## for affinity data 
econ_spending_stat = Namespace("http://covid.geog.ucsb.edu/lod/spending_stat/") 
econ_spending_stat_collection = Namespace("http://covid.geog.ucsb.edu/lod/spending_stat_collection/") 
econ_burning_glass = Namespace("http://covid.geog.ucsb.edu/lod/job-posting") 
econ_model = Namespace("http://covid.geog.ucsb.edu/lod/economic-model/")

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

def loadCSV_Afinity_City_Daily(fileName):
    header = ['year','month','day','cityid','spend_acf','spend_aer','spend_all','spend_apg','spend_grf','spend_hcs','spend_tws']
    data = pd.read_csv(fileName)
    data = data[header]

    afinity_city = [list(row) for row in data.values]
    return afinity_city

def loadCSV_Afinity_National_Daily(fileName):
    header = ['year','month','day','spend_acf','spend_aer','spend_all','spend_apg','spend_grf','spend_hcs','spend_tws', 'spend_all_inchigh','spend_all_inclow', 'spend_all_incmiddle']
    data = pd.read_csv(fileName)
    data = data[header]

    afinity_national = [list(row) for row in data.values]
    return afinity_national

def loadCSV_Afinity_County_Daily(fileName):
    header = ['year','month','day','countyfips','spend_all']
    data = pd.read_csv(fileName)
    data = data[header]

    afinity_national = [list(row) for row in data.values]
    return afinity_national

def loadCSV_Afinity_State_Daily(fileName):
    header = ['year','month','day','statefips','spend_acf','spend_aer','spend_all','spend_apg','spend_grf','spend_hcs','spend_tws','spend_all_inchigh','spend_all_inclow','spend_all_incmiddle']
    data = pd.read_csv(fileName)
    data = data[header]

    afinity_state = [list(row) for row in data.values]
    return afinity_state

def numeric_conversion(value):
    if value == ".":
        value = 0
    elif '.' in str(value):
        value = str(value).replace('.', '0.')
    return value

def triplify_obs_collection(city, time, members, graph, subject):
    graph.add((subject, RDF.type, econ['StatsCollection']))
    graph.add((subject, SOSA.hasFeatureOfInterest, covid_place[city]))
    graph.add((subject, SOSA.phenomenonTime, covid_instant[time]))

    for member in members:
        graph.add((subject, SOSA.hasMember, member))

    #graph.add((subject,  SOSA.observedProperty, econ_obs_property['spend_'+obs_property]))
    #graph.add((subject, covid['point'], Literal(float(point_value)))) ### the predicate can be sosa:hasSimpleResult

def triplify_obs_instances(obs_property, point_value, graph, subject):
    graph.add((subject, SOSA.observedProperty, econ_obs_property['spend_'+obs_property]))
    graph.add((subject, covid['point'], Literal(float(point_value)))) ### the predicate can be sosa:hasSimpleResult


def triplify_obs_property(obs_property, label, graph):
    subject = econ_obs_property['spend_'+obs_property]
    graph.add((subject, RDF.type, SOSA.ObservableProperty))
    graph.add((subject, RDFS.label, Literal(label)))

def triplify_affinity(affinity_data, output):

    affinity_g = Graph()
    affinity_g.bind('econ', econ)
    affinity_g.bind('covid', covid)
    affinity_g.bind('econ-spending', econ_spending)
    affinity_g.bind('econ-spending-stat', econ_spending_stat)
    affinity_g.bind('covid-place', covid_place)
    affinity_g.bind('covid-instant', covid_instant)
    affinity_g.bind('econ-obs-property', econ_obs_property)
    affinity_g.bind('econ-model', econ_model)
    affinity_g.bind('econ-spending-stat-collection',econ_spending_stat_collection)

    affinity_g.bind('rdf', RDF)
    affinity_g.bind('rdfs', RDFS)
    affinity_g.bind('xsd', XSD)
    affinity_g.bind('owl', OWL)
    affinity_g.bind('time', TIME)
    affinity_g.bind('sosa', SOSA)


    #n_column = len(affinity_data.columns)
    n_column = len(affinity_data[0])



    spend_city_daily =  "affinity-city-daily"
    spend_national_daily = "affinity-national-daily"
    spend_county_daily = "affinity-county-daily"
    spend_state_daily = "affinity-sate-daily"

    # affinity_g.add((econ_spending[spend_city_daily], RDF.type, econ['EconomicSpending']))
    # affinity_g.add((econ_spending[spend_city_daily], SOSA.resultTime, Literal(today_str)))
    # affinity_g.add((econ_spending[spend_city_daily], SOSA.madeBySensor, econ_model['Affinity']))
    # spend_city_daily_label = "City level daily speding data collected from Affinity"
    # affinity_g.add((econ_spending[spend_city_daily], RDFS.label, spend_city_daily_label))

    affinity_g.add((econ_spending[spend_national_daily], RDF.type, econ['EconomicSpending']))
    affinity_g.add((econ_spending[spend_national_daily], SOSA.resultTime, Literal(today_str)))
    affinity_g.add((econ_spending[spend_national_daily], SOSA.madeBySensor, econ_model['Affinity']))
    spend_national_daily_label = "National level daily speding data collected from Affinity"
    affinity_g.add((econ_spending[spend_national_daily], RDFS.label, Literal(spend_national_daily_label)))

    affinity_g.add((econ_spending[spend_county_daily], RDF.type, econ['EconomicSpending']))
    affinity_g.add((econ_spending[spend_county_daily], SOSA.resultTime, Literal(today_str)))
    affinity_g.add((econ_spending[spend_county_daily], SOSA.madeBySensor, econ_model['Affinity']))
    spend_county_daily_label = "County level daily speding data collected from Affinity"
    affinity_g.add((econ_spending[spend_county_daily], RDFS.label, Literal(spend_county_daily_label)))

    affinity_g.add((econ_spending[spend_state_daily], RDF.type, econ['EconomicSpending']))
    affinity_g.add((econ_spending[spend_state_daily], SOSA.resultTime, Literal(today_str)))
    affinity_g.add((econ_spending[spend_state_daily], SOSA.madeBySensor, econ_model['Affinity']))
    spend_state_daily_label = "State level daily speding data collected from Affinity"
    affinity_g.add((econ_spending[spend_state_daily], RDFS.label, Literal(spend_state_daily_label)))


    ### addig observedProperty instances 
    acf_label ="Seasonally adjusted credit/debit card spending relative to January 4-31 2020 in accomodation and food service (ACF) MCCs, 7 day moving average"
    all_label = "Seasonally adjusted credit/debit card spending relative to January 4-31 2020 in all merchant category codes (MCC), 7 day moving average"
    aer_label = "Seasonally adjusted credit/debit card spending relative to January 4-31 2020 in arts, entertainment, and recreation (AER) MCCs, 7 day moving average"
    apg_label = "Seasonally adjusted credit/debit card spending relative to January 4-31 2020 in general merchandise stores (GEN) and apparel and accessories (AAP) MCCs, 7 day moving average"
    grf_label = "Seasonally adjusted credit/debit card spending relative to January 4-31 2020 in grocery and food store (GRF) MCCs, 7 day moving average"
    hcs_label = "Seasonally adjusted credit/debit card spending relative to January 4-31 2020 in health care and social assistance (HCS) MCCs, 7 day moving average"
    tws_label = "Seasonally adjusted credit/debit card spending relative to January 4-31 2020 in transportation and warehousing (TWS) MCCs, 7 day moving average"
    all_inchigh_label = "Seasonally adjusted credit/debit card spending by consumers living in ZIP codes with high (top quartile) median income, relative to January 4-31 2020 in all merchant category codes (MCC), 7 day moving average"
    all_incmiddle_label = "Seasonally adjusted credit/debit card spending by consumers living in ZIP codes with middle (middle two quartiles) median income, relative to January 4-31 2020 in all merchant category codes (MCC), 7 day moving average"
    all_inclow_label = "Seasonally adjusted credit/debit card spending by consumers living in ZIP codes with low (bottom quartiles) median income, relative to January 4-31 2020 in all merchant category codes (MCC), 7 day moving average"

    triplify_obs_property('acf', acf_label, affinity_g)
    triplify_obs_property('all', all_label, affinity_g)
    triplify_obs_property('aer', aer_label, affinity_g)
    triplify_obs_property('apg', apg_label, affinity_g)
    triplify_obs_property('grf', grf_label, affinity_g)
    triplify_obs_property('hcs', hcs_label, affinity_g)
    triplify_obs_property('tws', tws_label, affinity_g)
    triplify_obs_property('all_inchigh', all_inchigh_label, affinity_g)
    triplify_obs_property('all_incmiddle', all_incmiddle_label, affinity_g)
    triplify_obs_property('all_inclow', all_inclow_label, affinity_g)

    date_list = []
    
    for item in affinity_data:
        year = item[0]
        month = item [1]
        day = item[2]
        date = datetime(int(year), int(month), int(day))
        date = date.strftime("%Y-%m-%d")
        date_list.append(date)

        if n_column == 11:
            city_id = str(item[3])
            city_str = 'City-'+str(city_id)
            spend_acf = item[4]
            spend_aer = item[5]
            spend_all = item[6]
            spend_apg = item[7]
            spend_grf = item[8]
            spend_hcs = item[9]
            spend_tws = item[10]

            spend_str = str(date)+"-affinity-city-daily-"+city_str
            spend_str_acf = str(date)+"-affinity-city-daily-acf-"+city_str
            spend_str_aer = str(date)+"-affinity-city-daily-aer-"+city_str
            spend_str_all = str(date)+"-affinity-city-daily-all-"+city_str
            spend_str_apg = str(date)+"-affinity-city-daily-apg-"+city_str
            spend_str_grf = str(date)+"-affinity-city-daily-grf-"+city_str
            spend_str_hcs = str(date)+"-affinity-city-daily-hcs-"+city_str
            spend_str_tws = str(date)+"-affinity-city-daily-tws-"+city_str

            subject = econ_spending_stat_collection[spend_str]
            subject_acf = econ_spending_stat[spend_str_acf]
            subject_aer = econ_spending_stat[spend_str_aer]
            subject_all = econ_spending_stat[spend_str_all]
            subject_apg = econ_spending_stat[spend_str_apg]
            subject_grf = econ_spending_stat[spend_str_grf]
            subject_hcs = econ_spending_stat[spend_str_hcs]
            subject_tws = econ_spending_stat[spend_str_tws]
            members = [subject_acf, subject_aer,subject_all, subject_apg, subject_grf, subject_hcs,subject_tws]

            #affinity_g.add((econ_spending[spend_city_daily], RDF.type, econ['StatsCollection']))
            affinity_g.add((econ_spending[spend_city_daily], SOSA.hasMember, subject))

            triplify_obs_collection(city_id, date, members, affinity_g, subject)
            
            triplify_obs_instances('acf', spend_acf, affinity_g, subject_acf)
            triplify_obs_instances('aer', spend_aer, affinity_g, subject_aer)
            triplify_obs_instances('all', spend_all, affinity_g, subject_all)
            triplify_obs_instances('apg', spend_apg, affinity_g, subject_apg)
            triplify_obs_instances('grf', spend_grf, affinity_g, subject_grf)
            triplify_obs_instances('hcs', spend_hcs, affinity_g, subject_hcs)
            triplify_obs_instances('tws', spend_tws, affinity_g, subject_tws)

        elif n_column == 13:
            place_str = 'US'
            spend_acf = item[3]
            spend_aer = item[4]
            spend_all = item[5]
            spend_apg = item[6]
            spend_grf = item[7]
            spend_hcs = item[8]
            spend_tws = item[9]
            spend_all_inchigh = item[10]
            spend_all_inclow = item[11]
            spend_all_incmiddle = item[12]


            spend_str = str(date)+"-affinity-national-daily-"+place_str
            spend_str_acf = str(date)+"-affinity-national-daily-acf-"+place_str
            spend_str_aer = str(date)+"-affinity-national-daily-aer-"+place_str
            spend_str_all = str(date)+"-affinity-national-daily-all-"+place_str
            spend_str_apg = str(date)+"-affinity-national-daily-apg-"+place_str
            spend_str_grf = str(date)+"-affinity-national-daily-grf-"+place_str
            spend_str_hcs = str(date)+"-affinity-national-daily-hcs-"+place_str
            spend_str_tws = str(date)+"-affinity-national-daily-tws-"+place_str
            spend_str_all_inchigh = str(date)+"-affinity-national-daily-all-inchigh-"+place_str
            spend_str_all_inclow = str(date)+"-affinity-national-daily-all-inclow-"+place_str
            spend_str_all_incmiddle = str(date)+"-affinity-national-daily-all-incmiddle-"+place_str


            subject = econ_spending_stat_collection[spend_str]
            subject_acf = econ_spending_stat[spend_str_acf]
            subject_aer = econ_spending_stat[spend_str_aer]
            subject_all = econ_spending_stat[spend_str_all]
            subject_apg = econ_spending_stat[spend_str_apg]
            subject_grf = econ_spending_stat[spend_str_grf]
            subject_hcs = econ_spending_stat[spend_str_hcs]
            subject_tws = econ_spending_stat[spend_str_tws]
            subject_all_inchigh = econ_spending_stat[spend_str_all_inchigh]
            subject_all_inclow = econ_spending_stat[spend_str_all_inclow]
            subject_all_incmiddle = econ_spending_stat[spend_str_all_incmiddle]

            members = [subject_acf, subject_aer,subject_all, subject_apg, subject_grf, subject_hcs,subject_tws, 
                       subject_all_inchigh, subject_all_inclow, subject_all_incmiddle]

            #affinity_g.add((econ_spending[spend_national_daily], RDF.type, econ['StatsCollection']))
            affinity_g.add((econ_spending[spend_national_daily], SOSA.hasMember, subject))

            triplify_obs_collection(place_str, date, members, affinity_g, subject)

            triplify_obs_instances('acf', spend_acf, affinity_g, subject_acf)
            triplify_obs_instances('aer', spend_aer, affinity_g, subject_aer)
            triplify_obs_instances('all', spend_all, affinity_g, subject_all)
            triplify_obs_instances('apg', spend_apg, affinity_g, subject_apg)
            triplify_obs_instances('grf', spend_grf, affinity_g, subject_grf)
            triplify_obs_instances('hcs', spend_hcs, affinity_g, subject_hcs)
            triplify_obs_instances('tws', spend_tws, affinity_g, subject_tws)
            triplify_obs_instances('all_inchigh', spend_all_inchigh, affinity_g, subject_all_inchigh)
            triplify_obs_instances('all_inclow', spend_all_inclow, affinity_g, subject_all_inclow)
            triplify_obs_instances('all_incmiddle', spend_all_incmiddle, affinity_g, subject_all_incmiddle)

        elif n_column == 5:
            county_id = FIPS_normalizer(str(item[3]), 2, 4)
            county_str = 'County-'+str(county_id)
            spend_all = item[4]
            
            spend_str = str(date)+"-affinity-county-daily-"+county_id
            spend_str_all = str(date)+"-affinity-county-daily-all-"+county_id

            subject = econ_spending_stat_collection[spend_str]
            subject_all = econ_spending_stat[spend_str_all]

            members = [subject_all]

            #affinity_g.add((econ_spending[spend_county_daily], RDF.type, econ['StatsCollection']))
            affinity_g.add((econ_spending[spend_county_daily], SOSA.hasMember, subject))
            
            triplify_obs_collection(county_id, date, members, affinity_g, subject)
            triplify_obs_instances('all', spend_all, affinity_g, subject_all)

        elif n_column == 14:
            state_id = FIPS_normalizer(str(item[3]), 2, 4)
            state_str = 'State-'+str(state_id)
            spend_acf = item[4]
            spend_aer = item[5]
            spend_all = item[6]
            spend_apg = item[7]
            spend_grf = item[8]
            spend_hcs = item[9]
            spend_tws = item[10]
            spend_all_inchigh = item[11]
            spend_all_inclow = item[12]
            spend_all_incmiddle = item[13]

            spend_str = str(date)+"-affinity-state-daily-"+state_id
            spend_str_acf = str(date)+"-affinity-state-daily-acf-"+state_id
            spend_str_aer = str(date)+"-affinity-state-daily-aer-"+state_id
            spend_str_all = str(date)+"-affinity-state-daily-all-"+state_id
            spend_str_apg = str(date)+"-affinity-state-daily-apg-"+state_id
            spend_str_grf = str(date)+"-affinity-state-daily-grf-"+state_id
            spend_str_hcs = str(date)+"-affinity-state-daily-hcs-"+state_id
            spend_str_tws = str(date)+"-affinity-state-daily-tws-"+state_id
            spend_str_all_inchigh = str(date)+"-affinity-state-daily-all-inchigh-"+state_id
            spend_str_all_inclow = str(date)+"-affinity-state-daily-all-inclow-"+state_id
            spend_str_all_incmiddle = str(date)+"-affinity-state-daily-all-incmiddle-"+state_id            


            subject = econ_spending_stat_collection[spend_str]
            subject_acf = econ_spending_stat[spend_str_acf]
            subject_aer = econ_spending_stat[spend_str_aer]
            subject_all = econ_spending_stat[spend_str_all]
            subject_apg = econ_spending_stat[spend_str_apg]
            subject_grf = econ_spending_stat[spend_str_grf]
            subject_hcs = econ_spending_stat[spend_str_hcs]
            subject_tws = econ_spending_stat[spend_str_tws]
            subject_all_inchigh = econ_spending_stat[spend_str_all_inchigh]
            subject_all_inclow = econ_spending_stat[spend_str_all_inclow]
            subject_all_incmiddle = econ_spending_stat[spend_str_all_incmiddle]

            members = [subject_acf, subject_aer,subject_all, subject_apg, subject_grf, subject_hcs,subject_tws, 
                       subject_all_inchigh, subject_all_inclow, subject_all_incmiddle]

            
            #affinity_g.add((econ_spending[spend_state_daily], RDF.type, econ['StatsCollection']))
            affinity_g.add((econ_spending[spend_state_daily], SOSA.hasMember, subject))

            triplify_obs_collection(state_id, date, members, affinity_g, subject)

            triplify_obs_instances('acf', spend_acf, affinity_g, subject_acf)
            triplify_obs_instances('aer', spend_aer, affinity_g, subject_aer)
            triplify_obs_instances('all', spend_all, affinity_g, subject_all)
            triplify_obs_instances('apg', spend_apg, affinity_g, subject_apg)
            triplify_obs_instances('grf', spend_grf, affinity_g, subject_grf)
            triplify_obs_instances('hcs', spend_hcs, affinity_g, subject_hcs)
            triplify_obs_instances('tws', spend_acf, affinity_g, subject_tws)
            triplify_obs_instances('all_inchigh', spend_all_inchigh, affinity_g, subject_all_inchigh)
            triplify_obs_instances('all_inclow', spend_all_inclow, affinity_g, subject_all_inclow)
            triplify_obs_instances('all_incmiddle', spend_all_incmiddle, affinity_g, subject_all_incmiddle)

    affinity_g.serialize(destination=output, format='turtle')
    print('Finished triplifying')


def main():
    data_dir = './EconomicTracker/data/'
    file_names = ["Affinity - County - Daily.csv",
     "Affinity - National - Daily.csv", "Affinity - State - Daily.csv"]
    for file_name in file_names:
        data_df = pd.read_csv(data_dir+file_name)
        data_df= data_df.applymap(lambda x: str(numeric_conversion(x)))
        data_list = data_df.values.tolist()
        output = file_name.replace(" - ", "_")
        output = './output_economy/'+output.replace(".csv", ".ttl")
        triplify_affinity(data_list, output)

if __name__ == "__main__":
    main()
