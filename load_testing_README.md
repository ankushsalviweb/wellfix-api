# Load Testing with Locust

This directory contains load testing scripts for the Laptop Repair Service Platform using Locust.

## Setup

1. Install Locust:
   ```
   pip install locust
   ```

2. Adjust test parameters in `locustfile.py` as needed (endpoints, user credentials, etc.)

## Running Tests

To start the Locust web interface:

```
locust -f locustfile.py --host=http://localhost:5000
```

Replace `http://localhost:5000` with your application's base URL.

Then open your browser and go to:
```
http://localhost:8089
```

From the Locust web interface, you can:
- Set the number of users to simulate
- Set the spawn rate (users per second)
- Start the test and monitor results in real-time
- View statistics on response times, requests per second, and failures

## Available Test Scenarios

The locustfile includes the following user classes:

1. **ServiceManagementUser**: Simulates admin users accessing management endpoints
   - View all service requests
   - View individual service requests
   - View technicians
   - View customers

2. **CustomerUser**: Simulates customers using the platform
   - View personal service requests
   - Create new service requests

## Customizing Tests

To modify the test scenarios:
1. Edit the `locustfile.py` file
2. Adjust the `wait_time` to change delays between requests
3. Add or modify `@task` methods to test different endpoints
4. Adjust the task weight by changing the number in `@task(n)` 