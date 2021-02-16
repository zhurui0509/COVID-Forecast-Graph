import pandas as pd
from pymantic import sparql
import csv
import plotly.express as px
import csv


#### This function implements a template to generate the query to list the forecast models's performances on each state

def query_generator(county_fips, time):
    query = ("""
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX covid-obs-property: <http://covid.geog.ucsb.edu/lod/observedproperty/>
PREFIX covid-instant: <http://covid.geog.ucsb.edu/lod/instant/>
PREFIX covid-place: <http://covid.geog.ucsb.edu/lod/place/>
PREFIX covid: <http://covid.geog.ucsb.edu/lod/ontology/>
PREFIX covid-method: <http://covid.geog.ucsb.edu/lod/method/>
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>


select ?modelName (min(abs(?predict_value-?groundtruth_value)) as ?min_gap) where {
     
  ?target a covid:Target ;
            sosa:observedProperty covid-obs-property:inc_case ;
            sosa:phenomenonTime ?time ;
            covid:point ?predict_value ;
            sosa:hasFeatureOfInterest ?place ;
            ^sosa:hasMember/^sosa:hasMember/sosa:madeBySensor ?model ;
     .
   
  ?model rdfs:label ?modelName .
            
  ?ground_truth a covid:GroundTruth ;
              sosa:hasFeatureOfInterest ?place ;
              sosa:observedProperty covid-obs-property:inc_case ;
              sosa:phenomenonTime ?time ;
              covid:point ?groundtruth_value .
  
  ?place covid:placeFIPS '%s' .
    
  ?time time:inXSDDateTime '%s' .
}
group by ?modelName
order by ?min_gap
""")% (county_fips, time)
    return query


### This function organizes the queries results from query_generator(model_url, date_str)

def extract_results(result):
    result_list = []
    
    for item in result['results']['bindings']:
        result_list.append([item['modelName']['value'], item['min_gap']['value']])
    
    return result_list

def main():
  fips = pd.read_csv("./US_FIPS_Codes.csv", header=None)
  fips.columns = ['State', 'County', "State_FIPS", "County_FIPS"]
  fips['State_FIPS'] = fips['State_FIPS'].apply(lambda x: str(x).zfill(2))
  fips['County_FIPS'] = fips['County_FIPS'].apply(lambda x: str(x).zfill(3))
  fips['FIPS'] = fips['State_FIPS'] + fips['County_FIPS']

  OW_county = []
  fips_list = fips['FIPS'].tolist()

  file_path = "OW_result.csv"

  for item in fips_list:
      if int(item)>=39039:
        print("processing county:%s"%item)
        query_item = query_generator(item, "2021-01-09")
        server = sparql.SPARQLServer('http://128.111.106.227:7201/repositories/Covid-KG')
        result = server.query(query_item)
        result_list = extract_results(result)
        result_pd = pd.DataFrame(result_list, columns =['Model', 'Error'])  
        if len(result_pd.index[result_pd['Model'] == 'OliverWyman-Navigator'].tolist())>0:
          OW_index = result_pd.index[result_pd['Model'] == 'OliverWyman-Navigator'].tolist()[0]
          OW_ratio = (OW_index+1)/len(result_pd)  # index start from 0, so +1
          with open(file_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow([item, OW_index+1, len(result_pd), OW_ratio])
        else:
          with open(file_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow([item, '', '', ''])

      #OW_county.append([item, OW_index+1, len(result_pd), OW_ratio])




if __name__ == "__main__":
    main()



