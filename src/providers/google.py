
    endpoint = "https://photoslibrary.googleapis.com/v1/mediaItems?pageSize=100"
    auth = f"Bearer {t}"
    # print(auth)
    myheaders = {
        'Authorization': auth,
        'Content-type': 'application/json'
    }
    body = { 'pageSize': '100' }

    r = requests.request(method='get', url=endpoint, headers=myheaders)

    print(r.text)
