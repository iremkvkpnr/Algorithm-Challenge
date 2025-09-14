# VRP API - Vehicle Routing Problem Solver

A high-performance HTTP microservice for solving Vehicle Routing Problems (VRP) using Google OR-Tools. This service optimizes delivery routes by minimizing total delivery duration while respecting vehicle capacity and service time constraints.

## Features

- 🚀 **Fast REST API** with POST /solve endpoint
- 📦 **Vehicle Capacity Constraints** - Respects delivery capacity limits
- ⏱️ **Service Time Support** - Includes service duration at each location
- 🎯 **Duration Optimization** - Minimizes total delivery time
- 🔄 **Flexible Routes** - Vehicles can end their journey at any location
- ✅ **Input Validation** - Comprehensive request validation with Pydantic
- 📊 **Detailed Response** - Returns optimized routes with duration breakdown

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Algorithm-Challenge
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server:**
   ```bash
   python -m src.main
   ```

   The API will be available at `http://localhost:8000`

4. **View API documentation:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## API Reference

### Endpoint

**POST** `/solve`

Solves a Vehicle Routing Problem and returns optimized routes.

### Request Format

| Field | Type | Description |
|-------|------|-------------|
| `vehicles` | Array | List of available vehicles |
| `jobs` | Array | List of delivery jobs |
| `matrix` | 2D Array | Distance/time matrix between locations |

#### Vehicle Object
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Unique vehicle identifier |
| `start_index` | Integer | Starting location index in matrix |
| `capacity` | Integer | Maximum delivery capacity |

#### Job Object
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Unique job identifier |
| `location_index` | Integer | Delivery location index in matrix |
| `delivery` | Integer | Delivery size (capacity units) |
| `service` | Integer | Service time at location (time units) |

### Example Requests

#### Simple Single Vehicle Problem
```bash
curl -X POST "http://localhost:8000/solve" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicles": [
      {
        "id": 1,
        "start_index": 0,
        "capacity": 10
      }
    ],
    "jobs": [
      {
        "id": 1,
        "location_index": 1,
        "delivery": 3,
        "service": 100
      },
      {
        "id": 2,
        "location_index": 2,
        "delivery": 2,
        "service": 200
      }
    ],
    "matrix": [
      [0, 100, 150],
      [100, 0, 200],
      [150, 200, 0]
    ]
  }'
```

#### Multi-Vehicle Problem
```bash
curl -X POST "http://localhost:8000/solve" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicles": [
      {"id": 1, "start_index": 0, "capacity": 4},
      {"id": 2, "start_index": 0, "capacity": 6}
    ],
    "jobs": [
      {"id": 1, "location_index": 1, "delivery": 2, "service": 100},
      {"id": 2, "location_index": 2, "delivery": 3, "service": 150},
      {"id": 3, "location_index": 3, "delivery": 1, "service": 200}
    ],
    "matrix": [
      [0, 100, 200, 300],
      [100, 0, 150, 250],
      [200, 150, 0, 100],
      [300, 250, 100, 0]
    ]
  }'
```

### Response Format

```json
{
  "total_delivery_duration": 750,
  "routes": {
    "1": {
      "jobs": [1, 2],
      "delivery_duration": 450
    },
    "2": {
      "jobs": [3],
      "delivery_duration": 300
    }
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `total_delivery_duration` | Integer | Total time for all vehicles to complete deliveries |
| `routes` | Object | Routes assigned to each vehicle |
| `routes[vehicle_id].jobs` | Array | Ordered list of job IDs for this vehicle |
| `routes[vehicle_id].delivery_duration` | Integer | Total time for this vehicle's route |

**Note:** The `delivery_duration` includes:
- Travel time between locations
- Service time at each delivery location
- Does NOT include return to depot (vehicles can end anywhere)

## Test Scenarios

The following test scenarios demonstrate the service's capabilities and validate the service time calculations:

### Scenario 1: No Service Times
**Input:** 2 jobs without service times
```bash
curl -X POST "http://localhost:8000/solve" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicles": [{"id": 1, "start_index": 0, "capacity": 10}],
    "jobs": [
      {"id": 1, "location_index": 1, "delivery": 2},
      {"id": 2, "location_index": 2, "delivery": 3}
    ],
    "matrix": [[0, 100, 200], [100, 0, 150], [200, 150, 0]]
  }'
```
**Result:** `total_delivery_duration: 450` (travel only: 100 + 150 + 200)

### Scenario 2: With Service Times
**Input:** Same jobs with service times added
```bash
curl -X POST "http://localhost:8000/solve" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicles": [{"id": 1, "start_index": 0, "capacity": 10}],
    "jobs": [
      {"id": 1, "location_index": 1, "delivery": 2, "service": 100},
      {"id": 2, "location_index": 2, "delivery": 3, "service": 200}
    ],
    "matrix": [[0, 100, 200], [100, 0, 150], [200, 150, 0]]
  }'
```
**Result:** `total_delivery_duration: 750` (travel: 450 + service: 300)

### Scenario 3: Complex Multi-Vehicle
**Input:** Original challenge example with multiple vehicles and jobs
```bash
curl -X POST "http://localhost:8000/solve" \
  -H "Content-Type: application/json" \
  -d @sample_input.json
```
**Result:** `total_delivery_duration: 8780` (optimized multi-vehicle routing)

### Performance Validation

✅ **Service Time Calculation:** Correctly adds service duration to delivery locations  
✅ **Capacity Constraints:** Respects vehicle capacity limits  
✅ **Route Optimization:** Minimizes total delivery duration  
✅ **Multi-Vehicle Support:** Efficiently distributes jobs across vehicles  
✅ **Input Validation:** Comprehensive error handling for invalid requests  

## Architecture

### Technology Stack
- **FastAPI**: High-performance web framework with automatic API documentation
- **Google OR-Tools**: Industry-standard constraint programming solver
- **Pydantic**: Runtime data validation and serialization
- **Uvicorn**: Lightning-fast ASGI server

### Project Structure
```
src/
├── main.py                    # FastAPI application entry point
├── schemas/                   # Pydantic data models (renamed from models/)
│   ├── __init__.py           # Schema exports
│   ├── request_models.py     # VRP input data structures (renamed from input.py)
│   └── response_models.py    # VRP output data structures (renamed from output.py)
├── services/
│   └── vrp_service.py        # Core VRP solving logic
├── api/
│   └── routers/
│       └── vrp.py           # VRP API endpoints
├── validators/              # Input validation logic
├── repositories/            # Data access layer
├── config/                  # Configuration management
├── exceptions/              # Custom exception classes
└── utils/                   # Utility functions
    └── __init__.py
```

### Key Design Decisions

1. **🔄 Flexible End Points**: Vehicles can end their journey at any location (no return to depot required)
2. **📦 Simplified Inventory**: Vehicles carry unlimited stock - focus on capacity constraints only
3. **⚡ Zero Handover Time**: Service time is for the delivery process, not the actual handover
4. **🎯 Integer Precision**: Uses integer values for capacity/delivery for simplicity and performance
5. **🛡️ Comprehensive Validation**: All inputs validated before processing

### Algorithm Details

- **Solver**: Google OR-Tools VRP solver with time and capacity dimensions
- **Objective**: Minimize total delivery duration across all vehicles
- **Constraints**: 
  - Vehicle capacity limits
  - Service time requirements
  - Distance matrix constraints
- **Optimization**: First solution strategy with local search improvements

### Domain Model vs DTO Architecture

**Note:** Bu challenge için basit bir yaklaşım benimsenmiştir. Gerçek production projelerinde farklı bir mimari tercih edilir.

#### Bu Challenge'da Kullanılan Yaklaşım
- **Sadece Pydantic DTO'lar** kullanılmıştır
- **API katmanından** doğrudan **OR-Tools** solver'a geçiş
- **Basit ve hızlı** implementasyon

#### Production Projelerinde Önerilen Yaklaşım
```
API Layer (DTO) → Domain Layer (Business Logic) → Data Layer (Repository)
     ↓                        ↓                           ↓
  Validation            Business Rules              Database
```

**Domain Model Avantajları:**
- **Business Logic Centralization**: İş kuralları domain objelerinde toplanır
- **Separation of Concerns**: Her katman kendi sorumluluğuna odaklanır
- **Testability**: Business logic bağımsız olarak test edilebilir
- **Maintainability**: API değişiklikleri domain katmanını etkilemez

**DTO (Data Transfer Object) Avantajları:**
- **API Validation**: Pydantic ile otomatik doğrulama
- **Serialization**: JSON ↔ Python object dönüşümü
- **Documentation**: FastAPI ile otomatik API dokümantasyonu
- **Type Safety**: IDE desteği ve compile-time kontrol

**Bu projede neden Domain Model kullanılmadı?**
- Challenge kapsamında **business logic minimal**
- **Sadece veri dönüştürme** işlemi var
- **Hızlı geliştirme** öncelikli
- **Karmaşıklık** gereksiz olurdu

**Ne zaman Domain Model kullanmalı?**
- Karmaşık business rules olduğunda
- Çoklu API endpoint'leri olduğunda
- Farklı data source'ları olduğunda
- Uzun vadeli maintainability önemli olduğunda

## Büyük Projeler İçin Mimari Notları

**⚠️ ÖNEMLİ: Bu proje bir challenge kapsamında geliştirilmiştir ve büyük ölçekli production sistemler için aşağıdaki mimari iyileştirmeler gereklidir:**

### 1. Domain-Driven Design (DDD)
```
src/
├── domain/
│   ├── entities/          # Core business entities
│   ├── value_objects/     # Immutable value objects
│   ├── aggregates/        # Business logic aggregates
│   ├── repositories/      # Domain repository interfaces
│   └── services/          # Domain services
├── application/
│   ├── use_cases/         # Application use cases
│   ├── commands/          # Command handlers
│   ├── queries/           # Query handlers
│   └── dto/              # Application DTOs
├── infrastructure/
│   ├── persistence/       # Database implementations
│   ├── external/          # External service adapters
│   └── messaging/         # Event/message handling
└── presentation/
    ├── api/              # REST API controllers
    ├── graphql/          # GraphQL resolvers
    └── cli/              # Command line interface
```

### 2. Microservices Architecture
- **VRP Solver Service**: Core optimization algorithms
- **Route Management Service**: Route CRUD operations
- **Vehicle Service**: Vehicle fleet management
- **Job Service**: Delivery job management
- **Notification Service**: Real-time updates
- **Analytics Service**: Performance metrics

### 3. Event-Driven Architecture
```python
# Domain Events
class VRPSolutionCalculated(DomainEvent):
    solution_id: str
    total_duration: int
    routes_count: int

class RouteOptimized(DomainEvent):
    route_id: str
    vehicle_id: str
    optimization_percentage: float
```

### 4. CQRS (Command Query Responsibility Segregation)
```python
# Commands
class SolveVRPCommand:
    vehicles: List[Vehicle]
    jobs: List[Job]
    constraints: OptimizationConstraints

# Queries
class GetOptimalRoutesQuery:
    solution_id: str
    include_metadata: bool = True
```

### 5. Hexagonal Architecture (Ports & Adapters)
```python
# Ports (Interfaces)
class VRPSolverPort(ABC):
    @abstractmethod
    def solve(self, problem: VRPProblem) -> VRPSolution

# Adapters (Implementations)
class ORToolsAdapter(VRPSolverPort):
    def solve(self, problem: VRPProblem) -> VRPSolution:
        # OR-Tools implementation

class GoogleMapsAdapter(DistanceMatrixPort):
    def calculate_distances(self, locations: List[Location]) -> DistanceMatrix:
        # Google Maps API implementation
```

### 6. Scalability & Performance
- **Caching**: Redis for frequent route calculations
- **Message Queues**: RabbitMQ/Apache Kafka for async processing
- **Load Balancing**: Multiple solver instances
- **Database Sharding**: Partition by geographic regions
- **CDN**: Static route visualizations

### 7. Monitoring & Observability
- **Distributed Tracing**: Jaeger/Zipkin
- **Metrics**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Health Checks**: Kubernetes readiness/liveness probes

### 8. Security
- **Authentication**: OAuth 2.0 / JWT tokens
- **Authorization**: Role-based access control (RBAC)
- **API Rate Limiting**: Per-user/per-endpoint limits
- **Data Encryption**: At rest and in transit
- **Input Validation**: Comprehensive sanitization

### 9. DevOps & Deployment
- **Containerization**: Docker + Kubernetes
- **CI/CD**: GitLab CI / GitHub Actions
- **Infrastructure as Code**: Terraform
- **Blue-Green Deployment**: Zero-downtime updates
- **Auto-scaling**: Based on CPU/memory/queue length

### 10. Testing Strategy
```python
# Unit Tests
class TestVRPSolver:
    def test_optimal_solution_small_problem(self):
        # Test core algorithm logic

# Integration Tests
class TestVRPAPI:
    def test_end_to_end_solution_flow(self):
        # Test complete request-response cycle

# Performance Tests
class TestVRPPerformance:
    def test_large_scale_problem_solving(self):
        # Test with 1000+ vehicles, 10000+ jobs

# Contract Tests
class TestVRPContracts:
    def test_api_backward_compatibility(self):
        # Ensure API changes don't break clients
```

**Bu mimari yaklaşımlar, enterprise-level VRP sistemleri için gerekli olan ölçeklenebilirlik, maintainability ve reliability sağlar.**

## Error Handling

The API provides comprehensive error responses:

- **400 Bad Request**: Invalid input format or constraint violations

## Changelog

### v1.1.0 - Schema Restructuring

**Structural Changes:**
- 📁 **Renamed `models/` to `schemas/`** - Following FastAPI best practices for API data models
- 📄 **Renamed `input.py` to `request_models.py`** - More descriptive naming for API request structures
- 📄 **Renamed `output.py` to `response_models.py`** - More descriptive naming for API response structures
- 🔧 **Updated all import references** - All files now import from the new schema structure
- 📦 **Enhanced `schemas/__init__.py`** - Added proper exports for all schema classes

**Benefits:**
- ✅ **Better Code Organization** - Clear separation between request and response models
- ✅ **FastAPI Compliance** - Follows established FastAPI project structure conventions
- ✅ **Improved Maintainability** - More intuitive file naming and organization
- ✅ **Enhanced Developer Experience** - Easier to locate and understand data structures
- **422 Unprocessable Entity**: Data validation errors with detailed field information
- **500 Internal Server Error**: Solver failures or unexpected errors

## Testing

### Test Suite

The project includes a comprehensive test suite covering:

- **🧪 Unit Tests** (`test_vrp_service.py`): Core VRP solving logic validation
- **🔗 Integration Tests** (`test_api_integration.py`): End-to-end API testing
- **⚡ Performance Tests** (`test_performance.py`): Load testing and performance validation

### Running Tests

```bash
# Run all tests
PYTHONPATH=. pytest tests/ -v

# Run specific test file
PYTHONPATH=. pytest tests/test_vrp_service.py -v

# Run with coverage
PYTHONPATH=. pytest tests/ --cov=src --cov-report=html
```

### Test Coverage

- ✅ **VRP Service Logic**: Algorithm correctness and edge cases
- ✅ **API Endpoints**: Request/response validation
- ✅ **Error Handling**: Invalid input scenarios
- ✅ **Performance**: Large-scale problem solving (100+ vehicles/jobs)
- ✅ **Service Time Calculations**: Accurate duration computations

## Performance Considerations

- **Fast Startup**: Minimal dependencies for quick container deployment
- **Memory Efficient**: Optimized data structures for large problem instances
- **Scalable**: Stateless design allows horizontal scaling
- **Monitoring Ready**: Structured logging for production monitoring
- **Test Coverage**: Comprehensive test suite ensures reliability and performance

## Development Recommendations

### Immediate Improvements

1. **📊 Monitoring & Metrics**
   - Add Prometheus metrics for request duration, success rates
   - Implement health check endpoints with dependency validation
   - Add structured logging with correlation IDs

2. **🔒 Security Enhancements**
   - Implement API key authentication
   - Add rate limiting per client
   - Input sanitization and size limits
   - CORS configuration for web clients

3. **⚡ Performance Optimizations**
   - Response caching for identical problems
   - Async processing for large problems
   - Connection pooling and timeout configurations
   - Memory usage optimization for large matrices

4. **🛠️ Developer Experience**
   - Docker containerization with multi-stage builds
   - Environment-based configuration management
   - API versioning strategy
   - Automated API documentation generation

### Future Enhancements

1. **🌐 Advanced Features**
   - Real-time route tracking integration
   - Multiple optimization objectives (cost, time, fuel)
   - Dynamic re-routing based on traffic conditions
   - Vehicle type constraints (electric, capacity variations)

2. **📈 Scalability**
   - Microservices architecture for large deployments
   - Message queue integration for async processing
   - Database persistence for solution history
   - Multi-region deployment support

3. **🔍 Analytics & Insights**
   - Route optimization analytics dashboard
   - Historical performance tracking
   - Cost savings calculations
   - Carbon footprint optimization

4. **🧪 Advanced Testing**
   - Property-based testing with Hypothesis
   - Load testing with realistic traffic patterns
   - Chaos engineering for resilience testing
   - A/B testing framework for algorithm improvements

### Code Quality Improvements

1. **📝 Documentation**
   - Add inline code documentation
   - Create architecture decision records (ADRs)
   - API usage examples and tutorials
   - Performance benchmarking results

2. **🔧 Code Standards**
   - Pre-commit hooks with black, isort, flake8
   - Type hints coverage improvement
   - Error handling standardization
   - Logging strategy documentation

3. **🚀 CI/CD Pipeline**
   - Automated testing on multiple Python versions
   - Security vulnerability scanning
   - Performance regression testing
   - Automated deployment to staging/production