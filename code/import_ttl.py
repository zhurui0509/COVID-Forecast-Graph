from pymantic import sparql 
import os
from glob import glob





server = sparql.SPARQLServer('http://stko-roy.geog.ucsb.edu:9999/blazegraph/namespace/covid19-prediction/sparql')


progress_file_list = []
progress_file = 'triple_progress_file.csv'
if os.path.isfile(progress_file):
    with open(progress_file, newline='') as fr:
        for line in fr:
        	progress_file_list.append(line.strip().replace('\n', ''))

##### Import the main part of the data #########
PATH = './output'
EXT = "*.ttl"
file_names = [file for path, subdir, files in os.walk(PATH) for file in glob(os.path.join(path, EXT))]

for file_name in file_names:
	if (file_name not in progress_file_list) and ('LICENSE' not in file_name) and ('README' not in file_name):
		file_command = 'load <file://'+os.path.abspath(file_name)+'>'
		print('loading %s' %(file_command))
		server.update(file_command)
		with open(progress_file, 'a') as fa:
			fa.write(file_name + '\n')
	#server.update('load <file:///home/rui/NSF-RAPID/output/2020-03-22-Imperial-ensemble1.ttl>')

####### Import the model2forecast data ##########
# file_command = 'load <file:///home/rui/NSF-RAPID/output/model2forecast.ttl>'
# server.update(file_command)

####### Import the model2team data ##########
# file_command = 'load <file:///home/rui/NSF-RAPID/output/model2team.ttl>'
# server.update(file_command)

####### Import the place_full data ##########
#file_command = 'load <file:///home/rui/NSF-RAPID/output/places_full.ttl>'
#server.update(file_command)


###### Import ground truth and method/assumption data ###########
#files = [ 'groundtruth_inc_death.ttl', 'groundtruth_inc_case.ttl' ,
#           'groundtruth_cum_death.ttl', 'groundtruth_cum_case.ttl', 
#           'method_assumption.ttl']

#for file in files:
#   file_command = 'load <file:///home/rui/NSF-RAPID/output/'+file+'>'
#   server.update(file_command)