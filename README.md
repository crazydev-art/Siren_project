Siren Project
Overview
The Siren Project is a data engineering and web application platform designed to process and visualize SIREN/SIRET data for French companies. It features a React/TypeScript frontend for user interaction, backend services for data processing using Redpanda and PostgreSQL, and monitoring with Prometheus and Grafana. The project is fully containerized with Docker, enabling easy deployment and scalability.
Features

Frontend Interface: A React-based UI with company search, map visualization, and user authentication.
Data Processing: ETL pipelines for handling SIREN/SIRET datasets.
Real-Time Streaming: Redpanda for high-throughput data streaming.
Monitoring: Prometheus and Grafana dashboards for system and database performance.
Containerization: Docker and Docker Compose for simplified service orchestration.

Project Structure
Siren_project/
├── Frontend/
│   └── Frontend/                   # React/TypeScript frontend
│       ├── src/                    # Source code (components, pages, API logic)
│       ├── package.json            # Frontend dependencies
│       ├── tailwind.config.js      # Tailwind CSS configuration
│       ├── vite.config.ts          # Vite build configuration
│       └── start.sh                # Script to start the frontend
├── siren/                          # Backend and data processing services
│   ├── Files_Siren/                # SIREN/SIRET data and configuration files
│   │   ├── environ.txt             # Environment configuration
│   │   └── job_time.txt            # Job timing configuration
│   ├── Redpanda/                   # Redpanda streaming configuration
│   │   └── .env                    # Redpanda environment variables
│   ├── Redpanda_connect/           # Redpanda connectors
│   │   └── .env                    # Connector environment variables
│   ├── UserTable_Join/             # User table processing scripts and tests
│   │   ├── tests/                  # Test scripts (e.g., inner_join_test.py)
│   │   ├── user_table.py           # User table processing script
│   │   ├── Dockerfile              # Docker configuration for user table service
│   │   └── .env                    # Environment variables
│   ├── data_updater/               # Data update scripts and services
│   │   ├── app/                    # Data updater application
│   │   │   └── .env                # Application environment variables
│   │   └── .env                    # Data updater environment variables
│   ├── prometheus-grafana-siren/   # Monitoring configurations
│   │   ├── grafana/                # Grafana dashboards
│   │   │   └── provisioning/
│   │   │       └── dashboards/     # Dashboard configurations
│   │   └── prometheus/             # Prometheus configurations
│   ├── docker-compose.yaml         # Docker Compose for service orchestration
│   ├── setenv.sh                   # Environment setup script
│   └── setenvV2.sh                 # Alternative environment setup script

Prerequisites

Docker and Docker Compose: For running services.
Node.js (v16 or higher): For frontend development.
Python (3.8 or higher): For backend scripts and tests.
Git: For version control.
Redpanda: For streaming (included in Docker setup).
PostgreSQL: For data storage (included in Docker setup).

Installation

Clone the repository:
git clone https://github.com/crazydev-art/Siren_project.git
cd Siren_project


Set up environment variables:
Copy the example environment files and configure them:
cp siren/Redpanda/.env.example siren/Redpanda/.env
cp siren/Redpanda_connect/.env.example siren/Redpanda_connect/.env
cp siren/UserTable_Join/.env.example siren/UserTable_Join/.env
cp siren/data_updater/.env.example siren/data_updater/.env
cp siren/data_updater/app/.env.example siren/data_updater/app/.env

Edit the .env files to include your settings (e.g., database credentials, Redpanda brokers, API keys).

Start services with Docker Compose:
Launch Redpanda, PostgreSQL, Grafana, and other services:
docker-compose -f siren/docker-compose.yaml up -d


Install frontend dependencies:
Navigate to the frontend directory and install dependencies:
cd Frontend/Frontend
npm install


Run the frontend:
Start the development server:
npm run dev

The frontend is accessible at http://localhost:5173 (or the port specified in vite.config.ts).

Run backend scripts:
Execute environment setup scripts:
cd siren
chmod +x setenv.sh setenvV2.sh
./setenv.sh

Run data processing scripts (e.g., siren/UserTable_Join/user_table.py) as needed.


Usage

Frontend: Access the web interface at http://localhost:5173. Features include:
Search: Query companies by SIREN/SIRET.
Map: View company locations on an interactive map.
Authentication: Sign in or sign up for personalized features.


Backend: Use scripts in siren/UserTable_Join or siren/data_updater to process SIREN/SIRET data.
Monitoring: Access Grafana at http://localhost:3000 to view dashboards:
Docker Monitoring: Tracks container performance.
PostgreSQL Metrics: Monitors database queries and performance.



Testing
Run backend tests for data processing scripts:
cd siren/UserTable_Join
python -m pytest tests/

Monitoring

Prometheus: Collects metrics for Docker containers and PostgreSQL.
Grafana: Dashboards are in siren/prometheus-grafana-siren/grafana/provisioning/dashboards/:
Docker Monitoring-1742827887324.json: Container metrics.
PostgreSQL Database DataEng-1742828064841.json: Database performance.



Contributing

Fork the repository.
Create a feature branch (git checkout -b feature/your-feature).
Commit your changes (git commit -m "Add your feature").
Push to your fork (git push origin feature/your-feature).
Open a pull request to the dev branch.

Please adhere to the Code of Conduct and ensure tests pass before submitting.
License
This project is licensed under the MIT License. See the LICENSE file for details.
Contact
For questions, bug reports, or feature requests, open an issue on the GitHub Issues page.

Built with ❤️ by the Siren Project team.
