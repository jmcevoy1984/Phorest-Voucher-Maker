import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from models import *
from app import app
from flask import abort, url_for, jsonify

#Variables denoting valid URI and log in details for Phorest demo environment.
#These could potentially be changed to match the details of a real salon.
username = 'user/test@phorest.com'
password = 'Testtest1'
business_id = '3Evn8Qqw6pVY4iScdZXWBA'
branch_id = 'nPpLa0UY4UO5dn68TpPsiA'
environment = 'eu-dev-api'


get_serial_uri = "https://"+environment+".phorest.com/memento/rest/business/"+business_id+"/voucher/branch/"+branch_id+"/voucherserialnumber"
post_uri = "https://"+environment+".phorest.com/memento/rest/business/"+business_id+"/voucher"

client_uri = "https://"+environment+".phorest.com/memento/rest/business/"+business_id+"/client"

voucher_uri = post_uri