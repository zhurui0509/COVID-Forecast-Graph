for entry in  ./*.ttl
do
   echo $entry
   curl -X POST -H "Content-Type:application/x-turtle" -T $entry http://stko-roy.geog.ucsb.edu:7201/repositories/Covid-KG/statements || exit 1
   ##echo $entry > "upload_progress.txt"
done
