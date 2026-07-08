# Incidents Microservice - FleetOps Platform

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=FleetOps-Corp_FleetOps-Incidents-Service&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=FleetOps-Corp_FleetOps-Incidents-Service)


Backend service for managing vehicle and driver incidents within the FleetOps platform. The service uses a hexagonal architecture with Django REST Framework, PostgreSQL, a synchronous vehicle validation call protected by Circuit Breaker, and asynchronous event publication through AWS SNS/SQS.

## Overview

The microservice handles three core actions:

- Register incidents after validating that the vehicle exists in the Vehicles service.
- Query incidents by type, severity, driver, vehicle, or date range.
- Retrieve a single incident by its identifier.

Incident records are immutable once created. The service persists audit timestamps (`created_at`, `updated_at`) and exposes REST endpoints only through the API layer.

## Architecture

### Hexagonal Structure

The project is organized into three main layers:

- `incidents/domain/`: core entities, value objects, ports, and business services.
- `incidents/application/`: use cases and DTOs that coordinate the domain.
- `incidents/infrastructure/`: REST API, persistence, HTTP client, messaging, and configuration.

### Design Patterns

- Hexagonal Architecture (Ports and Adapters)
- Circuit Breaker for the synchronous Vehicles validation call
- Repository Pattern for persistence
- Event publication through AWS SNS with SQS fan-out

### Quality Attributes

- Availability: fail-fast vehicle validation with Circuit Breaker.
- Traceability: immutable incident records with audit timestamps.
- Resilience: event publication failures are logged and do not block incident creation.
- Modifiability: adapters can be replaced without changing domain logic.
- Scalability: stateless REST API and containerized deployment.

## Tech Stack

- Python 3.11
- Django 4.2 LTS
- Django REST Framework
- PostgreSQL 16
- Docker
- AWS SNS / SQS
- pybreaker
- requests
- boto3

## Project Structure

- `manage.py`: Django management entry point.
- `incidents/urls.py`: root URL configuration and health check.
- `incidents/settings/`: environment-specific Django settings.
- `incidents/application/use_cases/`: application workflows.
- `incidents/domain/models/`: domain entities and value objects.
- `incidents/domain/services/`: business services.
- `incidents/domain/ports/`: repository, message publisher, and vehicle client ports.
- `incidents/infrastructure/api/`: serializers, views, and API routing.
- `incidents/infrastructure/adapters/`: persistence, messaging, HTTP client, and logging adapters.
- `tests/`: unit and integration tests.

## Requirements

- Docker 24+
- Docker Compose 2.20+
- Python 3.11+
- Git 2.40+

## Local Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a local `.env` file or export the required variables used by the project:

- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `VEHICLES_API_URL`
- `SNS_TOPIC_ARN`
- `AWS_REGION`
- `DJANGO_SECRET_KEY`
- `JWT_ALGORITHM`
- `JWT_PUBLIC_KEY_PATH`

### 4. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Run with Docker

```bash
docker compose up --build
```

Or use

```bash
docker-compose up --build
```

To stop the stack:

```bash
docker compose down

# Remove volumes (clean slate)
docker-compose down -v
```

## API Endpoints

### Health Check

```http
GET /health
```

### List and Filter Incidents

```http
GET /api/incidents/
```

Supported query parameters:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `incident_type` | Filter by incident type | `?incident_type=MECANICO` |
| `severity` | Filter by severity | `?severity=GRAVE` |
| `vehicle_id` | Filter by vehicle ID (license plate) | `?vehicle_id=ABC-129` |
| `driver_id` | Filter by driver ID | `?driver_id=CONDUCTOR-001` |
| `start_date` | Start date and time (ISO 8601) | `?start_date=2026-06-01T00:00:00` |
| `end_date` | End date and time (ISO 8601) | `?end_date=2026-06-24T23:59:59` |

Example requests:

```http
GET /api/incidents/?incident_type=MECANICO
```

```http
GET /api/incidents/?severity=GRAVE&tipo_incidente=MECANICO
```

```http
GET /api/incidents/?start_date=2026-06-01T00:00:00&end_date=2026-06-24T23:59:59
```

```http
GET /api/incidents/?incident_type=HUMANO&start_date=2026-06-01T00:00:00
```

### Get Incident by ID

```http
GET /api/incidents/{incident_id}/
```

Example request:

```http
GET /api/incidents/INC-20260624-a460
```

Response body example:

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

### Create Incident

```http
POST /api/incidents/create/
```

Request body example:

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

Response body example: 

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

## Testing and Quality

Run the main quality checks with:

```bash
mypy .
ruff check .
black --check .
pytest
pytest --cov=incidents --cov-report=xml --cov-report=html
coverage report --fail-under=95
```

If there is fixable errors with **ruff** run the following command

```bash
ruff check --fix
```

And, if errors with formatting happen, use ```black .```


For integration testing:

```bash
pytest tests/integration/test_register_incident_e2e.py -v
```

### SonarCloud

Run a local Sonar scan with:

```bash
docker run --rm -e SONAR_TOKEN="env.SONAR_TOKEN" -v "$(pwd):/usr/src" sonarsource/sonar-scanner-cli
```

## Behavior Notes

- Vehicle validation is the only synchronous REST call between microservices.
- The call is protected with Circuit Breaker and fails fast on Vehicles service errors.
- Incident publication is best-effort: if SNS publishing fails, the incident still remains saved.
- The current implementation does not model incident status transitions.

## CI/CD Pipeline

This project uses **GitHub Actions** to automate code quality verification, testing, and Docker image validation. The pipeline is triggered on every **push** and **pull request** targeting the `main` and `develop` branches.

### Continuous Integration (CI)

The CI workflow is automatically triggered on every push and pull request targeting the **main** and **develop** branches. It performs the following tasks:

1. Checks out the project source code.
2. Sets up a **Python 3.11** environment.
3. Installs all project dependencies defined in `requirements.txt`.
4. Starts a temporary **PostgreSQL 16** service for integration testing.
5. Performs static code analysis using:
   - Ruff
   - MyPy
6. Executes:
   - Unit tests with code coverage (minimum coverage: **80%**)
   - Integration tests
7. Generates code coverage reports in XML and HTML formats.
8. Uploads the coverage report to **Codecov**.
9. Runs a **SonarCloud** scan to analyze code quality, maintainability, and potential security issues.
10. Verifies code formatting using **Black**.

### Continuous Delivery (CD)

When all CI checks pass successfully and changes are merged into the **main** branch, the delivery pipeline:

1. Checks out the project source code.
2. Sets up **Docker Buildx**.
3. Authenticates with **Docker Hub** using repository secrets.
4. Builds the Docker image for the Incident Service.
5. Pushes the generated image to Docker Hub using the `latest` tag.

---

## Related Documentation

- [DAS del microservicio](docs/DAS_Microservicio_Incidentes_FleetOps.docx.md)
- [Docker Compose](docker-compose.yml)
- [Django settings](incidents/settings/base.py)

---

**Generated:** July 05, 2026 | **Version:** 2.0