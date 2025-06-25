import requests

url = "https://smartapi.angelbroking.com/scripmaster-csv.zip"
response = requests.get(url)

print("Status Code:", response.status_code)
print("Content-Type:", response.headers.get("Content-Type"))
