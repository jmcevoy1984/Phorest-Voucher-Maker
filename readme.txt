#Flask app that communicates with the Phorest Voucher API and creates/reads vouchers.

Application is built with Flask.

Uses the Python Requests library to communicate with the Phorest voucher API
Uses Flask Restful to create a REST API

I convert from the Phorest API's native XML to JSON for use on the front end.

I use the Python Element Tree (etree) library to parse the XML.

Frontend programmed with plain Javascript making AJAX calls to the REST API.

Uses Bootstrap as the CSS framework by making use of two Flask Libraries:
Flask-Bootstrap
Flask-Nav
