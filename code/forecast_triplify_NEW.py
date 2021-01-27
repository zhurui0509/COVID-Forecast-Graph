#### This is the code to triplify the COVID19-prediction csv ####

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

def loadCSV_new(fileName):
    
    header = ['forecast_date', 'target', 'target_end_date', 'location', 'type', 'quantile', 'value']
    data = pd.read_csv(fileName)
    data = data[header]

    forecast = [list(row) for row in data.values]
    return forecast

def loadCSV_groundTruth(fileName):
    
    header = ['date', 'location', 'location_name',  'value']
    data = pd.read_csv(fileName)
    data = data[header]

    ground_truth = [list(row) for row in data.values]
    return ground_truth

def compare_date(initial_date, target_date):
    ini_year, ini_month, ini_day = initial_date.split("-")
    tar_year, tar_month, tar_day = target_date.split("-")

    initial = datetime.datetime(int(ini_year), int(ini_month), int(ini_day))
    target = datetime.datetime(int(tar_year), int(tar_month), int(tar_day))
    if target > initial:
        return True
    else:
        return False


def loadCSV_groundTruth_filter(fileName, initial_date):
    
    header = ['date', 'location', 'location_name',  'value']
    data = pd.read_csv(fileName)
    data = data[header]

    ground_truth = [list(row) for row in data.values if compare_date(initial_date, row[0])]
    return ground_truth

def loadCSV_model_assumption(fileName):
    header = ['Team', 'Model_matched', 'Method', 'Method_filtered', 'Assumption', 'Assumption_filtered', 'Assumption_CDC']
    data = pd.read_csv(fileName)
    data = data[header]

    model_assumption = [list(row) for row in data.values]
    return model_assumption

# this is the new loading function to load the file with both intervention and hospitalization assumptions
def loadCSV_model_assumption_new(fileName):
    header = ['team', 'model', 'intervention assumptions', 'hospitalization assumptions', 'methods', 'methods_filtered', 'intervention assumptions_filtered', 'hospitalization assumptions_filtered']
    data = pd.read_csv(fileName)
    data = data[header]

    model_assumption = [list(row) for row in data.values]
    return model_assumption


def loadMetaTxt(fileName):
    meta = {}
    f = open(fileName, "r")
    f_s = f.read()
    f_s_p = f_s.replace('\n ', ' ')
    f_s_p_list = f_s_p.split('\n')

    for item in f_s_p_list:
        if ":" in item:
            item_list = item.split(': ')
            if len(item_list) == 2:
                meta[item_list[0]] = item_list[1].strip()
            else:
                key = item_list[0]
                item_list.pop(0)
                meta[key] = ': '.join(item_list)   
    return meta 

def get_requests(url, parameters):
    return requests.get(url, headers = {'User-agent': 'your bot 0.1'}, params=parameters)


def process_contributor(contributor):
    contributor_list = contributor.split(', ')
    return contributor_list

def process_team_name(team_name):
    team_name = team_name.replace(' ', '_')
    import re
    team_name = team_name.translate ({ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`~-=+"})

    return team_name

def triplify_forecast(fileName, forecast_data, output):

    ## Build graph 
    # 1. bind namespace into the graph
    covid_g = Graph()
    covid_g.bind('covid', covid)
    covid_g.bind('covid-research', covid_research)
    covid_g.bind('covid-forecast', covid_forecast)
    covid_g.bind('covid-instant', covid_instant)
    covid_g.bind('covid-place', covid_place)
    covid_g.bind('covid-target', covid_target)
    covid_g.bind('covid-target-type', covid_target_type)
    covid_g.bind('covid-obs-property', covid_obs_property)
    covid_g.bind('covid-model', covid_model)
    covid_g.bind('covid-method', covid_method)
    covid_g.bind('covid-method-type', covid_method_type)
    covid_g.bind('rdf', RDF)
    covid_g.bind('rdfs', RDFS)
    covid_g.bind('xsd', XSD)
    covid_g.bind('owl', OWL)
    covid_g.bind('time', TIME)
    covid_g.bind('geo', GEO)
    covid_g.bind('sosa', SOSA)

    ## 2. forecast triples 
    forecast_name = fileName.split('/')[-1].replace('.csv', '')
    forecast_time = forecast_name[:10]
    research_name = forecast_name[11:]

    research_obj = covid_research[research_name]
    forecast_obj = covid_forecast[forecast_name]

    research_class = covid['Research']
    forecast_class = covid['Forecast']
    target_class = covid['Target']
    target_type_class = covid['TargetType']
    #target_time_class = covid['Instant']
    target_time_class = TIME['Instant']
    target_place_class = covid['Place']


    forecast_time_p = covid['forecastTime']
    target_type_p = covid['hasTargetType']

    #forecasst_time_ins = covid_instant[forecast_time]

    target_types =[]
    target_dates = []
    target_locations = []
    research_forecast_dic = {}

    ## Each research is a collection with forecast as members
    #if research_name in research_forecast_dic:
    #   research_forecast_dic[research_name] = [forecast_obj]


    ## Each forecast is a collection with target as members
    covid_g.add((forecast_obj, RDF.type, forecast_class))
    covid_g.add((forecast_obj, RDFS.label, Literal(forecast_name)))
    covid_g.add((forecast_obj, SOSA.resultTime, Literal(forecast_time)))
    ## for sosa:madeBySensor and sosa:usedProcedure, we include it using the meta. 

    for item in forecast_data:
        target = item[1]  ## target name
        target_end_date = item[2] ## target end date
        target_location = item[3] ## target place
        target_value_type = item[4]
        target_obs_property = "_".join(target.split(" ")[-2:])
        
        target_obj = covid_target[forecast_name +"_"+ target.replace(" ", "-")+"_"+str(target_location)]
        target_endDate_obj= covid_instant[target_end_date]
        target_location_obj = covid_place[str(target_location)]
        target_type_obj = covid_target_type[target.replace(" ", "_")] 
        target_obs_property_obj = covid_obs_property[target_obs_property]
            
        covid_g.add((forecast_obj, SOSA.hasMember, target_obj))
        covid_g.add((target_obj, RDF.type, target_class))
        covid_g.add((target_obj, target_type_p, target_type_obj))
        covid_g.add((target_obj, SOSA.phenomenonTime, target_endDate_obj))
        covid_g.add((target_obj, SOSA.hasFeatureOfInterest, target_location_obj))
        covid_g.add((target_obj, SOSA.observedProperty, target_obs_property_obj))


        
        target_types.append((target_type_obj, target, target_type_class))
        target_dates.append((target_endDate_obj, target_end_date, target_time_class))
        target_locations.append((target_location_obj, target_location, target_place_class))

        
        if target_value_type == 'quantile':
            quantile_p = 'quantile_'+str(item[5])
            quantile_v = item[6]
            forecaset_quantile_p = covid[quantile_p]
            covid_g.add((target_obj, forecaset_quantile_p, Literal(quantile_v)))
        else:
            point_p = 'point'
            point_v = item[6]
            forecaset_point_p = covid[point_p]
            covid_g.add((target_obj, forecaset_point_p, Literal(point_v)))

    # output the triples into ttl file
    covid_g.serialize(destination=output, format='turtle')

    # return the used target_type, target_dates, and target_location 
    # these will be triplied in another function as they are consistent across all predications 
    # it also returns (research_obj, forecast_obj), which will be processed in another function as well
    return target_types, target_dates, target_locations, (research_name, forecast_name)



def triplify_meta(fileName, meta, output):
    research_name = fileName.split('/')[-1].replace('.txt', '')
    research_name = research_name.replace('metadata-', '')

    #model_list = []
    team_list = []
    license_list = []
    model_designation_list = []
    funding_source_list = []
    
    contributor_list = []
    data_input_list = []

    covid_meta_g = Graph()
    covid_meta_g.bind('covid', covid)
    covid_meta_g.bind('covid-research', covid_research)
    covid_meta_g.bind('covid-model', covid_model)
    covid_meta_g.bind('covid-method', covid_method)
    covid_meta_g.bind('covid-owner', covid_owner)
    covid_meta_g.bind('covid-license', covid_license)
    covid_meta_g.bind('covid-funding-resource', covid_fundingResource)
    covid_meta_g.bind('covid-model-designation', covid_modelDesignation)   
    covid_meta_g.bind('rdf', RDF)
    covid_meta_g.bind('rdfs', RDFS)
    covid_meta_g.bind('xsd', XSD)
    covid_meta_g.bind('owl', OWL)
    covid_meta_g.bind('time', TIME)
    covid_meta_g.bind('geo', GEO)


    model_class = covid['Model']
    method_class = covid['Method']
    team_class = covid['Team']
    license_class = covid['License']
    model_designation_class = covid['ModelDesignation']
    funding_resource_class = covid['Organization']
    research_class = covid['Research']



    model_license_p = covid['hasLicense']
    model_name_p = covid['hasName']
    model_short_p = covid['modelBrief']
    model_long_p = covid['modelDesc']
    model_website_p = covid['hasWebsite']
    model_designation_p = covid['modelDesignation']
    model_team_funding_p = covid['fundingSource']
    model_owner_p = covid['owner']

    research_obj = covid_research[research_name]

    covid_meta_g.add((research_obj, RDF.type, research_class))
    covid_meta_g.add((research_obj, RDFS.label, Literal(research_name)))


    if 'model_abbr' in meta:
        model_ns = covid_model[meta['model_abbr']]
        method_ns = covid_method[model_ns.split('-')[-1]]
        #model_list.append(model_ns)
        
        covid_meta_g.add((research_obj, SOSA.madeBySensor, model_ns))               
        covid_meta_g.add((model_ns, RDF.type, model_class))
        covid_meta_g.add((model_ns, RDFS.label, Literal(meta['model_abbr'])))
        
        covid_meta_g.add((research_obj, SOSA.usedProcedure, method_ns)) 
        covid_meta_g.add((method_ns, RDF.type, method_class))
        covid_meta_g.add((method_ns, RDFS.label, Literal(model_ns.split('-')[-1])))

        if 'model_name' in meta:
            covid_meta_g.add((model_ns, model_name_p, Literal(meta['model_name'])))
        if 'methods' in meta:
            covid_meta_g.add((model_ns, model_short_p, Literal(meta['methods'])))
        if 'methods_long' in meta:
            covid_meta_g.add((model_ns, model_long_p, Literal(meta['methods_long'])))
        if 'website_url' in meta:
            website_url_list = meta['website_url'].split(', ')
            for website_url in website_url_list:
                covid_meta_g.add((model_ns, model_website_p, URIRef(website_url)))       
        if 'license' in meta:
            license_ns = covid_license[meta['license']]
            license_list.append((license_ns, meta['license'], license_class))
            covid_meta_g.add((model_ns, model_license_p, license_ns))
        if 'team_model_designation' in meta:
            modelDesignation_ns = covid_modelDesignation[meta['team_model_designation']]
            model_designation_list.append((modelDesignation_ns, meta['team_model_designation'], model_designation_class))
            covid_meta_g.add((model_ns, model_designation_p, modelDesignation_ns))
        if 'data_inputs' in meta:
            data_inputs = process_contributor(meta['data_inputs'])
            #data_input_list.append(data_input for data_input in data_inputs)
            
    if 'team_name' in meta:
        contributor_ns = covid_owner[process_team_name(meta['team_name'])]
        team_list.append((contributor_ns, meta['team_name'], team_class))
        
        covid_meta_g.add((model_ns, model_owner_p, contributor_ns))
        covid_meta_g.add((contributor_ns, RDF.type, team_class))
        covid_meta_g.add((contributor_ns, RDFS.label, Literal(meta['team_name'])))

        if 'team_funding' in meta: 
            fundingResource_ns = covid_fundingResource[process_team_name(meta['team_funding'])]
            funding_source_list.append((fundingResource_ns, meta['team_funding'], funding_resource_class))
            covid_meta_g.add((contributor_ns, model_team_funding_p, fundingResource_ns))
        
        ## TODO
        if 'model_contributors' in meta:
            contributors = process_contributor(meta['model_contributors'])
            #contributor_list.append(contributor for contributor in contributors)
    
    covid_meta_g.serialize(destination=output, format='turtle')

    return team_list, license_list, model_designation_list, funding_source_list
    #return team_list, license_list, model_designation_list, funding_source_list, contributor_list, data_input_list

def rdfType(input_tuple_set, namespace_prefix, namespace, output):
    ### For target_types_list, team_list, licence_list, model_designation_list, funding_source_list
    covid_others_g = Graph()
    covid_others_g.bind('covid', covid)
    covid_others_g.bind(namespace_prefix, namespace)
    covid_others_g.bind('covid-model', covid_model)
    covid_others_g.bind('covid-owner', covid_owner)
    covid_others_g.bind('covid-license', covid_license)
    covid_others_g.bind('covid-target-type', covid_target_type)
    covid_others_g.bind('covid-funding-resource', covid_fundingResource)
    covid_others_g.bind('rdf', RDF)
    covid_others_g.bind('rdfs', RDFS)
    covid_others_g.bind('xsd', XSD)
    covid_others_g.bind('owl', OWL)
    covid_others_g.bind('time', TIME)
    covid_others_g.bind('geo', GEO)
    
    #input_tuple_set = list(set(input_tuple_list))
    #print(input_tuple_set)

    for input_tuple in input_tuple_set:
        item_url = input_tuple[0]
        item_str = input_tuple[1]
        item_class = input_tuple[2]

        covid_others_g.add((item_url, RDF.type, item_class))
        covid_others_g.add((item_url, RDFS.label, Literal(item_str)))


    covid_others_g.serialize(destination=output, format='turtle')

def rdfType_time(input_tuple_set, namespace_prefix, namespace, output):

    covid_others_g = Graph()
    covid_others_g.bind('covid', covid)
    covid_others_g.bind(namespace_prefix, namespace)
    
    #input_tuple_set = list(set(input_tuple_list))
    #print(input_tuple_set)

    for input_tuple in input_tuple_set:
        item_url = input_tuple[0]
        item_str = input_tuple[1]
        item_class = input_tuple[2]
        covid_others_g.add((item_url, RDF.type, item_class))
        covid_others_g.add((item_url, TIME['inXSDDateTime'], Literal(item_str)))

    covid_others_g.serialize(destination=output, format='turtle')

def rdfType_place(input_tuple_set, namespace_prefix, namespace, output):

    covid_others_g = Graph()
    covid_others_g.bind('covid', covid)
    covid_others_g.bind(namespace_prefix, namespace)
    
    #input_tuple_set = list(set(input_tuple_list))

    for input_tuple in input_tuple_set:
        item_url = input_tuple[0]
        item_str = input_tuple[1]
        item_class = input_tuple[2]

        covid_others_g.add((item_url, RDF.type, item_class))
        covid_others_g.add((item_url, covid['placeFIPS'], Literal(item_str)))

    covid_others_g.serialize(destination=output, format='turtle')

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
                    wiki_item= WDT[wiki_item]

        ## below is to fix the bug that county FIPS has five digits (not a good solution)
        #if len(place_FIPS) == 5 and place_FIPS[0] == '0':
        #    place_FIPS = place_FIPS[1:]

        covid_place_g.add((covid_place[place_FIPS], RDF.type, covid['Place']))
        covid_place_g.add((covid_place[place_FIPS], covid['placeFIPS'], Literal(str(place_FIPS))))
        covid_place_g.add((covid_place[place_FIPS], place_hasName_p, Literal(place_name)))
        covid_place_g.add((covid_place[place_FIPS], OWL['sameAs'], wiki_item))

    covid_place_g.serialize(destination=output, format='turtle')


def research2forecast(research_forecast_list, output):
    research_forecast_list = list(research_forecast_list)
    #print(research_forecast_list)

    covid_research_g = Graph()
    covid_research_g.bind('covid', covid)
    covid_research_g.bind('covid-research', covid_research)
    covid_research_g.bind('covid-forecast', covid_forecast)
    covid_research_g.bind('sosa', SOSA)
    
    research_forecast_dic = {}
    # convert the list to dic 
    for item in research_forecast_list:
        #print(item)
        research = item[0]
        forecast = item[1]
        if research in research_forecast_dic:
            research_forecast_dic[research].append(forecast)
        else:
            research_forecast_dic[research] = [forecast]

    for research, forecast_list in research_forecast_dic.items():
        research_obj = covid_research[research]

        for forecast in forecast_list:
            forecast_obj = covid_forecast[forecast]
            covid_research_g.add((research_obj, SOSA.hasMember, forecast_obj))

    covid_research_g.serialize(destination=output, format='turtle')


def triplify_groundtruth(groundtruth_file, groundtruth_type, initial_date, output):
    gt_list = loadCSV_groundTruth(groundtruth_file)  ## to triplify the whole dates
    covid_gt_g = Graph()
    covid_gt_g.bind('covid', covid)
    covid_gt_g.bind('covid-ground-truth', covid_groundTruth)
    covid_gt_g.bind('covid-place', covid_place)
    covid_gt_g.bind('covid-instant', covid_instant)
    covid_gt_g.bind('covid-obs-property', covid_obs_property)
    covid_gt_g.bind('sosa', SOSA)
    covid_gt_g.bind('rdf', RDF)
    covid_gt_g.bind('rdfs', RDFS)
    covid_gt_g.bind('xsd', XSD)
    covid_gt_g.bind('owl', OWL)
    covid_gt_g.bind('time', TIME)
    covid_gt_g.bind('geo', GEO)
    
    for item in gt_list:
        gt_date = item[0]
        gt_location = item[1]
        gt_location_name = item[2] ## will not be used though
        gt_value = item[3]

        gt_sub_url = str(gt_date)+"-GroundTruth-"+groundtruth_type+'_'+str(gt_location)
        gt_sub_str = str(gt_date)+" ground truth of "+groundtruth_type+' at '+str(gt_location)

        covid_gt_g.add((covid_groundTruth[gt_sub_url], RDF.type, covid['GroundTruth']))
        covid_gt_g.add((covid_groundTruth[gt_sub_url], RDFS.label, Literal(gt_sub_str)))
        covid_gt_g.add((covid_groundTruth[gt_sub_url], SOSA.phenomenonTime, covid_instant[gt_date]))
        covid_gt_g.add((covid_groundTruth[gt_sub_url], SOSA.hasFeatureOfInterest, covid_place[str(gt_location)]))
        covid_gt_g.add((covid_groundTruth[gt_sub_url], SOSA.observedProperty, covid_obs_property[groundtruth_type]))
        covid_gt_g.add((covid_groundTruth[gt_sub_url], covid['point'], Literal(gt_value))) ### the predicate can be sosa:hasSimpleResult
    
    covid_gt_g.serialize(destination=output, format='turtle')
    print('Finished triplifying %s' %(groundtruth_file))

## triplify_groundtruth_filer() is different from triplify_groundtruth() with an initial_date as input,
## the goal of this new function is to filter out those dates that have already been triplified.
def triplify_groundtruth_filter(groundtruth_file, groundtruth_type, initial_date, output):
    gt_list = loadCSV_groundTruth_filter(groundtruth_file, initial_date)  ## ony triplify those dates that are after the initial 
    covid_gt_g = Graph()
    covid_gt_g.bind('covid', covid)
    covid_gt_g.bind('covid-ground-truth', covid_groundTruth)
    covid_gt_g.bind('covid-place', covid_place)
    covid_gt_g.bind('covid-instant', covid_instant)
    covid_gt_g.bind('covid-obs-property', covid_obs_property)
    covid_gt_g.bind('sosa', SOSA)
    covid_gt_g.bind('rdf', RDF)
    covid_gt_g.bind('rdfs', RDFS)
    covid_gt_g.bind('xsd', XSD)
    covid_gt_g.bind('owl', OWL)
    covid_gt_g.bind('time', TIME)
    covid_gt_g.bind('geo', GEO)
    
    for item in gt_list:
        gt_date = item[0]
        gt_location = item[1]
        gt_location_name = item[2] ## will not be used though
        gt_value = item[3]

        gt_sub_url = str(gt_date)+"-GroundTruth-"+groundtruth_type+'_'+str(gt_location)
        gt_sub_str = str(gt_date)+" ground truth of "+groundtruth_type+' at '+str(gt_location)

        covid_gt_g.add((covid_groundTruth[gt_sub_url], RDF.type, covid['GroundTruth']))
        covid_gt_g.add((covid_groundTruth[gt_sub_url], RDFS.label, Literal(gt_sub_str)))
        covid_gt_g.add((covid_groundTruth[gt_sub_url], SOSA.phenomenonTime, covid_instant[gt_date]))
        covid_gt_g.add((covid_groundTruth[gt_sub_url], SOSA.hasFeatureOfInterest, covid_place[str(gt_location)]))
        covid_gt_g.add((covid_groundTruth[gt_sub_url], SOSA.observedProperty, covid_obs_property[groundtruth_type]))
        covid_gt_g.add((covid_groundTruth[gt_sub_url], covid['point'], Literal(gt_value))) ### the predicate can be sosa:hasSimpleResult
    
    covid_gt_g.serialize(destination=output, format='turtle')
    print('Finished triplifying %s' %(groundtruth_file))


def triplify_method_assumption(method_assumption_file, method_assumption_hosp_file, output):
    covid_ms_g = Graph()
    covid_ms_g.bind('covid', covid)
    covid_ms_g.bind('covid-model', covid_model)
    covid_ms_g.bind('covid-method', covid_method)
    covid_ms_g.bind('covid-method-type', covid_method_type)
    covid_ms_g.bind('covid-assumption', covid_assumption)
    covid_ms_g.bind('covid-assumption-type', covid_assumption_type)

    #covid_ms_g.bind('covid-assumption-social-distancing', covid_assumption_social_distancing)
    #covid_ms_g.bind('covid-assumption-hospitalization-rate', covid_assumption_hospitalization_rate)


    #model_hasMethod_p = covid['hasMethod']
    model_hasAssumption_p = covid['hasAssumption']
    assumption_hasType_sd_p = covid['assumptionType_sd']
    assumption_hasType_hr_p = covid['assumptionType_hr']
    assumption_hasFull_sd_p = covid['assumptionFull_sd']
    assumption_hasFull_hr_p = covid['assumptionFull_hr']

    method_hasType_p= covid['methodType']
    method_hasFull_p= covid['methodFull']

    #model_hasMethodFull_p = covid['hasMethodFull']
    #model_hasAssumption_social_CDC_p = covid['hasAssumption.SocialDistancing.CDC']
    #model_hasAssumption_social_Full_p = covid['hasAssumption.SocialDistancing.Full']
    #model_hasAssumption_hospitalization_CDC_p = covid['hasAssumption.HospitalizationRate.CDC']
    #model_hasAssumption_hospitalization_Full_p = covid['hasAssumption.HospitalizationRate.Full']

    method_set = set()
    assumption_cdc_set = set()
   
    ### get all existing models ####
    PATH = './output/'
    EXT = "*.ttl"
    ttl_list = [file for path, subdir, files in os.walk(PATH) for file in glob(os.path.join(path, EXT))]

    model_list = []

    for ttl_item in ttl_list:
        if './output/metadata-' in ttl_item:
            model_name = ttl_item.replace('./output/metadata-', '')
            model_name = model_name.replace('.ttl', '')
            model_list.append(model_name)
    #print(model_list)

    ### readin the modal and death assumption information (model_assumption_death.csv)
    method_assumption_list = loadCSV_model_assumption(method_assumption_file)
    for method_assumption  in method_assumption_list:
        team = method_assumption[0]
        method_full = method_assumption[2]
        method_entity = method_assumption[3]
        assumption_full = method_assumption[4]
        assumption_entity_cdc = method_assumption[6]

        #method_set.update([method_entity])
        assumption_cdc_set.update([assumption_entity_cdc])

        for model in model_list:
            if team in model:
                assumption_obj = covid_assumption[model+'_Assumption']
                method_obj = covid_method[model.split('-')[-1]]

                covid_ms_g.add((covid_model[model], model_hasAssumption_p, assumption_obj))
                covid_ms_g.add((assumption_obj, RDF.type, covid['Assumption']))
                covid_ms_g.add((assumption_obj, assumption_hasType_sd_p, covid_assumption_type[assumption_entity_cdc]))
                covid_ms_g.add((assumption_obj, assumption_hasFull_sd_p, Literal(assumption_full)))

                covid_ms_g.add((method_obj, method_hasType_p, covid_method_type[method_entity]))
                covid_ms_g.add((method_obj, method_hasFull_p, Literal(method_full)))

    ### readin the modal and hopital assumption information (model_assumption_death.csv)
    method_assumption_hosp_list = loadCSV_model_assumption(method_assumption_hosp_file)
    for method_assumption_hosp in method_assumption_hosp_list:
        ## we assume the method used is same to the one of predicting death cases 
        team = method_assumption_hosp[0]
        assumption_full = method_assumption_hosp[4]
        assumption_entity_cdc = method_assumption_hosp[6]

        assumption_cdc_set.update([assumption_entity_cdc])

        for model in model_list:
            if team in model:
                assumption_obj = covid_assumption[model+'_Assumption']

                covid_ms_g.add((assumption_obj, assumption_hasType_hr_p, covid_assumption_type[assumption_entity_cdc]))
                covid_ms_g.add((assumption_obj, assumption_hasFull_hr_p, Literal(assumption_full)))

    #for method_item in method_set:
    #    covid_ms_g.add((covid_method[method_item], RDF.type, covid['Method']))
    #    covid_ms_g.add((covid_method[method_item], RDFS.label, Literal(method_item)))

    for assumption_cdc_item in assumption_cdc_set:
        assumption_label = ''
        if assumption_cdc_item == 'sd_change':
            assumption_label = 'levels of social distancing will change in the future.'
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDF.type, covid['AssumptionType']))
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

        elif assumption_cdc_item == 'sd_continue':
            assumption_label = 'existing social distancing measures in each state will continue through the projected four-week time period.'
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDF.type, covid['AssumptionType']))
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

        elif assumption_cdc_item == 'fraction_of_infected':
            assumption_label = 'a certain fraction of infected people will be hospitalized.'
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDF.type, covid['AssumptionType']))
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

        elif assumption_cdc_item == 'number_of_forecasted_death':
            assumption_label = 'estimates hospitalizations based on numbers of forecasted deaths.'
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDF.type, covid['AssumptionType']))
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

        elif assumption_cdc_item == 'reported_hospitalization':
            assumption_label = 'uses COVID-19 hospitalization data reported by some states to forecast future hospitalizations.'
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDF.type, covid['AssumptionType']))
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

        elif assumption_cdc_item == 'complex':
            assumption_label = 'uses the rate of reported infections to estimate the number of new hospitalizations in a given jurisdiction, unless the rates of reported infections and hospitalizations differ. In that case, the rate of reported hospitalizations is used to forecast new hospitalizations.'
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDF.type, covid['AssumptionType']))
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

    covid_ms_g.serialize(destination=output, format='turtle')


def isNaN(num):
    return num != num


def triplify_method_assumption_new(method_assumption_file, output):
    covid_ms_g = Graph()
    covid_ms_g.bind('covid', covid)
    covid_ms_g.bind('covid-model', covid_model)
    covid_ms_g.bind('covid-method', covid_method)
    covid_ms_g.bind('covid-method-type', covid_method_type)
    covid_ms_g.bind('covid-assumption', covid_assumption)
    covid_ms_g.bind('covid-assumption-type', covid_assumption_type)

    #covid_ms_g.bind('covid-assumption-social-distancing', covid_assumption_social_distancing)
    #covid_ms_g.bind('covid-assumption-hospitalization-rate', covid_assumption_hospitalization_rate)


    #model_hasMethod_p = covid['hasMethod']
    model_hasAssumption_p = covid['hasAssumption']
    assumption_hasType_sd_p = covid['assumptionType_sd']
    assumption_hasType_hr_p = covid['assumptionType_hr']
    assumption_hasFull_sd_p = covid['assumptionFull_sd']
    assumption_hasFull_hr_p = covid['assumptionFull_hr']

    method_hasType_p= covid['methodType']
    method_hasFull_p= covid['methodFull']

    #model_hasMethodFull_p = covid['hasMethodFull']
    #model_hasAssumption_social_CDC_p = covid['hasAssumption.SocialDistancing.CDC']
    #model_hasAssumption_social_Full_p = covid['hasAssumption.SocialDistancing.Full']
    #model_hasAssumption_hospitalization_CDC_p = covid['hasAssumption.HospitalizationRate.CDC']
    #model_hasAssumption_hospitalization_Full_p = covid['hasAssumption.HospitalizationRate.Full']

    method_set = set()
    assumption_cdc_set = set()
   
    ### get all existing models ####
    PATH = './output2/'
    EXT = "*.ttl"
    ttl_list = [file for path, subdir, files in os.walk(PATH) for file in glob(os.path.join(path, EXT))]

    model_list = []

    for ttl_item in ttl_list:
        if './output2/metadata-' in ttl_item:
            model_name = ttl_item.replace('./output2/metadata-', '')
            model_name = model_name.replace('.ttl', '')
            model_list.append(model_name)
    #print(model_list)

    ### readin the modal and death assumption information (model_assumption_death.csv)
    method_assumption_list = loadCSV_model_assumption_new(method_assumption_file)
    for method_assumption  in method_assumption_list:
        team = method_assumption[0]
        model_matched = method_assumption[1]
        intervention_assumption_full = method_assumption[2]
        hospitalization_assumption_full = method_assumption[3]
        method_full = method_assumption[4]
        method_entity = method_assumption[5].replace(" ", "_")
        intervention_assumption_entity = method_assumption[6]
        hospitalization_assumption_entity = method_assumption[7]

        #method_set.update([method_entity])
        assumption_cdc_set.update([intervention_assumption_entity])
        assumption_cdc_set.update([hospitalization_assumption_entity])

        for model in model_list:
            if model_matched == model:
                assumption_obj = covid_assumption[model+'_Assumption']
                method_obj = covid_method[model.split('-')[-1]]

                covid_ms_g.add((covid_model[model], model_hasAssumption_p, assumption_obj))
                covid_ms_g.add((assumption_obj, RDF.type, covid['Assumption']))
                if not isNaN(intervention_assumption_full) :
                    if not isNaN(intervention_assumption_entity):
                        covid_ms_g.add((assumption_obj, assumption_hasType_sd_p, covid_assumption_type[intervention_assumption_entity]))
                    covid_ms_g.add((assumption_obj, assumption_hasFull_sd_p, Literal(intervention_assumption_full)))
                if not isNaN(hospitalization_assumption_full):
                    if not isNaN(hospitalization_assumption_entity):
                        covid_ms_g.add((assumption_obj, assumption_hasType_hr_p, covid_assumption_type[hospitalization_assumption_entity]))
                    covid_ms_g.add((assumption_obj, assumption_hasFull_hr_p, Literal(hospitalization_assumption_full)))

                if not isNaN(method_full):
                    if not isNaN(method_entity) :
                        covid_ms_g.add((method_obj, method_hasType_p, covid_method_type[method_entity]))
                    covid_ms_g.add((method_obj, method_hasFull_p, Literal(method_full)))

    #for method_item in method_set:
    #    covid_ms_g.add((covid_method[method_item], RDF.type, covid['Method']))
    #    covid_ms_g.add((covid_method[method_item], RDFS.label, Literal(method_item)))

    for assumption_cdc_item in assumption_cdc_set:
        assumption_label = ''
        if assumption_cdc_item == 'sd_change':
            assumption_label = 'levels of social distancing will change in the future.'
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDF.type, covid['AssumptionType']))
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

        elif assumption_cdc_item == 'sd_continue':
            assumption_label = 'existing social distancing measures in each state will continue through the projected four-week time period.'
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDF.type, covid['AssumptionType']))
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

        elif assumption_cdc_item == 'fraction_of_infected':
            assumption_label = 'a certain fraction of infected people will be hospitalized.'
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDF.type, covid['AssumptionType']))
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

        elif assumption_cdc_item == 'number_of_forecasted_death':
            assumption_label = 'estimates hospitalizations based on numbers of forecasted deaths.'
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDF.type, covid['AssumptionType']))
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

        elif assumption_cdc_item == 'reported_hospitalization':
            assumption_label = 'uses COVID-19 hospitalization data reported by some states to forecast future hospitalizations.'
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDF.type, covid['AssumptionType']))
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

        elif assumption_cdc_item == 'complex':
            assumption_label = 'uses the rate of reported infections to estimate the number of new hospitalizations in a given jurisdiction, unless the rates of reported infections and hospitalizations differ. In that case, the rate of reported hospitalizations is used to forecast new hospitalizations.'
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDF.type, covid['AssumptionType']))
            covid_ms_g.add((covid_assumption_type[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

    covid_ms_g.serialize(destination=output, format='turtle')

### serierlize places and build sameAs connection with wikidata 
def main_places():
    place_file = './covid19-forecast-hub/data-locations/locations.csv'
    output = './output2/places_full_new.ttl'

    triplify_place(place_file, output)

### serierliaze groundtruth data 
def main_groundTruth(initial_date, output):
    truth_incident_deaths_csv = '../covid19-forecast-hub/data-truth/truth-Incident Deaths.csv'
    gt_type_inc_death = 'inc_death'
    output_inc_death = '../'+output+'/groundtruth_inc_death_'+initial_date+'.ttl'

    truth_incident_cases_csv = '../covid19-forecast-hub/data-truth/truth-Incident Cases.csv'
    gt_type_inc_case = 'inc_case'
    output_inc_case = '../'+output+'/groundtruth_inc_case_'+initial_date+'.ttl'


    truth_cumulative_deaths_csv = '../covid19-forecast-hub/data-truth/truth-Cumulative Deaths.csv'
    gt_type_cum_death = 'cum_death'
    output_cum_death = '../'+output+'/groundtruth_cum_death_'+initial_date+'.ttl'

    truth_cumulative_cases_csv = '../covid19-forecast-hub/data-truth/truth-Cumulative Cases.csv'
    gt_type_cum_case = 'cum_case'
    output_cum_case = '../'+output+'/groundtruth_cum_case_'+initial_date+'.ttl'

    ## to triplify all dates
    #triplify_groundtruth(truth_incident_deaths_csv, gt_type_inc_death, output_inc_death)
    #triplify_groundtruth(truth_incident_cases_csv, gt_type_inc_case, output_inc_case)
    #triplify_groundtruth(truth_cumulative_deaths_csv, gt_type_cum_death, output_cum_death)
    #triplify_groundtruth(truth_cumulative_cases_csv, gt_type_cum_case, output_cum_case)
    #truth_zoltar_csv = './covid19-forecast-hub/data-truth/zoltar-truth.csv'

    ## to triplify those dates that are after the initial 
    triplify_groundtruth_filter(truth_incident_deaths_csv, gt_type_inc_death, initial_date, output_inc_death)
    triplify_groundtruth_filter(truth_incident_cases_csv, gt_type_inc_case, initial_date,output_inc_case)
    triplify_groundtruth_filter(truth_cumulative_deaths_csv, gt_type_cum_death, initial_date,output_cum_death)
    triplify_groundtruth_filter(truth_cumulative_cases_csv, gt_type_cum_case, initial_date,output_cum_case)
    #truth_   

### serierliaze model method and assumption
def main_model_assumption_method():
    method_assumption_out = './output2/method_assumption.ttl'
    #triplify_method_assumption('method_assumption_death.csv', 'method_assumption_hospitalization.csv', method_assumption_out)
    triplify_method_assumption_new('cdc_model_assumptions.csv', method_assumption_out)


def main():

    arg_time = sys.argv[1]
    arg_out = sys.argv[2]
    print("Processing triples after %s"%(arg_time))

    #forecast_file_list = ['./prediction_data/2020-07-23-YYG-ParamSearch.csv']
    #meta_file_list  = ['./prediction_data/metadata-YYG-ParamSearch.txt']

    PATH = '../covid19-forecast-hub/data-processed'
    EXT = "*.csv"
    EXT_m = "*.txt"
    forecast_file_list = [file for path, subdir, files in os.walk(PATH) for file in glob(os.path.join(path, EXT))]
    meta_file_list  = [file for path, subdir, files in os.walk(PATH) for file in glob(os.path.join(path, EXT_m))]
    ##print(meta_file_list)

    target_types_list = set()
    target_dates_list = set()
    target_location_list = set()
    team_list = set()
    license_list = set() 
    model_designation_list = set() 
    funding_source_list = set()
    research_forecast_list = []


    #progress_file = 'progress_file.csv'
    progress_file = '../progress_file.csv'

    ### Triplify the forecast data 
    for forecast_file in forecast_file_list:
        progress_file_list = []
        if os.path.isfile(progress_file):
            with open(progress_file, newline='') as fr:
                for line in fr:
                    progress_file_list.append(line.strip().replace('\n', ''))

        if forecast_file.replace("../", './') not in progress_file_list:
            print('Triplify for %s'%(forecast_file))
            output_file = '../'+arg_out+'/'+forecast_file.split('/')[-1].replace('csv', 'ttl')
            forecast_tmp = loadCSV_new(forecast_file)
            target_tmp, target_date_tmp, target_location_tmp, research_forecast_tuple = triplify_forecast(forecast_file, forecast_tmp, output_file)
            target_types_list.update(target_tmp)
            target_dates_list.update(target_date_tmp)
            target_location_list.update(target_location_tmp)
            research_forecast_list.append(research_forecast_tuple)
            #print(research_forecast_list)

            with open(progress_file, 'a') as fa:
                fa.write(forecast_file + '\n')
            pickle.dump((target_types_list, target_dates_list, target_location_list, research_forecast_list), open('target.p', 'wb'))
        else:
            print('%s has already been triplified'%(forecast_file))

    #### Triplify the meta data 
    for meta_file in meta_file_list:
        progress_file_list = []
        if os.path.isfile(progress_file):
            with open(progress_file, newline='') as fr:
                for line in fr:
                    progress_file_list.append(line.strip().replace('\n', ''))

        #if meta_file not in progress_file_list:
        if 1>0: # regenerate the meta triples as some of them are updated
            print('Triplify for %s'%(meta_file))
            #output_file = './output2/'+meta_file.split('/')[-1].replace('txt', 'ttl')
            output_file = '../'+arg_out+'/'+ meta_file.split('/')[-1].replace('txt', 'ttl')
            meta_tmp = loadMetaTxt(meta_file)
            team_tmp, license_tmp, model_designation_tmp, funding_source_tmp = triplify_meta(meta_file, meta_tmp, output_file)
            team_list.update(team_tmp)
            license_list.update(license_tmp)
            model_designation_list.update(model_designation_tmp)
            funding_source_list.update(funding_source_tmp)
            with open(progress_file, 'a') as fa:
                fa.write(meta_file + '\n')
            pickle.dump((team_list, license_list, model_designation_list, funding_source_list), open('meta.p', 'wb'))

        else:
            print('%s has already been triplified'%(meta_file))          

    ###  Triplify the target types (only run it once or add a date to the output file)
    #rdfType(target_types_list, 'covid-target-type', covid_target_type, './output2/target_type.ttl')
    ###  Triplify the team/contributor (only run it once)
    rdfType(team_list, 'covid-owner', covid_owner, '../'+arg_out+'/team.ttl')   
    ###  Triplify the license 
    rdfType(license_list, 'covid-license', covid_license, '../'+arg_out+'/license.ttl')
    ###  Triplify the model designation  
    rdfType(model_designation_list, 'covid-model-designation', covid_modelDesignation, '../'+arg_out+'/modelDesignation.ttl')
    ###  Triplify the funding resource  
    rdfType(funding_source_list, 'covid-funding-resource', covid_fundingResource, '../'+arg_out+'/fundingResource.ttl')
    ### Triplify the time 
    rdfType_time(target_dates_list, 'covid-instant', covid_instant, '../'+arg_out+'/timeInstant_01172021.ttl')
    ### Triplify the research_forecast
    research2forecast(research_forecast_list, '../'+arg_out+'/research2forecast.ttl')

    main_groundTruth(arg_time, arg_out)  ## 2020-09-03


def main_rdftype():
    target_types_list, target_dates_list, target_location_list, research_forecast_list = pickle.load( open( "target.p", "rb" ) )
    team_list, license_list, model_designation_list, funding_source_list = pickle.load( open( "meta.p", "rb" ) )

    rdfType(target_types_list, 'covid-target-type', covid_target_type, './output2/target_type.ttl')
    ###  Triplify the team/contributor 
    #rdfType(team_list, 'covid-owner', covid_owner, './output/team.ttl')   
    ###  Triplify the license 
    rdfType(license_list, 'covid-license', covid_license, './output2/license.ttl')
    ###  Triplify the model designation  
    rdfType(model_designation_list, 'covid-model-designation', covid_modelDesignation, './output2/modelDesignation.ttl')
    ###  Triplify the funding resource  
    rdfType(funding_source_list, 'covid-funding-resource', covid_fundingResource, './output2/fundingResource.ttl')
    ### Triplify the time 
    rdfType_time(target_dates_list, 'covid-instant', covid_instant, './output2/timeInstant.ttl')
    ### Triplify the research_forecast
    research2forecast(research_forecast_list, './output2/research2forecast.ttl')


if __name__ == "__main__":
    main()
    #main_model_assumption_method() # only need to run it once the CDC model description changes
    #main_places() # only need to run it once
    #main_groundTruth("2021-01-18", 'output3_forecast')  ## 2020-09-03
    #main_rdftype() # do not need to run it every time. Run it only if encoutered errors in main()
