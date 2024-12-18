"""Module providing a functions to get API siren Token and explore it."""

import requests


Api_Key = API_KEY
headers = {
    'Authorization': f"Bearer {Api_Key}",
    'Accept': 'application/json'
}

def get_content(url,header):
    try:
        response = requests.get(url,headers=header)
        if response.status_code == 200:
            content = response.json()
            return content
        else:
            print("error",response.status_code)
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None


    

