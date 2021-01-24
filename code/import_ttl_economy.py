from pymantic import sparql 
import os
from glob import glob





server = sparql.SPARQLServer('http://stko-roy.geog.ucsb.edu:9999/blazegraph/namespace/covid19-prediction/sparql')


progress_file_list = []
progress_file = 'triple_progress_file_economy.csv'
if os.path.isfile(progress_file):
    with open(progress_file, newline='') as fr:
        for line in fr:
        	progress_file_list.append(line.strip().replace('\n', ''))

##### Import the main part of the data #########
PATH = './output_economy'
EXT = "*.ttl"
file_names = [file for path, subdir, files in os.walk(PATH) for file in glob(os.path.join(path, EXT))]

for file_name in file_names:
	if (file_name not in progress_file_list) and ('LICENSE' not in file_name) and ('README' not in file_name):
		file_command = 'load <file://'+os.path.abspath(file_name)+'>'
		print('loading %s' %(file_command))
		server.update(file_command)
		with open(progress_file, 'a') as fa:
			fa.write(file_name + '\n')