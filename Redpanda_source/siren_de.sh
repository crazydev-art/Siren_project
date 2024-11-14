#!/bin/bash
rm /home/ubuntu/Files_Siren/job_time.txt
echo "$(date) 01 Stock Etabl. ZIP" >> /home/ubuntu/Files_Siren/job_time.txt
docker run --rm --user 1000:1000 -it -v /home/ubuntu/Redpanda/01StockEtablissementZIP.yaml:/01StockEtablissementZIP.yaml -v /home/ubuntu/Files_Siren:/home/ubuntu/Files_Siren  docker.redpanda.com/redpandadata/connect run ./01StockEtablissementZIP.yaml
echo "$(date) 02 Stock Etabl. ZIP to CSV" >> /home/ubuntu/Files_Siren/job_time.txt
docker run --rm --user 1000:1000 -it -v /home/ubuntu/Redpanda/02StockEtablissementZIP_csv.yaml:/02StockEtablissementZIP_csv.yaml   -v /home/ubuntu/Files_Siren:/home/ubuntu/Files_Siren   docker.redpanda.com/redpandadata/connect run ./02StockEtablissementZIP_csv.yaml
echo "$(date) 03 Stock Etabl. CSV to PostgreSQL" >> /home/ubuntu/Files_Siren/job_time.txt
docker run --rm --user 1000:1000 -it -v /home/ubuntu/Redpanda/03StockEtabl_SQL.yaml:/03StockEtabl_SQL.yaml   -v /home/ubuntu/Files_Siren:/home/ubuntu/Files_Siren   docker.redpanda.com/redpandadata/connect run ./03StockEtabl_SQL.yaml
echo "$(date) 04 Stock Unite Legale ZIP" >> /home/ubuntu/Files_Siren/job_time.txt
docker run --rm --user 1000:1000 -it -v /home/ubuntu/Redpanda/04StockUniteLegaleZIP.yaml:/04StockUniteLegaleZIP.yaml   -v /home/ubuntu/Files_Siren:/home/ubuntu/Files_Siren   docker.redpanda.com/redpandadata/connect run ./04StockUniteLegaleZIP.yaml
echo "$(date) 05 Stock Unite Legale ZIP to CSV" >> /home/ubuntu/Files_Siren/job_time.txt
docker run --rm --user 1000:1000 -it -v /home/ubuntu/Redpanda/05StockUniteLegaleZIP_csv.yaml:/05StockUniteLegaleZIP_csv.yaml   -v /home/ubuntu/Files_Siren:/home/ubuntu/Files_Siren   docker.redpanda.com/redpandadata/connect run ./05StockUniteLegaleZIP_csv.yaml
echo "$(date) 06 Stock Unite Legale to PostgreSQL" >> /home/ubuntu/Files_Siren/job_time.txt
docker run --rm --user 1000:1000 -it -v /home/ubuntu/Redpanda/06StockUniteLegale_SQL.yaml:/06StockUniteLegale_SQL.yaml   -v /home/ubuntu/Files_Siren:/home/ubuntu/Files_Siren   docker.redpanda.com/redpandadata/connect run ./06StockUniteLegale_SQL.yaml
echo "$(date) 07 categorie juridique PostgreSQL" >> /home/ubuntu/Files_Siren/job_time.txt
docker run --rm --user 1000:1000 -it -v /home/ubuntu/Redpanda/07CatJuridique_SQL.yaml:/07CatJuridique_SQL.yaml   -v /home/ubuntu/Files_Siren:/home/ubuntu/Files_Siren   docker.redpanda.com/redpandadata/connect run ./07CatJuridique_SQL.yaml
echo "$(date) 08 code NAF V2 PostgreSQL" >> /home/ubuntu/Files_Siren/job_time.txt
docker run --rm --user 1000:1000 -it -v /home/ubuntu/Redpanda/08CodeNaf_SQL.yaml:/08CodeNaf_SQL.yaml   -v /home/ubuntu/Files_Siren:/home/ubuntu/Files_Siren   docker.redpanda.com/redpandadata/connect run ./08CodeNaf_SQL.yaml
echo "$(date) End of Bash" >> /home/ubuntu/Files_Siren/job_time.txt

