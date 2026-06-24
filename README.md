# Incidents Microservice - FleetOps Platform

## Overview

**Incidents Microservice** is a production-grade backend service for managing vehicle and driver incidents within the FleetOps platform. It implements a **Hexagonal (Ports & Adapters) architecture** with 100% unit test coverage, asynchronous event-driven coordination, and resilience patterns.

The service centralizes incident registration, validation, querying, and SAGA-based coordination with downstream microservices (Vehicles, Mantenimiento, Asignaciones).

**Built With:** Python 3.11, Django 4.2 LTS, PostgreSQL 16, RabbitMQ 3.13, Docker

---

## Architecture

### Architectural Style: Hexagonal (Ports & Adapters)

The microservice isolates **pure domain logic** from external technologies:

- **Domain Core** (`incidents/domain/`): Business logic, aggregates, value objects, domain services
- **Application Layer** (`incidents/application/`): Use cases, orchestration, DTOs
- **Infrastructure Adapters** (`incidents/infrastructure/`): REST API, databases, message brokers, HTTP clients

### Design Patterns

✅ **Circuit Breaker** - Resilience for Vehicle microservice calls  
✅ **SAGA Pattern** - Distributed transaction coordination with compensations  
✅ **Repository Pattern** - Abstracted persistence via Hexagonal ports  
✅ **Message Broker Pattern** - Async decoupling with RabbitMQ  
✅ **API Gateway** - Centralized auth, JWT validation, rate limiting  
✅ **DDD (Domain-Driven Design)** - Aggregate roots, value objects, domain events

### Quality Attributes (ISO/IEC 25010)

| Attribute | Priority | Implementation |
| :--- | :--- | :--- |
| **Availability** | CRITICAL | Circuit Breaker, dead-letter queues, health checks |
| **Trazability** | CRITICAL | Immutable incident records + audit trail |
| **Resilience** | CRITICAL | SAGA pattern, message retry policies |
| **Security** | CRITICAL | JWT auth via API Gateway, input validation |
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
- **RabbitMQ** 3.13+ (if running without Docker)

---

## Quick Start

### 1. Clone and Setup

```bash
git clone [insert link for repo]
```

### 2. Run with Docker Compose

```bash
# Start all services (PostgreSQL, RabbitMQ, Incidents API)
docker compose up --build
docker-compose up --build
```

### 3. Verify Deployment

```bash
# Check services are running
docker-compose ps

# Verify API is responding
curl -X GET http://localhost:8000/api/incidents/

# Access RabbitMQ Management Console
open http://localhost:15672
# Credentials: guest / guest
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
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Run Database Migrations

```bash
python manage.py migrate
```

### Start Development Server

```bash
python manage.py runserver 0.0.0.0:8000 --settings incidents.settings.development
```

---

## Running Tests

### Unit Tests (100% Coverage Target)

```bash
# Run all unit tests
pytest tests/unit -v

# Run with coverage report
pytest tests/unit --cov=incidents --cov-report=html

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

---

## API Endpoints

on building . . .

## Project Structure

```
incidents-microservice/
│
├── incidents/
│   ├── domain/                          # Pure business logic layer
│   │   ├── models/                      # Aggregates, value objects
│   │   ├── services/                    # Domain services (orchestration)
│   │   ├── ports/                       # Hexagonal interfaces (repository, broker, client)
│   │   ├── events/                      # Domain events (for SAGA)
│   │   └── exceptions/                  # Domain exceptions
│   │
│   ├── application/                     # Use cases layer
│   │   ├── use_cases/                   # Use case orchestrators
│   │   ├── dtos/                        # Data transfer objects
│   │   └── exceptions/                  # Application exceptions
│   │
│   ├── infrastructure/                  # Adapters layer
│   │   ├── api/                         # REST API (Driving Adapter)
│   │   ├── adapters/
│   │   │   ├── persistence/             # Database (Driven Adapter)
│   │   │   ├── messaging/               # RabbitMQ (Driven Adapter)
│   │   │   ├── http_clients/            # Vehicle service (Driven Adapter)
│   │   │   └── logging/                 # Logging infrastructure
│   │   └── config/                      # Django app configuration
│   │
│   ├── settings/                        # Django settings (base, dev, prod)
│   ├── manage.py                        # Django entry point
│   └── urls.py                          # Root URL routing
│
├── tests/
│   ├── unit/                            # Unit tests (mocked adapters)
│   │   ├── test_domain/                 # Domain layer tests
│   │   ├── test_application/            # Application layer tests
│   │   └── test_infrastructure/         # Adapter tests
│   └── integration/                     # E2E tests (all layers)
│
├── Dockerfile                           # Multi-stage Docker build
├── docker-compose.yml                   # Local development environment
├── requirements.txt                     # Python dependencies
├── .env.example                         # Environment template
├── .coveragerc                          # Coverage configuration
├── .gitignore                           # Git ignore rules
└── README.md                            # This file
```

---

## Architectural Decisions

### Key ADRs (Architectural Decision Records)

1. **Hexagonal Architecture** ← Maximizes testability, modularity, and technology independence
2. **PostgreSQL with Immutable Incident Records** ← Strong audit trail, ACID compliance
3. **SAGA Pattern for Distributed Transactions** ← Eventual consistency across microservices
4. **RabbitMQ for Async Communication** ← Complete decoupling, fault tolerance
5. **Circuit Breaker for External Calls** ← Resilience, fail-fast, prevent cascading failures
6. **100% Unit Test Coverage** ← Production confidence, regression prevention
7. **Django REST Framework** ← Mature, battle-tested, excellent ecosystem

See `ARCHITECTURE.md` for detailed ADRs.

---

## CI/CD Pipeline

**GitHub Actions Workflow** (`.github/workflows/ci-cd.yml`):

1. **Build Phase**
   - Checkout code
   - Setup Python 3.11

2. **Test Phase**
   - Run unit tests (pytest)
   - Run integration tests
   - Generate coverage report
   - Upload to Codecov

3. **Lint Phase**
   - Flake8 (code style)
   - Black (code formatting)

4. **Docker Phase** (on main branch only)
   - Build multi-stage Docker image
   - Verify image runs tests

**Commands:**

```bash
# Run all checks locally (before pushing)
pytest tests/ --cov=incidents
flake8 incidents tests
black --check incidents tests

# Auto-format code
black incidents tests
isort incidents tests
```

---

## Known Limitations & Recommendations

### Current Limitations

1. **SAGA Orchestration Simplified** - Production should use dedicated saga orchestrator or choreography with saga state table
2. **Synchronous Vehicle Validation** - Only synchronous REST call; consider async with DLQ fallback for critical path
3. **No Circuit Breaker Fallback** - Failed vehicle validation aborts; could implement graceful degradation

### Recommendations for Production

- [ ] Implement Saga Orchestrator (Temporal, Cadence, or lightweight custom)
- [ ] Add distributed tracing (Jaeger, DataDog)
- [ ] Implement comprehensive monitoring (Prometheus, Grafana)
- [ ] Add API versioning strategy
- [ ] Implement request correlation IDs
- [ ] Add request/response logging middleware
- [ ] Implement API rate limiting per user/client
- [ ] Add database connection pooling optimization
- [ ] Implement graceful shutdown for containers
- [ ] Add support for incident state machine with advanced workflows

---

**Generated:** June 10, 2026 | **Version:** 1.0.0
