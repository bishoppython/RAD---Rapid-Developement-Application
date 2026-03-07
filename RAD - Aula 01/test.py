import requests
import json

response = requests.post("http://localhost:5000/calcular",
    json={
        "num1": 10,
        "num2": 3,
        "operacao": "soma"
    })
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
# print(response.json())