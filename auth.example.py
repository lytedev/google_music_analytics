from gmusicapi import Mobileclient

default_email = "your@gmail.com"
default_password = "app specific password"
# See https://security.google.com/settings/security/apppasswords

def get_authed_api(username = "", password = ""):
    if username == "":
        username = default_email
    if password == "":
        password = default_password

    api = Mobileclient()
    if not api.login(username, password):
        return False
    return api

