from locust.contrib.fasthttp import FastHttpUser
from locust import between, task


class ApiUser(FastHttpUser):
    wait_time = between(1, 3)

    @task()
    def predict_lambda(self):
        payload = {
            "length": -0.158164,
            "diameter": -0.280982,
            "height": -0.227545,
            "whole_weight": -0.352298,
            "shucked_weight": -0.596421,
            "viscera_weight": -0.019102,
            "shell_weight": -0.135293,
            "sex_M": 0.0,
            "sex_F": 0.0,
            "sex_I": 1.0
        }
        self.client.post("/", json=payload)
