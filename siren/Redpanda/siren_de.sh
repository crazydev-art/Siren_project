#!/bin/bash
env > $FILESIREN/environ.txt
echo "$(date) 01 Stock Etabl. ZIP" > $FILESIREN/job_time.txt
docker run --rm --user 1000:1000 -it --env-file ./.env -v $REDPANDA/01StockEtablissementZIP.yaml:/01StockEtablissementZIP.yaml -v $FILESIREN:$FILESIREN  docker.redpanda.com/redpandadata/connect run ./01StockEtablissementZIP.yaml
echo "$(date) 02 Stock Etabl. ZIP to CSV" >> $FILESIREN/job_time.txt
docker run --rm --user 1000:1000 -it --env-file ./.env -v $REDPANDA/02StockEtablissementZIP_csv.yaml:/02StockEtablissementZIP_csv.yaml   -v $FILESIREN:$FILESIREN   docker.redpanda.com/redpandadata/connect run ./02StockEtablissementZIP_csv.yaml
echo "$(date) 03 Stock Etabl. CSV to PostgreSQL" >> $FILESIREN/job_time.txt
docker run --rm --user 1000:1000 -it --env-file ./.env -v $REDPANDA/03StockEtabl_SQL.yaml:/03StockEtabl_SQL.yaml   -v $FILESIREN:$FILESIREN   docker.redpanda.com/redpandadata/connect run ./03StockEtabl_SQL.yaml
echo "$(date) 04 Stock Unite Legale ZIP" >> $FILESIREN/job_time.txt
docker run --rm --user 1000:1000 -it --env-file ./.env -v $REDPANDA/04StockUniteLegaleZIP.yaml:/04StockUniteLegaleZIP.yaml   -v $FILESIREN:$FILESIREN   docker.redpanda.com/redpandadata/connect run ./04StockUniteLegaleZIP.yaml
echo "$(date) 05 Stock Unite Legale ZIP to CSV" >> $FILESIREN/job_time.txt
docker run --rm --user 1000:1000 -it --env-file ./.env -v $REDPANDA/05StockUniteLegaleZIP_csv.yaml:/05StockUniteLegaleZIP_csv.yaml   -v $FILESIREN:$FILESIREN   docker.redpanda.com/redpandadata/connect run ./05StockUniteLegaleZIP_csv.yaml
echo "$(date) 06 Stock Unite Legale to PostgreSQL" >> $FILESIREN/job_time.txt
docker run --rm --user 1000:1000 -it --env-file ./.env -v $REDPANDA/06StockUniteLegale_SQL.yaml:/06StockUniteLegale_SQL.yaml   -v $FILESIREN:$FILESIREN   docker.redpanda.com/redpandadata/connect run ./06StockUniteLegale_SQL.yaml
echo "$(date) 07 categorie juridique PostgreSQL" >> $FILESIREN/job_time.txt
docker run --rm --user 1000:1000 -it --env-file ./.env -v $REDPANDA/07CatJuridique_SQL.yaml:/07CatJuridique_SQL.yaml   -v $FILESIREN:$FILESIREN   docker.redpanda.com/redpandadata/connect run ./07CatJuridique_SQL.yaml
echo "$(date) 08 code NAF V2 PostgreSQL" >> $FILESIREN/job_time.txt
docker run --rm --user 1000:1000 -it --env-file ./.env -v $REDPANDA/08CodeNaf_SQL.yaml:/08CodeNaf_SQL.yaml   -v $FILESIREN:$FILESIREN   docker.redpanda.com/redpandadata/connect run ./08CodeNaf_SQL.yaml
echo "$(date) 09 Stock Etablissement Geo Zip" >> $FILESIREN/job_time.txt
docker run --rm --user 1000:1000 -it --env-file ./.env -v $REDPANDA/09StockEtablissementGeoZIP.yaml:/09StockEtablissementGeoZIP.yaml   -v $FILESIREN:$FILESIREN   docker.redpanda.com/redpandadata/connect run ./09StockEtablissementGeoZIP.yaml
echo "$(date) 10 Stock Etablissement Geo Zip to CSV" >> $FILESIREN/job_time.txt
docker run --rm --user 1000:1000 -it --env-file ./.env -v $REDPANDA/10StockEtablissementGeoZIP_csv.yaml:/10StockEtablissementGeoZIP_csv.yaml   -v $FILESIREN:$FILESIREN   docker.redpanda.com/redpandadata/connect run ./10StockEtablissementGeoZIP_csv.yaml
echo "$(date) 10 Stock Etablissement Geo PostgreSQL" >> $FILESIREN/job_time.txt
docker run --rm --user 1000:1000 -it --env-file ./.env -v $REDPANDA/11StockEtablisGeo_SQL.yaml:/11StockEtablisGeo_SQL.yaml   -v $FILESIREN:$FILESIREN   docker.redpanda.com/redpandadata/connect run ./11StockEtablisGeo_SQL.yaml
echo "$(date) End of Bash" >> $FILESIREN/job_time.txt
# docker run --rm --user 1000:1000 -it --env-file ./.env -v $REDPANDA/low_StockEtablissementZIP_csv.yaml:/low_StockEtablissementZIP_csv.yaml -v $FILESIREN:$FILESIREN  docker.redpanda.com/redpandadata/connect run ./low_StockEtablissementZIP_csv.yaml
# docker run --rm --user 1000:1000 -it --env-file ./.env -v $REDPANDA/06StockUniteLegale_SQL_join.yaml:/06StockUniteLegale_SQL_join.yaml   -v $FILESIREN:$FILESIREN   docker.redpanda.com/redpandadata/connect run ./06StockUniteLegale_SQL_join.yaml