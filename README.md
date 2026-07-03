# Incidents Microservice - FleetOps Platform

## Overview

**Incidents Microservice** is a production-grade backend service for managing vehicle and driver incidents within the FleetOps platform. It implements a **Hexagonal (Ports & Adapters) architecture** with unit test coverage, asynchronous event-driven coordination, and resilience patterns.

The service centralizes incident registration, validation, querying

**Built With:** Python 3.11, Django 4.2 LTS, PostgreSQL 16, Docker

---

## Architecture

Revisar

### Architectural Style: Hexagonal (Ports & Adapters)

The microservice isolates **pure domain logic** from external technologies:

- **Domain Core** (`incidents/domain/`): Business logic, aggregates, value objects, domain services
- **Application Layer** (`incidents/application/`): Use cases, orchestration, DTOs
- **Infrastructure Adapters** (`incidents/infrastructure/`): REST API, databases, message brokers, HTTP clients

### Design Patterns

**Circuit Breaker** - Resilience for Vehicle microservice calls  
**Repository Pattern** - Abstracted persistence via Hexagonal ports  
**DDD (Domain-Driven Design)** - Aggregate roots, value objects, domain events

### Quality Attributes (ISO/IEC 25010)

Revisar 

| Attribute | Priority | Implementation |
| :--- | :--- | :--- |
| **Availability** | CRITICAL | Circuit Breaker, health checks |
| **Trazability** | CRITICAL | Immutable incident records |
| **Resilience** | CRITICAL | message retry policies |
| **Modifiability** | HIGH | Hexagonal isolation; adapters swappable |
| **Scalability** | HIGH | Stateless REST, containerized, horizontal replication |

---

## Prerequisites

### System Requirements
- **Docker** 24.0+
- **Docker Compose** 2.20+
- **Python** 3.11+ (for local development)
- **Git** 2.40+

### Optional Local Development
- **PostgreSQL** 16+ (if running without Docker)
---

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/FleetOps-Corp/FleetOps-Incidents-Service
```

### 2. Run with Docker Compose

```bash
# Start all services (PostgreSQL, Incidents API)
docker compose up --build
docker-compose up --build
```

### 3. Verify Deployment

```bash
# Check services are running
docker-compose ps

# Verify API is responding
curl -X GET http://localhost:8000/api/incidents/

```

### 4. Stop Services

```bash
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v
```

---

## Local Development (Without Docker)

### Setup Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

o en Windows

```bash
python -m venv venv
env\Scripts\activate

pip install -r requirements.txt
```

### Run Database Migrations

```bash
python manage.py migrate
```

---

## Running Tests

Before commiting or open pr to develop and main branches, run the following commands to check the quality of it

### Mypy check

```bash
mypy .
```

### Ruff check

```bash
ruff check .
```

### Black check

```bash
black --check .
```
if errors occur, use ```black .``` in the root terminal

### Unit Tests (100% Coverage Target)

```bash
# Run all unit tests
pytest

# Run with coverage report
pytest --cov=incidents --cov-report=html

# View HTML coverage report
open htmlcov/index.html

# Run specific test class
pytest tests/unit/test_domain/models/test_incident.py::TestIncidentAggregateRoot -v
```

### Integration Tests

```bash
# Run E2E workflow test
pytest tests/integration/test_register_incident_e2e.py -v
```

### Generate Coverage Report

```bash
# Text report
coverage report

# HTML report (detailed)
coverage html
open htmlcov/index.html

# Enforce minimum coverage
coverage report --fail-under=95
```

### Sonarqube analysis

the following command runs an analysis on sonarqube, when the analysis is done can be checked in the next link: https://sonarcloud.io/project/overview?id=FleetOps-Corp_FleetOps-Incidents-Service 

```bash
docker run --rm   -e SONAR_TOKEN="env.SONAR_TOKEN"   -v "$(pwd):/usr/src"   sonarsource/sonar-scanner-cli
```

---

## API Endpoints

### Get All Incidents

Retrieves all registered incidents. The endpoint also supports filtering using query parameters.

**Endpoint**

```http
GET /api/incidents/
```

#### Supported Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `incident_type` | Filter by incident type | `?incident_type=MECANICO` |
| `severity` | Filter by severity | `?severity=GRAVE` |
| `vehicle_id` | Filter by vehicle ID (license plate) | `?vehicle_id=ABC-129` |
| `driver_id` | Filter by driver ID | `?driver_id=CONDUCTOR-001` |
| `start_date` | Start date and time (ISO 8601) | `?start_date=2026-06-01T00:00:00` |
| `end_date` | End date and time (ISO 8601) | `?end_date=2026-06-24T23:59:59` |

#### Example Requests

```http
GET /api/incidents/
```

```http
GET /api/incidents/?incident_type=MECANICO
```

```http
GET /api/incidents/?severity=GRAVE&tipo_incidente=MECANICO
```

```http
GET /api/incidents/?vehicle_id=ABC-123&gravedad=GRAVE
```

```http
GET /api/incidents/?driver_id=CONDUCTOR-001
```

```http
GET /api/incidents/?start_date=2026-06-01T00:00:00&end_date=2026-06-24T23:59:59
```

```http
GET /api/incidents/?incident_type=HUMANO&start_date=2026-06-01T00:00:00
```

---

### Get Incident by ID

Retrieves a single incident using its unique identifier.

**Endpoint**

```http
GET /api/incidents/{incident_id}
```

#### Example

```http
GET /api/incidents/INC-20260624-a460
```

#### Response

```json
{
  "incident_id": "INC-20260624-a460",
  "event_date": "2026-06-24T15:00:00+00:00",
  "driver_id": "CONDUCTOR-002",
  "vehicle_id": "ABC-124",
  "incident_type": "MECANICO",
  "severity": "LEVE",
  "description": "El vehículo presentó falla en los frenos durante la ruta.",
  "created_at": "2026-06-25T00:46:37.207518+00:00",
  "updated_at": "2026-06-25T00:46:37.207538+00:00"
}
```

---

### Create Incident

Creates a new incident.

**Endpoint**

```http
POST /api/incidents/create/
```

#### Request Body

```json
{
    "driver_id": "CONDUCTOR-098",
    "vehicle_id": "ABC-129",
    "incident_type": "MECANICO",
    "severity": "GRAVE",
    "description": "El conductor se estrello",
    "event_date": "2026-06-24T10:00:00"
}
```

#### Response

```json
{
  "incident_id": "INC-20260624-116a",
  "event_date": "2026-06-24T10:00:00-05:00",
  "driver_id": "CONDUCTOR-098",
  "vehicle_id": "ABC-129",
  "incident_type": "MECANICO",
  "severity": "GRAVE",
  "description": "El conductor se estrello",
  "created_at": "2026-07-02T00:18:37.763930",
  "updated_at": "2026-07-02T00:18:37.763934"
}
```
---


## CI/CD Pipeline

This project uses **GitHub Actions** to automate code quality verification, testing, and Docker image validation. The pipeline is triggered on every **push** and **pull request** targeting the `main` and `develop` branches.

### Continuous Integration (CI)

The CI workflow performs the following tasks:

1. Checks out the project source code.
2. Sets up a Python 3.11 environment.
3. Installs all project dependencies.
4. Starts a temporary PostgreSQL service for testing.
5. Performs static code analysis using:
   - Ruff
   - MyPy
   - Black (format verification)
6. Executes:
   - Unit tests
   - Integration tests
7. Generates a code coverage report.
8. Uploads coverage results to Codecov.

### Docker Validation

After all tests pass successfully, the pipeline:

1. Builds the Docker image for the Incident Service.
2. Starts a container from the generated image.
3. Executes the unit test suite inside the container to verify that the application runs correctly in its deployment environment.
---

**Generated:** July 1, 2026 | **Version:** 2.0
