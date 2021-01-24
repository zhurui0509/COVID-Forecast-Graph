#### This is the code to triplify the COVID19-prediction csv ####

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
from datetime import datetime
import os
from glob import glob

covid = Namespace("http://covid.geog.ucsb.edu/lod/ontology/")
covid_forecast = Namespace("http://covid.geog.ucsb.edu/lod/prediction/")
covid_target = Namespace("http://covid.geog.ucsb.edu/lod/target/")
covid_instant = Namespace("http://covid.geog.ucsb.edu/lod/instant/")
covid_place =Namespace("http://covid.geog.ucsb.edu/lod/place/")
covid_target_type = Namespace("http://covid.geog.ucsb.edu/lod/target-type/")

covid_model = Namespace("http://covid.geog.ucsb.edu/lod/model/")
covid_method = Namespace("http://covid.geog.ucsb.edu/lod/method/")
#covid_assumption = Namespace("http://covid.geog.ucsb.edu/lod/assumption/")
covid_assumption_social_distancing = Namespace("http://covid.geog.ucsb.edu/lod/assumption-social-distancing/")
covid_assumption_hospitalization_rate = Namespace("http://covid.geog.ucsb.edu/lod/assumption-hospitalization-rate/")


covid_contributor = Namespace("http://covid.geog.ucsb.edu/lod/contributor/")
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

def loadCSV_model_assumption(fileName):
    header = ['Team', 'Model_matched', 'Method', 'Method_filtered', 'Assumption', 'Assumption_filtered', 'Assumption_CDC']
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
                meta[item_list[0]] = item_list[1]
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
    return team_name


def triplify_forecast(fileName, forecast_data, output):

    ## Build graph 
    # 1. bind namespace into the graph
    covid_g = Graph()
    covid_g.bind('covid', covid)
    covid_g.bind('covid-forecast', covid_forecast)
    covid_g.bind('covid-instant', covid_instant)
    covid_g.bind('covid-place', covid_place)
    covid_g.bind('covid-target', covid_target)
    covid_g.bind('covid-target-type', covid_target_type)
    covid_g.bind('rdf', RDF)
    covid_g.bind('rdfs', RDFS)
    covid_g.bind('xsd', XSD)
    covid_g.bind('owl', OWL)
    covid_g.bind('time', TIME)
    covid_g.bind('geo', GEO)

    ## 2. forecast triples 
    forecast_name = fileName.split('/')[-1].replace('.csv', '')
    forecast_time = forecast_name[:10]

#forecast = URIRef(covid_forecast[forecast_name])
    forecast_obj = covid_forecast[forecast_name]
    forecast_class = covid['Forecast']
    target_class = covid['Target']
    target_type_class = covid['TargetType']
    target_time_class = covid['Instant']
    target_place_class = covid['Place']

    forecast_time_p = covid['forecastTime']
    forecast_target_p = covid['hasTarget']
    target_endDate_p = covid['endDate']
    target_hasType_p = covid['hasType']
    target_location_p = covid['location']

    #target_hasQuantile_p = covid['hasQuantile']
    forecasst_time_ins = covid_instant[forecast_time]

    target_types =[]
    target_dates = []
    target_locations = []

    covid_g.add((forecast_obj, RDF.type, forecast_class))
    covid_g.add((forecast_obj, RDFS.label, Literal(forecast_name)))
    covid_g.add((forecast_obj, forecast_time_p, forecasst_time_ins))

    target_dates.append((forecasst_time_ins,forecast_time, target_time_class))

    for item in forecast_data:
        target = item[1]  ## target name
        target_end_date = item[2] ## target end date
        target_location = item[3] ## target place
        target_value_type = item[4]
        
        target_obj = covid_target[forecast_name +"_"+ target.replace(" ", "-")+"_"+str(target_location)]
        target_endDate_obj= covid_instant[target_end_date]
        target_location_obj = covid_place[target_location]
        target_type_obj = covid_target[target.replace(" ", "_")] 
            
        covid_g.add((forecast_obj, forecast_target_p, target_obj))
        covid_g.add((target_obj, RDF.type, target_class))
        covid_g.add((target_obj, target_hasType_p, target_type_obj))
        covid_g.add((target_obj, target_endDate_p, target_endDate_obj))
        covid_g.add((target_obj, target_location_p, target_location_obj))
        
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
    return target_types, target_dates, target_locations

def triplify_meta(meta, output):
    #model_list = []
    team_list = []
    license_list = []
    model_designation_list = []
    funding_source_list = []
    contributor_list = []
    data_input_list = []

    covid_meta_g = Graph()
    covid_meta_g.bind('covid', covid)
    covid_meta_g.bind('covid-model', covid_model)
    covid_meta_g.bind('covid-contributor', covid_contributor)
    covid_meta_g.bind('covid-license', covid_license)
    covid_meta_g.bind('rdf', RDF)
    covid_meta_g.bind('rdfs', RDFS)
    covid_meta_g.bind('xsd', XSD)
    covid_meta_g.bind('owl', OWL)
    covid_meta_g.bind('time', TIME)
    covid_meta_g.bind('geo', GEO)


    model_class = covid['Model']
    team_class = covid['Team']
    license_class = covid['License']
    model_designation_class = covid['ModelDesignation']
    funding_resource_class = covid['Organization']


    model_license_p = covid['hasLicense']
    model_name_p = covid['hasName']
    model_method_short_p = covid['methodBrief']
    model_method_long_p = covid['methodDesc']
    model_website_p = covid['hasWebsite']
    model_designation_p = covid['modelDesignation']
    team_funding_p = covid['fundingSource']

    if 'model_abbr' in meta:
        model_ns = covid_model[meta['model_abbr']]
        #model_list.append(model_ns)
        covid_meta_g.add((model_ns, RDF.type, model_class))
        covid_meta_g.add((model_ns, RDFS.label, Literal(meta['model_abbr'])))
        if 'model_name' in meta:
            covid_meta_g.add((model_ns, model_name_p, Literal(meta['model_name'])))
        if 'methods' in meta:
            covid_meta_g.add((model_ns, model_method_short_p, Literal(meta['methods'])))
        if 'methods_long' in meta:
            covid_meta_g.add((model_ns, model_method_long_p, Literal(meta['methods_long'])))
        if 'website_url' in meta:
            covid_meta_g.add((model_ns, model_website_p, URIRef(meta['website_url'])))       
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
        contributor_ns = covid_contributor[process_team_name(meta['team_name'])]
        team_list.append((contributor_ns, meta['team_name'], team_class))
        covid_meta_g.add((contributor_ns, RDF.type, team_class))
        covid_meta_g.add((contributor_ns, RDFS.label, Literal(meta['team_name'])))

        if 'team_funding' in meta: 
            fundingResource_ns = covid_fundingResource[process_team_name(meta['team_funding'])]
            funding_source_list.append((fundingResource_ns, meta['team_funding'], funding_resource_class))
            covid_meta_g.add((contributor_ns, team_funding_p, fundingResource_ns))
        if 'model_contributors' in meta:
            contributors = process_contributor(meta['model_contributors'])
            #contributor_list.append(contributor for contributor in contributors)
    covid_meta_g.serialize(destination=output, format='turtle')

    return team_list, license_list, model_designation_list, funding_source_list
    #return team_list, license_list, model_designation_list, funding_source_list, contributor_list, data_input_list

def rdfType(input_tuple_set, namespace_prefix, namespace, output):

    covid_others_g = Graph()
    covid_others_g.bind('covid', covid)
    covid_others_g.bind(namespace_prefix, namespace)
    covid_others_g.bind('covid-model', covid_model)
    covid_others_g.bind('covid-contributor', covid_contributor)
    covid_others_g.bind('covid-license', covid_license)
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
        covid_others_g.add((item_url, covid['countyFIPS'], Literal(item_str)))

    covid_others_g.serialize(destination=output, format='turtle')


def model2forecast(progress_file, output):

    covid_model2forecast = Graph()
    covid_model2forecast.bind('covid', covid)
    covid_model2forecast.bind('covid-forecast', covid_forecast)
    covid_model2forecast.bind('covid-model', covid_model)
    
    modelHasForecast_p = covid['hasForecast']


    csv_list = []
    txt_list = []
    with open(progress_file, newline='') as fr:
        for line in fr:
            tmp = line.strip().replace('\n', '').split('/')[-1]
            if 'csv' in tmp:
                csv_list.append(tmp.replace('.csv', ''))
            elif 'txt' in tmp:
                txt_list.append(tmp.replace('.txt', ''))
    
    for txt in txt_list:
        if 'metadata' in txt:
            model_name = txt.replace('metadata-', '')
            for forecast_name in csv_list:
                if model_name in forecast_name:
                    covid_model2forecast.add((covid_model[model_name], modelHasForecast_p, covid_forecast[forecast_name]))

    covid_model2forecast.serialize(destination=output, format='turtle')

def model2team(meta_file_list, output):
    covid_model2team = Graph()
    covid_model2team.bind('covid', covid)
    covid_model2team.bind('covid-model', covid_model)
    covid_model2team.bind('covid-contributor', covid_contributor)


    modelOwner_p = covid['owner']

    for meta_file in meta_file_list:
        meta = loadMetaTxt(meta_file)

        if 'model_abbr' in meta:
            model_ns = covid_model[meta['model_abbr']]

            if 'team_name' in meta:
                contributor_ns = covid_contributor[process_team_name(meta['team_name'])]
                covid_model2team.add((model_ns, modelOwner_p, contributor_ns))
            else:
                print("%s has no team name" %(meta['model_abbr']))
        else:
            print('%s has no model_abbr' %(meta_file))
    
    covid_model2team.serialize(destination=output, format='turtle')


def triplify_place(place_file, output):
    covid_place_g = Graph()
    covid_place_g.bind('covid', covid)
    covid_place_g.bind('covid-model', covid_model)
    covid_place_g.bind('covid-place', covid_place)
    covid_place_g.bind('WD', WD)
    covid_place_g.bind('WDT', WDT)

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


        covid_place_g.add((covid_place[place_FIPS], RDF.type, covid['Place']))
        covid_place_g.add((covid_place[place_FIPS], covid['countyFIPS'], Literal(place_FIPS)))
        covid_place_g.add((covid_place[place_FIPS], place_hasName_p, Literal(place_name)))
        covid_place_g.add((covid_place[place_FIPS], OWL['sameAs'], wiki_item))

    covid_place_g.serialize(destination=output, format='turtle')

def triplify_groundtruth(groundtruth_file, groundtruth_type, output):
    gt_list = loadCSV_groundTruth(groundtruth_file)
    covid_gt_g = Graph()
    covid_gt_g.bind('covid', covid)
    covid_gt_g.bind('covid-ground-truth', covid_groundTruth)
    covid_gt_g.bind('covid-place', covid_place)
    covid_gt_g.bind('covid-instant', covid_instant)

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

        covid_gt_g.add((covid_groundTruth[gt_sub_url], RDF.type, covid['GroundTruth']))
        covid_gt_g.add((covid_groundTruth[gt_sub_url], covid['endDate'], covid_instant[gt_date]))
        covid_gt_g.add((covid_groundTruth[gt_sub_url], covid['location'], covid_place[gt_location]))
        covid_gt_g.add((covid_groundTruth[gt_sub_url], covid['point'], Literal(gt_value))) 
    
    covid_gt_g.serialize(destination=output, format='turtle')
    print('Finished triplifying %s' %(groundtruth_file))

def triplify_method_assumption(method_assumption_file, method_assumption_hosp_file, output):
    covid_ms_g = Graph()
    covid_ms_g.bind('covid', covid)
    covid_ms_g.bind('covid-model', covid_model)
    covid_ms_g.bind('covid-method', covid_method)
    #covid_ms_g.bind('covid-assumption', covid_assumption)
    covid_ms_g.bind('covid-assumption-social-distancing', covid_assumption_social_distancing)
    covid_ms_g.bind('covid-assumption-hospitalization-rate', covid_assumption_hospitalization_rate)



    model_hasMethod_p = covid['hasMethod']
    model_hasMethodFull_p = covid['hasMethodFull']
    model_hasAssumption_social_CDC_p = covid['hasAssumption.SocialDistancing.CDC']
    model_hasAssumption_social_Full_p = covid['hasAssumption.SocialDistancing.Full']
    model_hasAssumption_hospitalization_CDC_p = covid['hasAssumption.HospitalizationRate.CDC']
    model_hasAssumption_hospitalization_Full_p = covid['hasAssumption.HospitalizationRate.Full']


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
    print(model_list)

    ### readin the modal and assumption information (model_assumption_death.csv)
    method_assumption_list = loadCSV_model_assumption(method_assumption_file)
    for method_assumption  in method_assumption_list:
        team = method_assumption[0]
        method_full = method_assumption[2]
        method_entity = method_assumption[3]
        assumption_full = method_assumption[4]
        assumption_entity_cdc = method_assumption[6]

        method_set.update([method_entity])
        assumption_cdc_set.update([assumption_entity_cdc])

        for model in model_list:
            if team in model:
                covid_ms_g.add((covid_model[model], model_hasMethod_p, covid_method[method_entity]))
                covid_ms_g.add((covid_model[model], model_hasMethodFull_p, Literal(method_full)))
                covid_ms_g.add((covid_model[model], model_hasAssumption_social_CDC_p, covid_assumption_social_distancing[assumption_entity_cdc]))
                covid_ms_g.add((covid_model[model], model_hasAssumption_social_Full_p, Literal(assumption_full)))

    method_assumption_hosp_list = loadCSV_model_assumption(method_assumption_hosp_file)
    for method_assumption_hosp in method_assumption_hosp_list:
        ## we assume the method used is same to the one of predicting death cases 
        team = method_assumption_hosp[0]
        assumption_full = method_assumption_hosp[4]
        assumption_entity_cdc = method_assumption_hosp[6]

        assumption_cdc_set.update([assumption_entity_cdc])

        for model in model_list:
            if team in model:
                covid_ms_g.add((covid_model[model], model_hasAssumption_hospitalization_CDC_p, covid_assumption_hospitalization_rate[assumption_entity_cdc]))
                covid_ms_g.add((covid_model[model], model_hasAssumption_hospitalization_Full_p, Literal(assumption_full)))


    for method_item in method_set:
        covid_ms_g.add((covid_method[method_item], RDF.type, covid['Method']))
        covid_ms_g.add((covid_method[method_item], RDFS.label, Literal(method_item)))

    for assumption_cdc_item in assumption_cdc_set:
        assumption_label = ''
        if assumption_cdc_item == 'sd_change':
            assumption_label = 'levels of social distancing will change in the future.'
            covid_ms_g.add((covid_assumption_social_distancing[assumption_cdc_item], RDF.type, covid['Assumption']))
            covid_ms_g.add((covid_assumption_social_distancing[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

        elif assumption_cdc_item == 'sd_continue':
            assumption_label = 'existing social distancing measures in each state will continue through the projected four-week time period.'
            covid_ms_g.add((covid_assumption_social_distancing[assumption_cdc_item], RDF.type, covid['Assumption']))
            covid_ms_g.add((covid_assumption_social_distancing[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

        elif assumption_cdc_item == 'fraction_of_infected':
            assumption_label = 'a certain fraction of infected people will be hospitalized.'
            covid_ms_g.add((covid_assumption_hospitalization_rate[assumption_cdc_item], RDF.type, covid['Assumption']))
            covid_ms_g.add((covid_assumption_hospitalization_rate[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

        elif assumption_cdc_item == 'number_of_forecasted_death':
            assumption_label = 'estimates hospitalizations based on numbers of forecasted deaths.'
            covid_ms_g.add((covid_assumption_hospitalization_rate[assumption_cdc_item], RDF.type, covid['Assumption']))
            covid_ms_g.add((covid_assumption_hospitalization_rate[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

        elif assumption_cdc_item == 'reported_hospitalization':
            assumption_label = 'uses COVID-19 hospitalization data reported by some states to forecast future hospitalizations.'
            covid_ms_g.add((covid_assumption_hospitalization_rate[assumption_cdc_item], RDF.type, covid['Assumption']))
            covid_ms_g.add((covid_assumption_hospitalization_rate[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

        elif assumption_cdc_item == 'complex':
            assumption_label = 'uses the rate of reported infections to estimate the number of new hospitalizations in a given jurisdiction, unless the rates of reported infections and hospitalizations differ. In that case, the rate of reported hospitalizations is used to forecast new hospitalizations.'
            covid_ms_g.add((covid_assumption_hospitalization_rate[assumption_cdc_item], RDF.type, covid['Assumption']))
            covid_ms_g.add((covid_assumption_hospitalization_rate[assumption_cdc_item], RDFS.label, Literal(assumption_label)))

    covid_ms_g.serialize(destination=output, format='turtle')





### serierlize model2forecast
def main1():
    progress_file = 'progress_file.csv'
    output_file = './output/model2forecast.ttl'
    model2forecast(progress_file, output_file)


### serierlize model2team
def main2():
    output_file = './output/model2team.ttl'
    PATH = './covid19-forecast-hub/data-processed'
    EXT_m = "*.txt"
    meta_file_list  = [file for path, subdir, files in os.walk(PATH) for file in glob(os.path.join(path, EXT_m))]
    model2team(meta_file_list, output_file)

### serierlize places and build sameAs connection with wikidata 
def main3():
    place_file = './covid19-forecast-hub/data-locations/locations.csv'
    output = './output/places_full.ttl'

    triplify_place(place_file, output)

### serierliaze groundtruth data 
def main4():
    truth_incident_deaths_csv = './covid19-forecast-hub/data-truth/truth-Incident Deaths.csv'
    gt_type_inc_death = 'inc-death'
    output_inc_death = './output/groundtruth_inc_death.ttl'

    truth_incident_cases_csv = './covid19-forecast-hub/data-truth/truth-Incident Cases.csv'
    gt_type_inc_case = 'inc-case'
    output_inc_case = './output/groundtruth_inc_case.ttl'


    truth_cumulative_deaths_csv = './covid19-forecast-hub/data-truth/truth-Cumulative Deaths.csv'
    gt_type_cum_death = 'cum-death'
    output_cum_death = './output/groundtruth_cum_death.ttl'

    truth_cumulative_cases_csv = './covid19-forecast-hub/data-truth/truth-Cumulative Cases.csv'
    gt_type_cum_case = 'cum-case'
    output_cum_case = './output/groundtruth_cum_case.ttl'


    triplify_groundtruth(truth_incident_deaths_csv, gt_type_inc_death, output_inc_death)
    triplify_groundtruth(truth_incident_cases_csv, gt_type_inc_case, output_inc_case)
    triplify_groundtruth(truth_cumulative_deaths_csv, gt_type_cum_death, output_cum_death)
    triplify_groundtruth(truth_cumulative_cases_csv, gt_type_cum_case, output_cum_case)
    #truth_zoltar_csv = './covid19-forecast-hub/data-truth/zoltar-truth.csv'

### serierliaze model method and assumption
def main5():
    method_assumption_out = './output/method_assumption.ttl'
    triplify_method_assumption('method_assumption_death.csv', 'method_assumption_hospitalization.csv', method_assumption_out)

def main():

    #forecast_file_list = ['./prediction_data/2020-07-23-YYG-ParamSearch.csv']
    #meta_file_list  = ['./prediction_data/metadata-YYG-ParamSearch.txt']

    PATH = './covid19-forecast-hub/data-processed'
    EXT = "*.csv"
    EXT_m = "*.txt"
    forecast_file_list = [file for path, subdir, files in os.walk(PATH) for file in glob(os.path.join(path, EXT))]
    meta_file_list  = [file for path, subdir, files in os.walk(PATH) for file in glob(os.path.join(path, EXT_m))]
    #print(meta_file_list)

    target_types_list = set()
    target_dates_list = set()
    target_location_list = set()
    team_list = set()
    license_list = set() 
    model_designation_list = set() 
    funding_source_list = set()


    #progress_file = 'progress_file.csv'
    progress_file = 'progress_file2.csv'

    ### Triplify the forecast data 
    for forecast_file in forecast_file_list:
        progress_file_list = []
        if os.path.isfile(progress_file):
            with open(progress_file, newline='') as fr:
                for line in fr:
                    progress_file_list.append(line.strip().replace('\n', ''))

        if forecast_file not in progress_file_list:
            print('Triplify for %s'%(forecast_file))
            output_file = './output/'+forecast_file.split('/')[-1].replace('csv', 'ttl')
            forecast_tmp = loadCSV_new(forecast_file)
            target_tmp, target_date_tmp, target_location_tmp = triplify_forecast(forecast_file, forecast_tmp, output_file)
            target_types_list.update(target_tmp)
            target_dates_list.update(target_date_tmp)
            target_location_list.update(target_location_tmp)
            with open(progress_file, 'a') as fa:
                fa.write(forecast_file + '\n')
            pickle.dump((target_types_list, target_dates_list, target_location_list), open('target.p', 'wb'))
        else:
            print('%s has already been triplified'%(forecast_file))

    #### Triplify the meta data 
    for meta_file in meta_file_list:
        progress_file_list = []
        if os.path.isfile(progress_file):
            with open(progress_file, newline='') as fr:
                for line in fr:
                    progress_file_list.append(line.strip().replace('\n', ''))

        if meta_file not in progress_file_list:
            print('Triplify for %s'%(meta_file))
            output_file = './output/'+meta_file.split('/')[-1].replace('txt', 'ttl')
            meta_tmp = loadMetaTxt(meta_file)
            team_tmp, license_tmp, model_designation_tmp, funding_source_tmp = triplify_meta(meta_tmp, output_file)
            team_list.update(team_tmp)
            license_list.update(license_tmp)
            model_designation_list.update(model_designation_tmp)
            funding_source_list.update(funding_source_tmp)
            with open(progress_file, 'a') as fa:
                fa.write(meta_file + '\n')
            pickle.dump((team_list, license_list, model_designation_list, funding_source_list), open('meta.p', 'wb'))

        else:
            print('%s has already been triplified'%(meta_file))          

    ###  Triplify the target types 
    rdfType(target_types_list, 'covid-target-type', covid_target_type, './output/target_type.ttl')
    ###  Triplify the team/contributor 
    rdfType(team_list, 'covid-contributor', covid_contributor, './output/team.ttl')   
    ###  Triplify the license 
    rdfType(license_list, 'covid-license', covid_license, './output/license.ttl')
    ###  Triplify the model designation  
    rdfType(model_designation_list, 'covid-model-designation', covid_modelDesignation, './output/modelDesignation.ttl')
    ###  Triplify the funding resource  
    rdfType(funding_source_list, 'covid-funding-resource', covid_fundingResource, './output/fundingResource.ttl')
    ### Triplify the time 
    rdfType_time(target_dates_list, 'covid-instant', covid_instant, './output/timeInstant.ttl')
    ### Triplify the place 
    # triplify_place() could replace it and it only need to run once. 
    #rdfType_place(target_location_list, 'covid-place', covid_place, './output/places.ttl')


if __name__ == "__main__":
    main5()