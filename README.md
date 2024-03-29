# COVID-Forecast-Graph
This is the repository for the paper "COVID-Forecast-Graph: An Open Knowledge Graph for Consolidating COVID-19 Forecasts and Economic Indicators via Place and Time", which is accepted at [AGILE 2022](https://agile-online.org/conference-2022). 

## About The Project
The longer the COVID-19 pandemic lasts, the more apparent is becomes that understanding its social drivers may be as important as understanding the virus itself. One such social driver of the ongoing spread of COVID-19 is misinformation and distrust in institutions. This is particularly interesting as the scientific process is more transparent than ever before. Numerous scientific teams across the world have published data sets that cover almost any imaginable aspects of this crisis, e.g., daily reported cases and death numbers, forecast of the future death numbers, economic impacts, human mobility, imposed restrictions, biological genes, and so on. However, how to consistently and efficiently integrate and make sense of these separate data 'silos' and present them to scientists, decision makers, journalists, and more importantly the general public remains a key challenge. One approach to integrate COVID-19 related data across domains is knowledge graphs, and several such graphs have been published over the past months. These graphs excel at enabling data crosswalks and exploring auxiliary data to contextualize the patterns of spread. Interestingly, none of these graphs has focused on COVID-19 forecasts and the assumptions underlying these forecasts despite them acting as the underpinning for decision making at NGOs, the industry, and governments from the local to the state level. In this work we report on our work in developing such a graph, motivate the need for exposing forecasts as a knowledge graph, showcase several types of queries that can be run against the graph, and geographically interlink forecast data with indicators of economic impacts.

## Data Sources 
Our graph is generated based on mainly four repositories: 

* COVID-19 Forecast\
  [COVID-19 Forecast](https://covid19forecasthub.org/) collects forecasts of COVID-19 related observations made by various teams using different methods. The folder `./covid19-forecast-hub` is forked from the public repository https://github.com/reichlab/COVID19-forecast-hub. Collected observable properties from this repository include: 
  * incident death 
  * incident case
  * cumulative death
  * incident hospitalization
  
* JHU CSSE Reported Cases \
 JHU CSSE's reported cases and deaths are regarded as the 'ground truth' of the observations in this work. We directly use the processed JHU CSSE case and death numbers provided by the COVID-19 Forecast repository. Other options include [NYT's Covid-19 Data in the United States](https://github.com/nytimes/covid-19-data). Collected observable properties include: 
  * incident death
  * incident case 
  * cumulative death 
 
* Economic Tracker \
We use [Opportunity Insights](https://tracktherecovery.org/) team's [Economic Tracker](https://github.com/OpportunityInsights/EconomicTracker) repository to collect the economic related data. Data in the `./EconomicTracker` folder are forked from this repository. Collected observable properties include:
  * Spending data from [Affinity Solutions](https://www.affinity.solutions/)
  * Job postings from [Burning Glass Technologies](https://www.burning-glass.com/)
  * Employment levels relative to Jan 4-31 from [Paychex](https://www.paychex.com/), [Intuit](https://www.intuit.com/), [Earnin](https://www.earnin.com/) and [Kronos](https://www.kronos.com/)
  * Small business openings data from [Womply](https://www.womply.com/)
  * Small business revenue data from [Womply](https://www.womply.com/)
  * Google mobility data from [Google Mobility](https://www.google.com/covid19/mobility/)

* CDC Model Assumptions and Method Types \
The underlying model assumptions and method types of involved [COVID-19 Forecasts](https://github.com/reichlab/COVID19-forecast-hub) are linked to the [CDC reported data](https://github.com/cdcepi/COVID-19-Forecasts). However, the naming schema are quite different between these two repositories. Therefore, we manually matched the team names used by CDC and project names used by COVID-19 Forecast. Moreoever, we categorized the methods into types such as: Machine Leanring, SEIR, SIR, Regression Analysis, Bayesian Analysis, and so on. The processed data is stored as <em>[./cdc_model_assumptions.csv](https://github.com/zhurui0509/COVID-Forecast-Graph/blob/main/cdc_model_assumptions.csv)</em>.

Folder [output_economy_02182022](https://github.com/zhurui0509/COVID-Forecast-Graph/tree/main/output_economy_02182022) collects graphs of economic-related observations. Folder [output_forecast_02182022](https://github.com/zhurui0509/COVID-Forecast-Graph/tree/main/output_forecast_02182022) contains triplified forecasts untill Feb 18, 2022. All data are represnted in the format of [RDF](https://www.w3.org/RDF/) and stored as [turtle files](https://www.w3.org/TR/turtle/). 

The graph and corresponding [endpoint](http://stko-roy.geog.ucsb.edu:7201 ) are updated every Tuesday. Latest update date: May 12th, 2022. 

## COVID-SO Ontology
To increase the interoperability and reusability of data, we design a COVID-19 forecast related ontology - COVID-SO - on top of the [W3C recommended Semantic Sensor Network ontology](https://www.w3.org/TR/vocab-ssn/) and [its extensions](https://www.w3.org/TR/vocab-ssn-ext/). Concretely, we design a three-tier ontology demonstrated as below. COVID-SO can be found in the folder of <em>[./COVID-SO Ontology](https://github.com/zhurui0509/COVID-Forecast-Graph/tree/main/COVID-SO%20Ontology)</em>. 

* Upper-level ontology
<p align="center">
    <img src="https://github.com/zhurui0509/COVID-Forecast-Graph/blob/main/COVID-SO%20Ontology/images/covid19.png" alt="framework" >
</p>

* Middle-level ontology 
  * COVID-19 forecast 
    <p align="center">
    <img src="https://github.com/zhurui0509/COVID-Forecast-Graph/blob/main/COVID-SO%20Ontology/images/forecast.png" alt="framework" >
    </p>
  * Economic indicators 
    <p align="center">
    <img src="https://github.com/zhurui0509/COVID-Forecast-Graph/blob/main/COVID-SO%20Ontology/images/economic.png" alt="framework" >
    </p>
  * Reported 'ground truth' 
    <p align="center">
    <img src="https://github.com/zhurui0509/COVID-Forecast-Graph/blob/main/COVID-SO%20Ontology/images/groundtruth.png" alt="framework" >
    </p>
* Lower-level ontology 
    <p align="center">
    <img src="https://github.com/zhurui0509/COVID-Forecast-Graph/blob/main/COVID-SO%20Ontology/images/lowerlevel.png" alt="framework" >
    </p> 
* Place-time ontology 
    <p align="center">
    <img src="https://github.com/zhurui0509/COVID-Forecast-Graph/blob/main/COVID-SO%20Ontology/images/placetime.png" alt="framework" >
    </p>
## COVID-Forecast-KG 
COVID-Forecast-KG uses the [Resource Description Framework (RDF)](https://www.w3.org/RDF/) to represent the data. Specificly, the data are formed using [turtle]( https://www.w3.org/TR/turtle/). All forecast-related data are stored in folder(s): <em>[./output_forecast_02182022](https://github.com/zhurui0509/COVID-Forecast-Graph/tree/main/output_forecast_02182022)</em>. And new data are added weekly. Economic indicators are stored in <em>[./output_economy_02182022](https://github.com/zhurui0509/COVID-Forecast-Graph/tree/main/output_economy_02182022)</em>. Censues related data can be found at <em>[./US_census_population_area](https://github.com/zhurui0509/COVID-Forecast-Graph/tree/main/US_census_population_area)</em>. 

The generated graph is also served at https://stko-roy.geog.ucsb.edu/covid (using GraphDB 9.5.1 free version) and below is a sub graph visualization of COVID-Forecast-KG:
    <p align="center">
    <img src="https://github.com/zhurui0509/COVID-Forecast-Graph/blob/main/COVID-SO%20Ontology/images/graphdb_screenshot.png" alt="framework" >
    </p>


## Competency Questions and Exemplary Queries
A set of saved exemplary SPARQL queries to answer the discussed competency questions in the paper can be found in <em>[./example_queries.txt](https://github.com/zhurui0509/COVID-Forecast-Graph/blob/main/example_queries.txt)</em>. Moreover, these exmplary queires are pre-stored in the [endpoint](http://stko-roy.geog.ucsb.edu/covid/sparql) and can be direcyly tested in COVID-Forecast-KG. 

1. Which projects have forecasts about cumulative death for California on 2022-03-12? When have these forecast been made? Which of them used regression analysis? \
First part of the question can be tested [here](http://stko-roy.geog.ucsb.edu/covid/sparql?savedQueryName=Q1_project_forecast_timelist&owner=admin) and the query is listed below:
```
select ?proj_label ?method_label (GROUP_CONCAT(?time; SEPARATOR=",") as ?time_list) where { 
  
  			 ?proj a covid:Research ;
                   rdfs:label ?proj_label ;
                   sosa:hasMember ?f ;
                   sosa:usedProcedure ?method .
  
             ?f a covid:Forecast ;
                sosa:resultTime ?time ;
                sosa:hasMember ?m .
  
             ?m sosa:hasFeatureOfInterest ?p ;
                sosa:observedProperty covid-obs-property:cum_death ;
                sosa:phenomenonTime covid-instant:2022-03-12 .
  
             ?p covid:hasPlaceName 'California' . 
  
  			?method rdfs:label ?method_label ;
                     		    
                                  } 
group by ?proj_label ?method_label
```

The second part can be tested [here](http://stko-roy.geog.ucsb.edu/covid/sparql?savedQueryName=Q1_project_forecast_method&owner=admin) and the query is listed as:
```
select ?project_label where {
  ?project a covid:Research ;
           sosa:hasMember ?forecast ;
           rdfs:label ?project_label ;
           sosa:usedProcedure ?method .
    ?method covid:methodType ?method_type .
    ?method_type rdfs:label 'Regression Analysis' .
    
  ?forecast sosa:hasMember ?target ;
      		sosa:resultTime ?time .
  ?target sosa:observedProperty covid-obs-property:cum_death ;
            sosa:phenomenonTime covid-instant:2021-04-10 ;
            sosa:hasFeatureOfInterest ?place.
  ?place covid:hasPlaceName "California" .
}
```

2. Which projects implement the assumption that local social distancing policies will be kept in place? Which methods do these projects utilize? \
The query can be tested [here](http://stko-roy.geog.ucsb.edu/covid/sparql?savedQueryName=Q2_project_assumption_method&owner=admin) and the specific SPARQl query is: 
```
select ?project_label ?method_label  where {

   ?project a covid:Research ;
             rdfs:label  ?project_label ;
             sosa:madeBySensor ?model;
   			 sosa:usedProcedure ?method .
  
     ?model covid:hasAssumption ?assumption ;
            rdfs:label ?model_label . 
  	 ?assumption covid:assumptionType_sd covid-assumption-type:sd_continue .
                 
     ?method covid:methodFull ?method_label . 
  
}
```

3. Find all predicted cumulative death in California on 2022-02-12, and compare it with the reported ground truth. Further check the prediction interval of forecasts that include the reported 'ground truth'.\
The first part can be tested [here](http://stko-roy.geog.ucsb.edu/covid/sparql?savedQueryName=Q3_prediction_groundtruth&owner=admin) and below is the SPARQL query:
```
select ?forecast ?predict_value ?groundtruth_value where {
   
  ?forecast sosa:hasMember ?target .
  
  ?target a covid:Target ;
            sosa:observedProperty covid-obs-property:cum_death ;
            sosa:phenomenonTime ?time ;
            covid:point ?predict_value ;
            sosa:hasFeatureOfInterest ?place .
    
  ?ground_truth a covid:GroundTruth ;
              sosa:hasFeatureOfInterest ?place ;
              sosa:observedProperty covid-obs-property:cum_death ;
              sosa:phenomenonTime ?time ;
              covid:point ?groundtruth_value .
  
  ?place covid:hasPlaceName "California" .
  ?time time:inXSDDateTime "2022-02-12" .
}
limit 100
    
}
```

The second part can be evaluated [here](http://stko-roy.geog.ucsb.edu/covid/sparql?savedQueryName=Q3_groundtruth_forecast_interval&owner=admin) and its SPARQL query is:
```
select ?project_label ?forecast_time ?ground_value ?upper_bound ?lower_bound ((?upper_bound-?lower_bound) as ?interval) where {
   ?project sosa:hasMember ?forecast ;
            rdfs:label ?project_label . 
    
   ?forecast sosa:hasMember ?target ;
             sosa:resultTime ?forecast_time .
             
   
   ?target a covid:Target ;
            sosa:observedProperty covid-obs-property:cum_death ;
            sosa:phenomenonTime ?time ;
            sosa:hasFeatureOfInterest ?place ;
            covid:quantile_0.01 ?lower_bound ;
            covid:quantile_0.99 ?upper_bound . 
    
  ?ground_truth a covid:GroundTruth ;
              sosa:hasFeatureOfInterest ?place ;
              sosa:observedProperty covid-obs-property:cum_death ;
              sosa:phenomenonTime ?time ;
               covid:point ?ground_value .

  
  ?place covid:hasPlaceName "California" .
  ?time time:inXSDDateTime "2022-02-12" .
    
  filter (?ground_value <?upper_bound && ?ground_value>?lower_bound)
    
}
```

4. Among all the 4-week ahead forecasts of cumulative death in early January 2022 (i.e., before the Omicron peak in the US), which model performed the best for each state across the US?\
There are multiple steps involved in answering this question. First, we extract the earliest forecast date of each research project in January 2022, whose query can be found [here](http://stko-roy.geog.ucsb.edu/covid/sparql?savedQueryName=Q4_1_first_date_of_Jan2022&owner=admin) and the SPARQL query can be found below. The result is stored at <em>[./Question4-Analysis/model_first_august.csv](https://github.com/zhurui0509/COVID-Forecast-Graph/blob/main/Question4-Analysis/model_first_august.csv)</em>. Then we use simple Python scripts to loop through each state finding their best models and subsequently visualize them as a map. All Python scripts can be found in a Jupter Notebook at <em>[./Question4-Analysis/Q5_COVID-Best_model.ipynb](https://github.com/zhurui0509/COVID-Forecast-Graph/blob/main/Question4-Analysis/Q5_COVID-Best_model.ipynb)</em>.

```
select ?research (min(?result_time) as ?first_jan) {
  
  	?research sosa:hasMember ?forecast .
  
  	?forecast a covid:Forecast ;
    	sosa:resultTime ?result_time .

 	FILTER regex(?result_time, "^2022-01") .
}
group by ?research
order by ?first_jan
```
5. Which US state does the [JHUAPL-Bucky] model perform the best (and the worst) compared with other models on [2022-02-05]? How do the results differ from forecasts for [2022-02-12] (another target forecast date)? 
There are multiple steps to answer this question using our COVID-Forecast-Graph. The python code can be found in a Jupyter Notebook at <em>[./Question5-Analysis/OW-State-Comparision.ipynb](https://github.com/zhurui0509/COVID-Forecast-Graph/blob/main/Question5-Analysis/OW-State-Comparision.ipynb)</em>. The specific query to rank model performance on predicting cumulative death on 2021-01-02 for Alabama is listed below and can be tested [here](http://stko-roy.geog.ucsb.edu/covid/sparql?savedQueryName=Q5_1_Karlen-pypm_performance_state&owner=admin). 
```
select ?modelName (min(abs(?predict_value-?groundtruth_value)) as ?min_gap) where {
     
  ?target a covid:Target ;
            sosa:observedProperty covid-obs-property:cum_death ;
            sosa:phenomenonTime ?time ;
            covid:point ?predict_value ;
            sosa:hasFeatureOfInterest ?place ;
            ^sosa:hasMember/^sosa:hasMember/sosa:madeBySensor ?model ;
     .
   
  ?model rdfs:label ?modelName .
            
  ?ground_truth a covid:GroundTruth ;
              sosa:hasFeatureOfInterest ?place ;
              sosa:observedProperty covid-obs-property:cum_death ;
              sosa:phenomenonTime ?time ;
              covid:point ?groundtruth_value .
  
  ?place covid:placeFIPS '01' .
    
  ?time time:inXSDDateTime '2022-02-05' .
}
group by ?modelName
order by ?min_gap
```

6. What is the relation between reported incident cases and citizens spending time at retail and recreation locations (collected by Google) in New York?\
This question can be tested [here](http://stko-roy.geog.ucsb.edu/covid/sparql?savedQueryName=Q6_coviddeath_economic&owner=admin) and below is the specific query. The visualization code can be found in a Jupyter Notebook at <em>[./Question6-Analysis/TimeSeries-Ecomonic-IncidentCases.ipynb](https://github.com/zhurui0509/COVID-Forecast-Graph/blob/main/Question6-Analysis/TimeSeries-Ecomonic-IncidentCases.ipynb)</em>
```
SELECT distinct ?time ?groundtruth_value ?val_econ where {

    ?groundtruth a covid:GroundTruth ;
                sosa:phenomenonTime ?time ;
                sosa:observedProperty covid-obs-property:inc_case ;
                 sosa:hasFeatureOfInterest ?place ;
                 covid:point ?groundtruth_value .
  

    econ-affinity:state-daily sosa:hasMember ?econ_collection .
    ?econ_colelction sosa:phenomenonTime ?time ;
                     sosa:hasFeatureOfInterest ?place ;
                     sosa:hasMember ?econ .
    ?econ sosa:observedProperty econ-obs-property:gps_retail_and_recreation ;
      econ:point ?val_econ .

        ?place covid:hasPlaceName "New York" .
}
order by DESC(?time)
limit 100

```
7. Which model shows the largest deviation in accuracy of forecasting [cumulative death] as a function of [population density]?
The code for this question can be found in a Jupyter Notebook at <em>[./Question7-Analysis/deviationAccuracy_populationDensit.ipynb](https://github.com/zhurui0509/COVID-Forecast-Graph/blob/main/Question7-Analysis/deviationAccuracy_populationDensity.ipynb)</em>. The specific query to find the relation between population density and the accuracy of models (use Alabama on 2021-01-16 as an example) is listed below and can be tested at [here](http://stko-roy.geog.ucsb.edu/covid/sparql?savedQueryName=Q7_1_PopulationDensity_ModelAccuracy&owner=admin). 
```
SELECT ?placeName ?modelName (xsd:float(?census_pop_val)/xsd:float(?census_area_val) AS ?population_density) (min(abs(?predict_value-?groundtruth_value)) as ?min_gap)  where {
	
    ?target a covid:Target ;
            sosa:observedProperty covid-obs-property:cum_death ;
            sosa:phenomenonTime ?time ;
            covid:point ?predict_value ;
            sosa:hasFeatureOfInterest ?place ;
            ^sosa:hasMember/^sosa:hasMember/sosa:madeBySensor ?model ;
     .
    
    ?model rdfs:label ?modelName .

    ?groundtruth a covid:GroundTruth ;
            sosa:phenomenonTime ?time ;
            sosa:observedProperty covid-obs-property:cum_death ;
            sosa:hasFeatureOfInterest ?place ;
            covid:point ?groundtruth_value .
  
    ?census_stat_col a census:StatsCollection ;
            sosa:hasFeatureOfInterest ?place ;
            sosa:hasMember ?census_pop ,
            ?census_area .
    
    ?census_pop covid:point ?census_pop_val;
                sosa:observedProperty census-obs-property:POPESTIMATE2019 . 
    ?census_area covid:point ?census_area_val;
                sosa:observedProperty census-obs-property:TotalArea . 
        
    ?place covid:placeFIPS '01' ;
           covid:hasPlaceName ?placeName.
    
   	?time time:inXSDDateTime '2022-02-12' .

 }
group by ?placeName ?modelName ?census_pop_val ?census_area_val
order by ?min_gap
```



## Code Usage 
Codes in this project can be grouped into two catgeories: 1) codes to generate the RDF graph (code is in [python 3](https://www.python.org/download/releases/3.0/)) and 2) codes for analysis (i.e., answering competency questions) using the graph (codes are provided via Jupyter Notebook - in .ipynb). 

* Libraries needed to run python code (Category 1):
	* [rdflib](https://pypi.org/project/rdflib/)
	* [pandas](https://pandas.pydata.org/docs/getting_started/install.html)
	* [requests](https://pypi.org/project/requests/)
	* [datetime](https://pypi.org/project/DateTime/)
	* [pickle](https://pypi.org/project/pickle5/)

* Libraries needed to run the Jupyter Lab (Category 2):
	* make sure [jupyter lab](https://jupyter.org/install) is installed
	* [pandas](https://pandas.pydata.org/docs/getting_started/install.html)
	* [pymantic](https://pypi.org/project/pymantic/)
	* [plotly](https://plotly.com/python/getting-started/)
	* [matplotlib](https://pypi.org/project/matplotlib/)
	* [pickle](https://pypi.org/project/pickle5/)


Codes to triplify the data collected from various repositories (Catgeory 1) are organized at <em>[./codes](https://github.com/zhurui0509/COVID-Forecast-Graph/tree/main/code)</em>. 
To triplify forecast, reported 'ground truth', and CDC reported model assumption and method types:
```
python forecast_triplify_NEW.py [start_date] [output_folder]
```
To triplify economic data:
```
python economy_general.py
```
To upload generated triples into GraphDB-based COVID-Forecast-Graph (have to install GraphDB and set up the repository first):
```
~/graphdb-free-9.5.1/bin$ ./loadrdf -v -f -i Covid-KG -m parallel [economy_data_folder] [forecast_groundtruth_data_folder]
```
There are other ways to upload the data to the GraphDB endpoint. More details can be found [here](https://graphdb.ontotext.com/documentation/standard/loading-data.html).

## Funding 
The work is funded by the National Science Foundation (Awards No. 2028310, 1936677, and 2033521)

## License
This repository, and associated codes, are distributed under the MIT License. See LICENSE for more information.
