for entry in  "output7_forecast"/*
do
   echo $entry
   curl -X POST -H "Content-Type:application/x-turtle" -T $entry http://stko-roy.geog.ucsb.edu:7201/repositories/COVID19-Forecast-KG/statements || exit 1
   ##echo $entry > "upload_progress.txt"
done

##"/home/rui/NSF-RAPID/output5_forecast"/* (this is loaded through loadRDF)

##"/home/rui/NSF-RAPID/output4_forecast"/* (this is loaded through loadRDF)

## "output3_forecast"/*
## "output6_forecast"/*
## "output_economy"/*
## "output2_forecast"/*


