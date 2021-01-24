###### Code to (1). restore the progress_file.csv (2). solve the issue of accidentlt deleting the progress_file.csv
import os
from glob import glob
import csv

folder_PATH = './output/'
EXT = "*.ttl"

ttl_file_list = [file for path, subdir, files in os.walk(folder_PATH) for file in glob(os.path.join(path, EXT))]

progress_list = []
progress_file_name = './covid19-forecast-hub-master/data-processed/'


for ttl_file in ttl_file_list:
	if '2020' in ttl_file:
		forecast_name = ttl_file.replace('./output/', '')
		forecast_name = forecast_name.replace('.ttl', '')
		
		model_name  = forecast_name[11:]

		forecast_csv_file = forecast_name+".csv"

		csv_file_name = ttl_file.replace('.ttl', '.csv')

		progress_list.append(progress_file_name+model_name+'/'+forecast_csv_file)


with open('progress_file2.csv', 'w') as csvfile:
	for item in progress_list:
		csvfile.write(item + '\n')

