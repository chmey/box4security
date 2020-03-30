import os
SQL_VERBOSE = False


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/project/static"

    # Mail
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")


class Dashboard():
    url = None
    name = None
    parent_id = None

    def __init__(self, url="", name="", parent_id=""):
        self.url = url
        self.name = name
        self.parent_id = parent_id


Dashboards = [
    Dashboard(name='start', url='/kibana/app/kibana#/dashboard/8d13ea50-3de1-11ea-bbd4-bb7e0278945f?_g=()&_a=(fullScreenMode:!t)', parent_id='#start'),
    Dashboard(name='ids', url='/kibana/app/kibana#/dashboard/a7bfd050-ce1d-11e9-943f-fdbfa2556276?_g=()&_a=(fullScreenMode:!t)', parent_id='#siem'),
    Dashboard(name='vuln-overview', url='/kibana/app/kibana#/dashboard/f8712020-cefa-11e9-943f-fdbfa2556276?_g=()&_a=(fullScreenMode:!t)', parent_id='#vuln'),
    Dashboard(name='vuln-details', url='/kibana/app/kibana#/dashboard/bcb41f20-f18b-11e9-a167-6152d43fae94?_g=()&_a=(fullScreenMode:!t)', parent_id='#vuln'),
    Dashboard(name='vuln-progress', url='/kibana/app/kibana#/dashboard/87c24930-ceff-11e9-943f-fdbfa2556276?_g=()&_a=(fullScreenMode:!t)', parent_id='#vuln'),
    Dashboard(name='network-overview', url='/kibana/app/kibana#/dashboard/dc847fd0-3dd9-11ea-bbd4-bb7e0278945f?_g=()&_a=(fullScreenMode:!t)', parent_id='#net'),
    Dashboard(name='network-streams', url='/kibana/app/kibana#/dashboard/e5fbd440-ce2c-11e9-943f-fdbfa2556276?_g=()&_a=(fullScreenMode:!t)', parent_id='#net'),
    Dashboard(name='network-asn', url='/kibana/app/kibana#/dashboard/c2b4c450-ce46-11e9-943f-fdbfa2556276?_g=()&_a=(fullScreenMode:!t)', parent_id='#net')
]
