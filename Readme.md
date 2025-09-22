# AyurFHIR Bridge: A Modern Terminology Service

**AyurFHIR Bridge** is a high-performance, open-source API designed to bridge the gap between traditional Indian medical terminologies (Ayurveda, Siddha, Unani) and modern global health standards like ICD-11 and LOINC.

This project provides a complete, production-ready terminology service, including robust data pipelines, a powerful REST API, and a demonstration user interface.

[![Build Status](https://img.shields.io/github/actions/workflow/status/your-github-username/your-repo-name/main.yml?branch=main)](https://github.com/your-github-username/your-repo-name/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Key Features

* **Unified Terminology:** Ingests and standardizes terms from Ayurveda, Siddha, and Unani into a single, searchable database.
* **Modern Standards:** Includes complete ingestion pipelines for ICD-11 and LOINC.
* **Automated Concept Mapping:** Intelligently creates a "first draft" map between NAMASTE and ICD-11 terms using the official WHO API.
* **High-Performance API:** Built with Python and FastAPI, offering fast, interactive, and automatically documented endpoints.
* **Easy Deployment:** Fully containerized with Docker and Docker Compose for a one-command setup.
* **Interactive UI:** A simple, responsive frontend to search all terminologies and view concept maps in real-time.

## Quick Start: Running the Service

Get the entire application stack (API, Database, Frontend) running in under 5 minutes.

**Prerequisites:**
* Docker
* Docker Compose

**Instructions:**

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-github-username/your-repo-name.git](https://github.com/your-github-username/your-repo-name.git)
    cd your-repo-name
    ```

2.  **Build and run the services:**
    ```bash
    docker-compose up --build
    ```

3.  **Access the services:**
    * **API Docs (Swagger UI):** `http://localhost:8000/docs`
    * **Frontend UI:** `http://localhost:8000/`

## Data Pipelines

To use the API, you must first populate the database. The ingestion scripts should be run in the following order from your terminal.

1.  **Ingest Core Terminologies:**
    ```bash
    python -m scripts.ingest_icd11
    python -m scripts.ingest_loinc
    python -m scripts.pipeline_namaste
    ```

2.  **Build the Concept Map:**
    *Note: This script makes thousands of live API calls to the WHO server and can take a long time to complete. It can be safely stopped and restarted.*
    ```bash
    python -m scripts.build_live_map
    ```

## API Endpoints

The API is divided into two main categories.

### 1. Terminology Search

| Method | Path              | Description                                                  |
| :----- | :---------------- | :----------------------------------------------------------- |
| `GET`  | `/search/namaste` | Searches for terms across Ayurveda, Siddha, and Unani systems. |
| `GET`  | `/search/icd11`   | Searches for terms within the ICD-11 terminology.            |
| `GET`  | `/search/loinc`   | Searches for terms within the LOINC terminology.             |

**Example:** `GET /search/namaste?term=fever`

### 2. Concept Mapping

| Method | Path   | Description                                                                                              |
| :----- | :----- | :------------------------------------------------------------------------------------------------------- |
| `GET`  | `/map` | Retrieves the full ICD-11 map for a specific NAMASTE code, identified by its `code` and `system`. |

**Example:** `GET /map?namaste_code=A-2&namaste_system=unani`

## Technology Stack

* **Backend:** Python, FastAPI
* **Database:** PostgreSQL
* **Deployment:** Docker, Docker Compose
* **Data Processing:** Pandas
* **Frontend:** HTML, Tailwind CSS, JavaScript

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` file for details on how to get started.

## License

This project is licensed under the MIT License.