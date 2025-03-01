"""Point d'entrée de l'application."""
import sys
from pathlib import Path
from dotenv import load_dotenv
from app.src.service.updater import UpdateService

app_path = Path(__file__).resolve().parent / "app"
sys.path.append(str(app_path))

def main():
    """Démarre le service de mise à jour."""
    # Charger les variables d'environnement
    load_dotenv()    
    # Démarrer le service
    service = UpdateService()
    service.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Au revoir!")
        sys.exit(0) 