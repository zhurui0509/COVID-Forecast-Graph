# COVID-Forecast-Graph
This is the repository for the paper "COVID-Forecast-Graph: An Open Knowledge Graph for Querying and Comparing COVID-19 Forecasts and Linking Them to Economic Indicators"

## About The Project
The longer the COVID-19 pandemic lasts, the more apparent is becomes that understanding its social drivers may be as important as understanding the virus itself. One such social driver of the ongoing spread of COVID-19 is misinformation and distrust in institutions. This is particularly interesting as the scientific process is more transparent than ever before. Numerous scientific teams across the world have published data sets that cover almost any imaginable aspects of this crisis, e.g., daily reported cases and death numbers, forecast of the future death numbers, economic impacts, human mobility, imposed restrictions, biological genes, and so on. However, how to consistently and efficiently integrate and make sense of these separate data 'silos' and present them to scientists, decision makers, journalists, and more importantly the general public remains a key challenge. One approach to integrate COVID-19 related data across domains is knowledge graphs, and several such graphs have been published over the past months. These graphs excel at enabling data crosswalks and exploring auxiliary data to contextualize the patterns of spread. Interestingly, none of these graphs has focused on COVID-19 forecasts and the assumptions underlying these forecasts despite them acting as the underpinning for decision making at NGOs, the industry, and governments from the local to the state level. In this work we report on our work in developing such a graph, motivate the need for exposing forecasts as a knowledge graph, showcase several types of queries that can be run against the graph, and geographically interlink forecast data with indicators of economic impacts.

## Data Sources 
Our graph is generated based on mainly three repository: 

* COVID-19 Forecast\
  The project page can be found at https://covid19forecasthub.org/. The folder <em>[covid19-forecast-hub]</em> is forked from the public repository https://github.com/reichlab/COVID19-forecast-hub. Collected observable properties include: 
  * incident death 
  * incident case
  * cumulative death
  * incident hospitalization
  
* JHU CSSE Reported Cases \
 JHU CSSE's reported cases are regarded as the 'ground truth' of the observations. We directly used the processed data from the COVID-19 Forecast repository. Other options include [NYT's Covid-19 Data in the United States](https://github.com/nytimes/covid-19-data). Collected observable properties include: 
  * incident death
  * incident case 
  * cumulative death 
 
* Economic Tracker \
We use [Opportunity Insights](https://tracktherecovery.org/) team's [Economic Tracker](https://github.com/OpportunityInsights/EconomicTracker) repository to collect the economic related data. Data in the <em>[EconomicTracker]</em> is forked from this repository. Collected observable properties in this work include:
  * Spending data from [Affinity Solutions](https://www.affinity.solutions/)
  * Job postings from [Burning Glass Technologies](https://www.burning-glass.com/)
  * Employment levels relative to Jan 4-31 from [Paychex](https://www.paychex.com/), [Intuit](https://www.intuit.com/), [Earnin](https://www.earnin.com/) and [Kronos](https://www.kronos.com/)
  * Small business openings data from [Womply](https://www.womply.com/)
  * Small business revenue data from [Womply](https://www.womply.com/)

* CDC Model Assumptions and Method Types \
The underlying model assumptions and method types of involved [COVID-19 Forecasts](https://github.com/reichlab/COVID19-forecast-hub) are linked to the [CDC reported data](https://github.com/cdcepi/COVID-19-Forecasts). However, the naming schema are quite different between these two repositories. Therefore, we manually matched the team names used by CDC and project names used by COVID-19 Forecast. Moreoever, we categorized the methods into types such as: Machine Leanring, SEIR, SIR, Regression Analysis, Bayesian Analysis, and so on. The processed data is stored as [cdc_model_assumptions.csv](https://github.com/zhurui0509/COVID-Forecast-Graph/blob/main/cdc_model_assumptions.csv) 

Folder [output_forecast](https://github.com/zhurui0509/COVID-Forecast-Graph/tree/main/output_forecast) contains the triplified forecasts untill 09-30-2020, folder [output2_forecast](https://github.com/zhurui0509/COVID-Forecast-Graph/tree/main/output2_forecast) include forecasts after 09-30-2020. Folder [output_economy] collects graphs of economic-related observations. All data are represnted in the format of [RDF](https://www.w3.org/RDF/) and stored as [turtle files](https://www.w3.org/TR/turtle/). 

The graph and corresponding [endpoint](http://stko-roy.geog.ucsb.edu:7201 ) are updated every Tuesday. 

## COVID-SO Ontology
To increase the interoperability and reusability of the data, we design a COVID-19 related ontology - COVID-SO - on top of the [W3C recommended Semantic Sensor Network ontology](https://www.w3.org/TR/vocab-ssn/) and [its extensions](https://www.w3.org/TR/vocab-ssn-ext/). Concretely, we designed a three-tier ontology demonstrated as below. COVID-SO can be at in the folder of [COVID-SO Ontology](https://github.com/zhurui0509/COVID-Forecast-Graph/tree/main/COVID-SO%20Ontology). 

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
The generated graph is served at http://stko-roy.geog.ucsb.edu:7201 

## Competency Questions and Exemplary Queries
A set of saved exemplary queries to answer the discussed competency questions in the paper can be found at http://stko-roy.geog.ucsb.edu:7201/sparql. 

## Code Usage 

## Funding 
