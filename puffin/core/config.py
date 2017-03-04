import subprocess, re, os
from ..util.homer import HOME
from .. import app


class DefaultConfig:

    # Interface and port where to serve Puffin
    HOST = "0.0.0.0"
    PORT = 8080

    # Number of threads serving the requests (keep in mind in CPython there's [GIL]()).
    THREADS = 1

    # Debugging settings, they might be useful during development (see [Flask]())
    DEBUG = False
    TESTING = False

    # External address of the server, used when generating installed application domains
    # For localhost use:
    SERVER_NAME = None
    # For remote host use:
    # SERVER_NAME = "example.com"

    # Secret key used to encrypt session cookies and passwords
    SECRET_KEY = b"puffin"
    
    # Postgres database connection settings
    DB_HOST = "puffindb"
    DB_PORT = "5432"
    DB_NAME = "puffin"
    DB_USER = "postgres"
    DB_PASSWORD = ""

    # SMTP connection settings used to send emails
    MAIL_SERVER = "mailhog"
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = "puffin <puffin@localhost>"
    MAIL_SUPPRESS_SEND = False

    # Account registration
    SECURITY_REGISTERABLE = True

    # Docker machine settings. 
    # For local docker instance use the following settings:
    MACHINE_URL = "unix://var/run/docker.sock"
    MACHINE_PATH = None
    # For docker running on a remote machine use the following settings:
    # IP address and port number of the machine
    # MACHINE_URL=https://123.45.67.89:2376
    # Path to a directory containing cert.pem, key.pem and ca.pem files, 
    # generated by docker-machine.
    # MACHINE_PATH=/etc/puffin/machine/

    # HTTPS / Let's Encrypt
    LETSENCRYPT = False
    LETSENCRYPT_TEST = True

    # URL and site ID for [Piwik](https://piwik.org). 
    ANALYTICS_PIWIK_BASE_URL = None
    ANALYTICS_PIWIK_SITE_ID = None

    # Extra notifications for administrator
    NEW_USER_NOTIFICATION = False

    # Extra links that will appear in the main menu
    LINK_1 = None
    LINK_2 = None
    LINK_3 = None

def init():
    app.config.from_object("puffin.core.config.DefaultConfig")
    
    app.config.update(get_env_vars())
    
    app.config['VERSION'] = get_version()
    app.config['SERVER_NAME_FULL'] = get_server_name_full()
    app.config['LINKS'] = get_links()

    validate()


def get_version():
    version = (None, None)
    try:
        description = subprocess.check_output(
            ["git", "describe", "--long",  "--match", "[0-9].*"], 
            stderr=subprocess.STDOUT, cwd=HOME, universal_newlines=True)
        m = re.match(r"([\w\.]+)-\d+-g(\w+)", description)
        if m:
            version = (m.group(1), m.group(2))
    except subprocess.CalledProcessError:
        pass 
    return version

def get_env_vars():
    env_vars = {}
    for name in (n for n in dir(DefaultConfig) if not n.startswith("_")):
        value = os.environ.get(name)
        if value != None:
            default_value = getattr(DefaultConfig, name)
            env_vars[name] = cast_str(value, type(default_value))
    return env_vars

def cast_str(value, typ):
    if typ is bool:
        return value.lower() in ("true", "1", "yes")
    if typ is int:
        return int(value)
    else:
        return value

def validate():
    if app.config["SECRET_KEY"] == DefaultConfig.SECRET_KEY:
        app.logger.warning("No SECRET_KEY provided, using the default one.")

def get_server_name_full():
    return app.config["SERVER_NAME"] or "localhost"

def get_links():
    links = []
    for key in ("LINK_1", "LINK_2", "LINK_3"):
        value = app.config.get(key)
        if value:
            links.append(value.split())
    return links
