AyurFHIR Bridge: Project Documentation
Project: AyurFHIR Bridge
Problem Statement: ID25026 (Smart India Hackathon)
Date: September 18, 2025
1. Introduction
AyurFHIR Bridge is a lightweight, FHIR-compliant microservice designed to bridge the gap between India's traditional Ayush medical terminologies (NAMASTE) and the global ICD-11 standard. It provides a full-stack solution for enabling dual-coding in Electronic Medical Record (EMR) systems, ensuring compliance with India's EHR Standards.
2. Features ✨
Automated Data Pipeline: A fully automated, resumable ETL pipeline that processes raw NAMASTE codes (Ayurveda, Siddha, Unani), cleans them, and maps them to ICD-11 (TM2) codes by querying the official WHO API.
FHIR R4 Compliant API: A robust FastAPI backend that serves terminology lookups and generates valid FHIR Condition resources.
Dual-Coding Engine: The core logic generates FHIR resources containing both the original NAMASTE code and the mapped ICD-11 code, fulfilling a key requirement for interoperability.
Secure & Auditable: Features a secure endpoint simulating ABHA token validation and provides a clear audit trail for data ingestion, adhering to national EHR standards.
Interactive Web UI: A simple, clean frontend to demonstrate the search, translation, and secure upload functionality in real-time.
Containerized & Reproducible: The entire application is containerized with Docker, ensuring a consistent and easy setup process.
3. Tech Stack 🛠️
Backend: Python, FastAPI
Database: PostgreSQL
Data Processing: Pandas
FHIR Handling: fhir.resources
Frontend: HTML, CSS, Vanilla JavaScript
Containerization: Docker, Docker Compose
4. Project Structure 📂
The project is organized into a clean, maintainable structure:
ayur-fhir-bridge/
├── app/                  # FastAPI application code
├── data/
│   ├── raw/              # Raw source NAMASTE CSVs go here
│   ├── processed/        # Intermediate and final processed data files
│   └── ...
├── frontend/             # HTML, CSS, and JS for the web UI
├── scripts/              # All Python scripts for the data ETL pipeline
├── docker-compose.yml    # Orchestrates the application and database
├── Dockerfile            # Defines the application's container
└── README.md


5. Setup and Installation
Prerequisites
Docker and Docker Compose
Python 3.10+
A Git client
Step 1: Clone the Repository
git clone <your-repository-url>
cd ayur-fhir-bridge


Step 2: Set Up the Python Environment
Create and activate a virtual environment to manage dependencies for running the data scripts.
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt


Step 3: Place Raw Data Files
Place your raw, unprocessed NAMASTE code CSV files for Ayurveda, Siddha, and Unani into the data/raw/ directory. Ensure they are named correctly:
data/raw/ayurveda.csv
data/raw/siddha.csv
data/raw/unani.csv
Step 4: Configure API Credentials
The data mapping script (scripts/mapper.py) requires credentials for the WHO ICD-11 API.
Open scripts/mapper.py.
Replace the placeholder values for CLIENT_ID and CLIENT_SECRET with your actual credentials.
6. Running the Project 🚀
Running the project is a three-step, fully automated process.
Command 1: Prepare the Data
This single command runs the entire automated and resumable ETL pipeline. It will filter, combine, and map all the raw data, producing the final enriched_namaste_codes_with_icd11.csv file.
python scripts/prepare_data.py


Command 2: Ingest Data into the Application
This command takes the final processed CSV and populates the application's PostgreSQL database. It will reset the database to ensure a clean import.
python scripts/ingest_data.py


Command 3: Run the Application
This command starts the FastAPI backend server and the PostgreSQL database using Docker Compose.
docker-compose up --build


Your AyurFHIR Bridge is now live and accessible.
7. How to Use 🌐
Open your web browser and navigate to http://localhost:8000.
Search for a term: In the search box, start typing a NAMASTE term (e.g., "gudabhraṁśaḥ"). A list of matching terms will appear.
Generate FHIR Resource: Click on a term from the list. A valid, dual-coded FHIR Condition resource will be generated and displayed in the text area.
Save to EMR: Click the "Save to EMR" button. This will send the FHIR resource as part of a Bundle to the secure /bundle endpoint. You will see a success alert.
Verify Audit Trail: In the terminal where Docker is running, you will see the AUDIT LOG printed, confirming the secure and audited ingestion of the data.
