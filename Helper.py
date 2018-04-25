def getUrl(user, password, dbname, host='127.0.0.1', port=5432):
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, dbname)
    return url
