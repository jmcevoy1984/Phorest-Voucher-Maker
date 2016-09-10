from app import app
from flask import render_template, jsonify, request
from voucher_api import *


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/voucher_list')
def voucher_list():
    return render_template('voucher_list.html')

@app.route('/clients/<ref>')
def client_vouchers(ref):
	return render_template('client_record.html', ref=ref)

@app.route('/client/vouchers')
def client_voucher_list():
	#print(dir(request))
	ref = request.args.get('link')
	return jsonify({ 'vouchers' : get_client_vouchers(ref) }), 200
#@marshal_with(voucher_get_fields)
@app.route('/search')
def search():
	result = get_voucher_list(0, 1)
	total = int(result.attrib['totalResults'])
	return jsonify({ 'Vouchers' : convert_vouchers(get_voucher_list(0, total)) }), 200
    #voucher = find_voucher(field)
    #if voucher:
        #return jsonify(serialize(find_voucher(field))), 200
    #else:
        #abort(404)