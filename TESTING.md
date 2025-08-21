# Testing Guide for RAG Application

This document provides guidance on how to run tests and add new tests to the application.

## Project Structure

```
rag-app/
├── tests/                    # Backend tests (Python)
│   ├── conftest.py          # pytest configuration and fixtures
│   ├── test_api/            # API endpoint tests
│   ├── test_core/           # Core business logic tests
│   └── test_utils/          # Utility function tests
├── frontend/
│   ├── src/
│   └── tests/               # Frontend tests (TypeScript)
│       ├── setup.ts         # Test setup and mocks
│       └── components/      # Component tests
├── pytest.ini              # pytest configuration
└── requirements.txt         # Python dependencies including testing
```

## Backend Testing (Python)

### Setup

1. Install testing dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api/test_main.py

# Run tests matching pattern
pytest -k "test_api"

# Run tests with verbose output
pytest -v
```

### Test Categories

- **Unit Tests**: Test individual functions and classes in isolation
- **Integration Tests**: Test how components work together
- **API Tests**: Test FastAPI endpoints using TestClient

### Writing Backend Tests

1. **Test File Naming**: `test_*.py`
2. **Test Function Naming**: `test_*`
3. **Use Fixtures**: Define reusable test data in `conftest.py`
4. **Mock External Dependencies**: Use `unittest.mock` for database calls, API calls, etc.

Example:
```python
def test_generate_summary_with_valid_api_key(test_client: TestClient, api_headers):
    """Test summary generation with valid API key."""
    response = test_client.post(
        "/summaries/generate/", 
        json={"text": "Test medical conversation"}, 
        headers=api_headers
    )
    assert response.status_code == 200
```

## Frontend Testing (TypeScript/React)

### Setup

1. Install testing dependencies:
```bash
cd frontend
npm install
```

2. Run tests:
```bash
# Run tests in watch mode
npm test

# Run tests once
npm run test:run

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

### Test Categories

- **Component Tests**: Test React components in isolation
- **Hook Tests**: Test custom React hooks
- **Utility Tests**: Test utility functions
- **Integration Tests**: Test component interactions

### Writing Frontend Tests

1. **Test File Naming**: `*.test.tsx` or `*.test.ts`
2. **Use Testing Library**: Focus on testing behavior, not implementation
3. **Mock External Dependencies**: Mock API calls, browser APIs, etc.

Example:
```typescript
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import MyComponent from './MyComponent'

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })
})
```

## Test Coverage

### Backend Coverage
- Run `pytest --cov=app --cov-report=html` to generate HTML coverage report
- Coverage report will be available in `htmlcov/` directory

### Frontend Coverage
- Run `npm run test:coverage` to generate coverage report
- Coverage report will be displayed in terminal and available in `coverage/` directory



### Getting Help

- Check pytest documentation: https://docs.pytest.org/
- Check Testing Library documentation: https://testing-library.com/
- Check Vitest documentation: https://vitest.dev/ 



## Integration Tests

- Pytest markers to distinguish integration tests: `@pytest.mark.integration`.
- These tests may touch live services (e.g., ChromaDB) running from docker-compose.
- Tests will self-skip if services are unreachable.

### Run Integration Tests Only
```bash
# inside container
pytest -m integration -v
```

### Run All Except Integration
```bash
pytest -m "not integration" -v
```

### Example Integration Tests
- `tests/integration/test_chroma_store_list.py`: direct Chroma client lifecycle
- `tests/integration/test_api_flow.py`: FastAPI routes with live backing services 

### End-to-End Integration (optional)
- Gated by env flag `E2E_FULL=1`. Defaults to skipped.
- Fast mock mode enabled by `E2E_MOCK_MODE=1` (default). Set `0` to hit real TEI/TGI if available.

Run:
```bash
# inside container
E2E_FULL=1 E2E_MOCK_MODE=1 pytest -m integration tests/integration/test_e2e_flow.py -v
``` 