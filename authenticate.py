import requests
import config

def login(email, password):
    session = requests.session()

    # This is the form data that the page sends when logging in
    login_data = {
        'email': email,
        'pword': password,
        'authenticate': 'signin'
    }
    # adding headers to avoid 403 Forbidden status
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'referer' : 'https://www.saltybet.com/authenticate?signin=1'
    }

    #submit login request
    request = session.post(config.LOGIN_URL, data=login_data, headers=headers)

    if ( request.url != config.MAINS_URL and request.url != config.MAIN_URL ):
        raise RuntimeError("Error: Wrong URL: " + request.url)

    return session, request