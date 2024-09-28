#!/bin/bash
rm /home/ubuntu/Files_Siren/job_time.txt
echo "$(date)" >> /home/ubuntu/Files_Siren/job_time.txt
docker run --rm --user 1000:1000 -it -v $(pwd)/StockDoublons.yaml:/StockDoublons.yaml -v /home/ubuntu/Files_Siren:/home/ubuntu/Files_Siren  docker.redpanda.com/redpandadata/connect run ./StockDoublons.yaml
docker run --rm --user 1000:1000 -it -v $(pwd)/StockEtablissementHistorique.yaml:/StockEtablissementHistorique.yaml   -v /home/ubuntu/Files_Siren:/home/ubuntu/Files_Siren   docker.redpanda.com/redpandadata/connect run ./StockEtablissementHistorique.yaml
docker run --rm --user 1000:1000 -it -v $(pwd)/StockEtablissementLiensSucc.yaml:/StockEtablissementLiensSucc.yaml   -v /home/ubuntu/Files_Siren:/home/ubuntu/Files_Siren   docker.redpanda.com/redpandadata/connect run ./StockEtablissementLiensSucc.yaml
docker run --rm --user 1000:1000 -it -v $(pwd)/StockUniteLegal.yaml:/StockUniteLegal.yaml   -v /home/ubuntu/Files_Siren:/home/ubuntu/Files_Siren   docker.redpanda.com/redpandadata/connect run ./StockUniteLegal.yaml
docker run --rm --user 1000:1000 -it -v $(pwd)/StockUniteLegalHistoriqueZIP.yaml:/StockUniteLegalHistoriqueZIP.yaml   -v /home/ubuntu/Files_Siren:/home/ubuntu/Files_Siren   docker.redpanda.com/redpandadata/connect run ./StockUniteLegalHistoriqueZIP.yaml
echo "$(date)" >> /home/ubuntu/Files_Siren/job_time.txt
