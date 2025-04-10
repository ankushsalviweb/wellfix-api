from locust import HttpUser, task, between

class ServiceManagementUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login to get authentication token
        self.client.post("/api/auth/login", json={
            "username": "admin@wellfix.com",
            "password": "admin123"
        })
    
    @task(2)
    def view_service_requests(self):
        self.client.get("/api/service-requests")
    
    @task(1)
    def view_single_service_request(self):
        # Assuming IDs 1-5 exist in the system
        service_id = self.get_random_id(1, 5)
        self.client.get(f"/api/service-requests/{service_id}")
    
    @task(1)
    def view_technicians(self):
        self.client.get("/api/technicians")
    
    @task(1)
    def view_customers(self):
        self.client.get("/api/customers")
    
    def get_random_id(self, min_id, max_id):
        import random
        return random.randint(min_id, max_id)


class CustomerUser(HttpUser):
    wait_time = between(2, 5)
    
    def on_start(self):
        # Login as a customer
        self.client.post("/api/auth/login", json={
            "username": "customer@example.com",
            "password": "customer123"
        })
    
    @task(3)
    def view_own_service_requests(self):
        self.client.get("/api/customers/me/service-requests")
    
    @task(1)
    def create_service_request(self):
        self.client.post("/api/service-requests", json={
            "device_type": "Laptop",
            "brand": "TestBrand",
            "model": "TestModel",
            "issue_description": "Performance test - please ignore",
            "priority": "Medium"
        }) 