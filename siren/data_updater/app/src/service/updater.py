"""Service principal de mise à jour des établissements et unités légales."""

import time
import requests
import psycopg2
from datetime import datetime

from app.src.config.settings import UPDATE_INTERVAL
from app.src.utils.logger import DatabaseLogger
from app.src.api.siret import fetch_etablissement_data
from app.src.api.siren import fetch_unitelegale_data
from app.src.database.loader import (
    load_data_to_staging,
    update_from_staging,
    dump_and_clear_staging
)

from app.src.api.base_client import BaseInseeClient

class UpdateService:
    """Service de mise à jour des établissements et unités légales."""

    def __init__(self):
        self.logger = DatabaseLogger()
        # Initialiser les clients à None
        self.etab_client = None
        self.ul_client = None

    def init_clients(self):
        """Initialise les clients INSEE."""
        self.etab_client = BaseInseeClient("etablissement", "Établissements")
        self.ul_client = BaseInseeClient("unitelegale", "Unités Légales")

    def process_updates(self):
        """Exécute un cycle de mise à jour pour les deux types de données."""
        try:
            self.init_clients()
            api_calls = 0

            # 1. Mise à jour des établissements et adresses
            print("\n📦 Traitement des établissements et adresses")
            cursor_value = "*"
            cursor_suivant = ""
            initial_db_date = self.etab_client.get_initial_db_date()

            while cursor_value != cursor_suivant and cursor_value is not None:
                api_calls += 1
                data_tuple, next_cursor = fetch_etablissement_data(
                    cursor_value, 
                    client=self.etab_client,
                    db_date=initial_db_date
                )
            
                if not data_tuple or (not data_tuple[0] and not data_tuple[1]):
                    print("ℹ️ Plus de données à traiter")
                    break

                etab_data, adresse_data = data_tuple
                if etab_data and adresse_data:
                    success_etab = load_data_to_staging(etab_data, "etablissement")
                    success_addr = load_data_to_staging(adresse_data, "adresse")
                    
                    if success_etab and success_addr:
                        success_etab, records_etab = update_from_staging("etablissement")
                        success_addr, records_addr = update_from_staging("adresse")
                        
                        if success_etab and success_addr:
                            print(f"✅ Établissements traités : {records_etab} enregistrements")
                            print(f"✅ Adresses traitées : {records_addr} enregistrements")
                            
                            # Si aucune donnée n'a été traitée, on sort de la boucle
                            if records_etab == 0 and records_addr == 0:
                                print("ℹ️ Plus de nouvelles données à traiter")
                                break
                            
                            # Vider les tables staging après traitement réussi
                            dump_and_clear_staging("etablissement")
                            dump_and_clear_staging("adresse")
                    else:
                        print("❌ Erreur lors de la mise à jour des données")
                        break

                cursor_value = next_cursor
                time.sleep(4)

            # 2. Mise à jour des unités légales
            print("\n📦 Traitement des unités légales")
            cursor_value = "*"
            cursor_suivant = ""
            initial_db_date = self.ul_client.get_initial_db_date()

            while cursor_value != cursor_suivant and cursor_value is not None:
                api_calls += 1
                ul_data, next_cursor = fetch_unitelegale_data(
                    cursor_value, 
                    client=self.ul_client,
                    db_date=initial_db_date
                )
            
                if not ul_data:
                    print("ℹ️ Plus de données à traiter")
                    break

                success = load_data_to_staging(ul_data, "unitelegale")
                if success:
                    success, records = update_from_staging("unitelegale")
                    if success:
                        print(f"✅ Unités légales traitées : {records} enregistrements")
                        
                        if records == 0:
                            print("ℹ️ Plus de nouvelles données à traiter")
                            break
                            
                        # Dump et vide la table staging
                        dump_and_clear_staging("unitelegale")

                cursor_value = next_cursor
                time.sleep(4)

            print(f"\n📊 Nombre total d'appels API : {api_calls}")
                
        except Exception as e:
            self.logger.log_error("SERVICE", f"Erreur : {str(e)}")
            raise

    def run(self):
        """Démarre le service"""
        print("🚀 Service de mise à jour démarré")

        try:
            self.process_updates()
            print(f"💤 Prochaine mise à jour dans {UPDATE_INTERVAL}")
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du service")
        except (requests.RequestException, psycopg2.Error) as e:
            self.logger.log_error("SERVICE", f"Erreur critique: {str(e)}")
            time.sleep(60)  # Attendre avant de réessayer 