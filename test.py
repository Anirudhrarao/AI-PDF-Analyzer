import requests

url = "http://127.0.0.1:8000/api/pdf/upload/"
files = {"file": open("backend/media/pdfs/sample.pdf", "rb")}

response = requests.post(url, files=files)

print(response.status_code)
print(response.text)  # If response is JSON
