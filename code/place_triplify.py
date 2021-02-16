############### This is to triplify places ############

import rdflib
import csv 
import pandas as pd
import pickle
import json
import requests

#from wikidata.sparql  import return_sparql_query_results

from rdflib.namespace import CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL, \
                           PROF, PROV, RDF, RDFS, SDO, SH, SKOS, SOSA, SSN, TIME, \
                           VOID, XMLNS, XSD
from rdflib import Namespace
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
#from datetime import datetime
import datetime as datetime
import os
from glob import glob
import sys

SOSA = SSN
covid = Namespace("http://covid.geog.ucsb.edu/lod/ontology/")
covid_research = Namespace("http://covid.geog.ucsb.edu/lod/research/")
covid_forecast = Namespace("http://covid.geog.ucsb.edu/lod/prediction/")
covid_target = Namespace("http://covid.geog.ucsb.edu/lod/target/")
covid_instant = Namespace("http://covid.geog.ucsb.edu/lod/instant/")
covid_place =Namespace("http://covid.geog.ucsb.edu/lod/place/")
covid_target_type = Namespace("http://covid.geog.ucsb.edu/lod/target-type/")

covid_model = Namespace("http://covid.geog.ucsb.edu/lod/model/")
covid_method = Namespace("http://covid.geog.ucsb.edu/lod/method/")
covid_method_type = Namespace("http://covid.geog.ucsb.edu/lod/methodtype/")
covid_assumption_type = Namespace("http://covid.geog.ucsb.edu/lod/assumptiontype/")
covid_obs_property = Namespace("http://covid.geog.ucsb.edu/lod/observedproperty/")
covid_assumption = Namespace("http://covid.geog.ucsb.edu/lod/assumption/")

#covid_assumption_social_distancing = Namespace("http://covid.geog.ucsb.edu/lod/assumption-social-distancing/")
#covid_assumption_hospitalization_rate = Namespace("http://covid.geog.ucsb.edu/lod/assumption-hospitalization-rate/")
#covid_contributor = Namespace("http://covid.geog.ucsb.edu/lod/contributor/")
covid_owner = Namespace("http://covid.geog.ucsb.edu/lod/owner/") 
covid_license = Namespace("http://covid.geog.ucsb.edu/lod/license/")
covid_modelDesignation = Namespace("http://covid.geog.ucsb.edu/lod/modelDesignation/")
covid_fundingResource = Namespace("http://covid.geog.ucsb.edu/lod/fundingResource/")
covid_groundTruth = Namespace("http://covid.geog.ucsb.edu/lod/groundTruth/")
    #covid_organization = Namespace("http://covid.geog.ucsb.edu/lod/organization/") 
GEO = Namespace("http://www.opengis.net/ont/geosparql#")

WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")

wiki = 'https://query.wikidata.org/sparql'


def loadCSV(fileName):
    result = []
    with open(fileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter =',')
        next(csv_reader)
        for row in csv_reader:
            result.append(row)
    return result

def get_requests(url, parameters):
    return requests.get(url, headers = {'User-agent': 'your bot 0.1'}, params=parameters)


def triplify_place(place_file, output):
    covid_place_g = Graph()
    covid_place_g.bind('covid', covid)
    covid_place_g.bind('covid-model', covid_model)
    covid_place_g.bind('covid-place', covid_place)
    covid_place_g.bind('WD', WD)
    covid_place_g.bind('WDT', WDT)
    covid_place_g.bind('OWL', OWL)


    place_list = loadCSV(place_file) # 1st column: abbreviation, 2nd column: location_FIPS, 3rd column: location_name

    place_hasName_p = covid['hasPlaceName']


    for place in place_list:
        place_abbr = place[0]
        place_FIPS = place[1]
        place_name = place[2]

        if place_FIPS == 'US':
            wiki_item = WDT['Q30']
            query = ''

        elif len(place_FIPS) < 5:
            query = '''
                PREFIX wd: <http://www.wikidata.org/entity/>
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                SELECT ?item WHERE
                    {
                        ?item wdt:P5087 \'''' +str(place_FIPS) +'''\' .} '''
        else:
            ## get the wikidata sameAs entity
            query = '''
                    PREFIX wd: <http://www.wikidata.org/entity/>
                    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                    SELECT ?item WHERE
                        {
                            ?item wdt:P882 \'''' +str(place_FIPS) +'''\' .} '''
        if query:

            r = get_requests(wiki, {'format': 'json', 'query': query})
            r = r.json()

            for binding in r['results']['bindings']:
                if binding['item']:
                    wiki_item= binding['item']['value'].split('/')[-1]
                    wiki_item= WD[wiki_item]

        ## below is to fix the bug that county FIPS has five digits (not a good solution)
        #if len(place_FIPS) == 5 and place_FIPS[0] == '0':
        #    place_FIPS = place_FIPS[1:]

        covid_place_g.add((covid_place[place_FIPS], RDF.type, covid['Place']))
        covid_place_g.add((covid_place[place_FIPS], covid['placeFIPS'], Literal(str(place_FIPS))))
        covid_place_g.add((covid_place[place_FIPS], place_hasName_p, Literal(place_name)))
        covid_place_g.add((covid_place[place_FIPS], OWL['sameAs'], wiki_item))

    covid_place_g.serialize(destination=output, format='turtle')



def main():
    place_file = '../covid19-forecast-hub/data-locations/locations.csv'
    output = '../output4_forecast/places_full_new.ttl'

    triplify_place(place_file, output)

if __name__ == "__main__":
    main()