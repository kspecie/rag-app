# Testing Guide for RAG Application

This document provides guidance on how to run tests and add new tests to the RAG application.

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

## Best Practices

### General Testing Principles

1. **Arrange-Act-Assert**: Structure tests with setup, execution, and verification
2. **Test Isolation**: Each test should be independent and not affect others
3. **Meaningful Names**: Use descriptive test names that explain what is being tested
4. **Test One Thing**: Each test should verify one specific behavior

### Backend Testing

1. **Use Fixtures**: Define test data and mocks in `conftest.py`
2. **Mock External Services**: Don't make real API calls or database connections in tests
3. **Test Edge Cases**: Include tests for error conditions and boundary cases
4. **Use Parametrized Tests**: Test multiple scenarios with `@pytest.mark.parametrize`

### Frontend Testing

1. **Test User Behavior**: Focus on what users see and do, not implementation details
2. **Use Data Attributes**: Add `data-testid` attributes to elements you want to test
3. **Mock API Calls**: Use MSW (Mock Service Worker) or similar for API mocking
4. **Test Accessibility**: Ensure components are accessible to screen readers

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=app

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run tests
        run: |
          cd frontend
          npm run test:run
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure test files can import from the main application
2. **Database Connections**: Mock database calls or use test database
3. **Environment Variables**: Set test environment variables in `conftest.py`
4. **Async Tests**: Use `@pytest.mark.asyncio` for async test functions

### Getting Help

- Check pytest documentation: https://docs.pytest.org/
- Check Testing Library documentation: https://testing-library.com/
- Check Vitest documentation: https://vitest.dev/ 