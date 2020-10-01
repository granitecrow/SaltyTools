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

    request = session.post(config.LOGIN_URL, data=login_data)

    if ( request.url != config.MAINS_URL and request.url != config.MAIN_URL ):
        raise RuntimeError("Error: Wrong URL: " + request.url)

    return session, request