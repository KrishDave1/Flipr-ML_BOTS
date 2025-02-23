import requests

response = requests.post(
    f"https://api.stability.ai/v2beta/stable-image/generate/sd3",
    headers={
        "authorization": f"Bearer sk-WCa57OPKYiNKOLhLYNqYJl3k4Kn8xvygbEH2XXrtQEE7ESK1",
        "accept": "image/*"
    },
    files={"none": ''},
    data={
        "prompt": "Fugitive gangster Shariq Sata is on police radar for his suspected role in the violence",
        "output_format": "png",
    },
)

if response.status_code == 200:
    with open("./article1.png", 'wb') as file:
        file.write(response.content)
else:
    raise Exception(str(response.json()))