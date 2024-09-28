#### Fichier du 28.09.2024 Version 1: Initialisiation ####

Explication des différentes étapes:

1) Téléchargement des fichiers du site https://www.data.gouv.fr/
2) décompression des fichiers à la volée pour les fichiers les inférieurs À 1Go
3) Uniquement Téléchargement des fichiers au format zip si supérieur à 1Go

Pour pouvoir executer les traitements, il faut tout d'abord créer un répertoire pour y stocker les fichiers téléchargés.

mkdir Files_Siren --> dans le script siren.sh, le répertoire se situe dans /home/ubuntu

Si GitHub disponible récupérer les fichiers actuellement présent dans la branche dev.

Pré-requis pour le container Redpanda (anciennement Benthos), avoir installer docker et docker-container

Lien vers le site https://docs.redpanda.com/current/get-started/quick-start/#configure-redpanda-in-docker

command: docker pull docker.redpanda.com/redpandadata/connect

Pour information l'execution des fichiers yaml à travers docker se réalise en mappant les chemins locales vers le container en y affectant les autorisations adéquates:

docker run --rm --user 1000:1000 -it -v $(pwd)/StockDoublons.yaml:/StockDoublons.yaml -v /home/ubuntu/Files_Siren:/home/ubuntu/Files_Siren  docker.redpanda.com/redpandadata/connect run ./StockDoublons.yaml

Dans le cadre du projet, il a été rajouté un fichier timestamp pour analyser la durée d'execution des fichiers.
job_time.txt


