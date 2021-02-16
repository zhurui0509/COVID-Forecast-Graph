################  This is to triplify all dates information #################
from datetime import date, timedelta

from rdflib.namespace import CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL, \
                           PROF, PROV, RDF, RDFS, SDO, SH, SKOS, SOSA, SSN, TIME, \
                           VOID, XMLNS, XSD

from rdflib import Namespace
from rdflib import Graph
from rdflib import URIRef, BNode, Literal

import sys


def main():
    arg_output = sys.argv[1]

    sdate = date(2020, 3, 21)   # start date
    edate = date(2022, 3, 21)   # end date

    delta = edate - sdate       # as timedelta



    covid = Namespace("http://covid.geog.ucsb.edu/lod/ontology/")
    covid_instant = Namespace("http://covid.geog.ucsb.edu/lod/instant/")

    covid_dates_g = Graph()
    covid_dates_g.bind('covid', covid)
    covid_dates_g.bind('covid-instant', covid_instant)
    covid_dates_g.bind('time', TIME)

    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        item_str = day
        item_url = covid_instant[day.strftime('%Y-%m-%d')]

        covid_dates_g.add((item_url, RDF.type, covid['Instant']))
        covid_dates_g.add((item_url, TIME['inXSDDateTime'], Literal(item_str)))    
        #print(day)


    covid_dates_g.serialize(destination=arg_output, format='turtle')


if __name__ == "__main__":
    main()