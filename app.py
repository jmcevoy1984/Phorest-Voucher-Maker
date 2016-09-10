from flask import Flask
from flask_bootstrap import Bootstrap
from navbar import nav

app = Flask(__name__)
app.debug = True
Bootstrap(app)
nav.init_app(app)

import voucher_api
import views