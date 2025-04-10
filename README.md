## Running Tests

This project uses pytest for testing. To run tests successfully, you'll need to make sure environment variables are set correctly. We've provided a helper script to fix common issues:

```bash
# Fix environment variables and run all tests
python fix_settings.py --run-tests

# Fix environment variables and run specific tests
python fix_settings.py --run-tests tests/api/v1/test_service_areas.py

# Only fix environment variables (no tests)
python fix_settings.py
```

### Test Coverage

To check the test coverage of the codebase, use the included coverage script:

```bash
# Run coverage on all tests
python run_coverage.py

# Run coverage on specific tests
python run_coverage.py tests/api/v1/test_service_areas.py
```

This will generate both console output and an HTML report in the `htmlcov` directory.

### Common Issues

- **Environment Variables with Comments**: Ensure environment variables in `.env` files don't have inline comments. 
  For example, use `ACCESS_TOKEN_EXPIRE_MINUTES=1440` instead of `ACCESS_TOKEN_EXPIRE_MINUTES=1440 # 1 day`.
  The `fix_settings.py` script can automatically fix these issues.

### Test Organization

The tests are organized as follows:

- `tests/api/`: Integration tests for API endpoints
- `tests/crud/`: Unit tests for CRUD operations
- `tests/models/`: Unit tests for database models
- `tests/core/`: Tests for core functionality like config and dependencies 