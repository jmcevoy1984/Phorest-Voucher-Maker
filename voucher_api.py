from shared import *
from helper_functions import *
from app import app
from flask_restful import Api, Resource, reqparse, fields, marshal_with, marshal

#Wraps the flask 'app' with the Api function from flask-RESTful. Assigns this to the 'api' variable.
api = Api(app)


#---------------MAIN API------------------

#Fields for marshaling output in JSON using the 'marshal_with' decorator/the 'marshal' function of flask-RESTful.
#Only the fields listed here will be output as the reponse in JSON format during the specified HTTP request.
voucher_post_fields = {
    'ref' : fields.String,
    'serial' : fields.String,
}

voucher_get_fields = {
    'ref' : fields.String,
    'serial' : fields.String,
    'expiryDate' : fields.String,
    'originalBalance' : fields.String,
    'clientCardRef' : fields.String,
    'archived' : fields.String,
    'remainingBalance' : fields.String,
    'issueDate' : fields.String
}

#Classes that subclass the "Resource" class from flask-RESTful.
#These are the resources for the API and contain all HTTP C.R.U.D methods.
class VoucherListAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('issueDate', type=str, default="{:%Y-%m-%d}".format(datetime.now()), location = 'json')
        self.reqparse.add_argument('expiryDate', type=str, default='{:%Y-%m-%d}'.format(datetime.now() + timedelta(days=365)), location='json')
        self.reqparse.add_argument('originalBalance', type=str, default='50', location='json')
        self.reqparse.add_argument('clientCardRef', type=str, default='', location='json')
        self.reqparse.add_argument('creatingBranchRef', type=str, default='urn:x-memento:Branch:'+branch_id, location='json')
        self.reqparse.add_argument('archived', type=str, default='false', location='json')
        self.reqparse.add_argument('start', type=str, default='0')
        self.reqparse.add_argument('max', type=str, default='50')
        #self.reqparse.add_argument('remainingBalance', type=str, default='', location='json')
        super(VoucherListAPI, self).__init__()

    @marshal_with(voucher_post_fields)
    def post(self):
        print('we go to post!')
        args = self.reqparse.parse_args()
        voucher = Voucher()
        setattr(voucher, 'serial', get_voucher_serial())
        for key, value in args.items():
            if hasattr(voucher, key):
                setattr(voucher, key, value)
        #setattr(voucher, 'remainingBalance', getattr(voucher, 'originalBalance'))
        #exl = ['remainingBalance', 'ref']
        xml_voucher = to_xml(voucher, 'voucher', 'remainingBalance')
        print(xml_voucher)
        headers = { 'content-type' : 'application/vnd.memento.Voucher+xml' }
        req = requests.post(voucher_uri, headers=headers, auth=(username, password), data=xml_voucher, verify=False)
        print(req.status_code)
        print(req.content)
        if req.status_code != 201:
            abort(req.status_code)
        else:
            root = ET.fromstring(req.content)
            setattr(voucher, 'ref', root.find('./identity').attrib['id']) #set the newly aquired id/uri for the voucher
            return voucher, 201

    def get(self):
        args = self.reqparse.parse_args()
        params = { 'start' : int(args['start']), 'max' : int(args['max']) }
        req = requests.get( voucher_uri, auth=(username, password), params=params, verify=False)
        #print(req.content)
        #print(req.headers)
        #print(req.status_code)
        voucher_list = []
        if req.status_code != 200:
            abort(req.status_code)
        else:
            root = ET.fromstring(req.content)
            #voucher = Voucher()
            #setattr(voucher, 'ref', ref)
            for child in root:
                if child.tag == 'voucher':
                    voucher = Voucher()
                    filled_voucher = xml_to_object(child, voucher)
                    voucher_list.append(marshal(filled_voucher, voucher_get_fields))
            return { 'voucher_list' : voucher_list }, 200 #to be fixed

class VoucherAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('issueDate', type=str, default="{:%Y-%m-%d}".format(datetime.now()), location = 'json')
        self.reqparse.add_argument('expiryDate', type=str, default='{:%Y-%m-%d}'.format(datetime.now() + timedelta(days=365)), location='json')
        self.reqparse.add_argument('originalBalance', type=str, default='50', location='json')
        self.reqparse.add_argument('clientCardRef', type=str, default='', location='json')
        self.reqparse.add_argument('creatingBranchRef', type=str, default='urn:x-memento:Branch:'+branch_id, location='json')
        self.reqparse.add_argument('archived', type=str, default='false', location='json')
        #self.reqparse.add_argument('remainingBalance', type=str, default='', location='json')
        super(VoucherAPI, self).__init__()
#api.add_resource(VoucherAPI, '/api/voucher', endpoint='vouchers')
    #get a voucher by it's unique reference (id)
    @marshal_with(voucher_get_fields)
    def get(self, ref):
        req = requests.get( voucher_uri +'/'+ ref, auth=(username, password), verify=False)
        print(req.content)
        print(req.headers)
        print(req.status_code)
        if req.status_code != 200:
            abort(req.status_code)
        else:
            root = ET.fromstring(req.content)
            voucher = Voucher()
            setattr(voucher, 'ref', ref)
            for child in root:
                if hasattr(voucher, child.tag):
                    setattr(voucher, child.tag, root.find('./'+child.tag).text)
            print(voucher.__dict__)
            return voucher, 200 #to be fixed

    def put(self, ref):
        original = get_voucher(ref)
        args = self.reqparse.parse_args()
        voucher = Voucher()
        for key, value in original.__dict__.items():
            if hasattr(voucher, key):
                setattr(voucher, key, value)
        for key, value in args.items():
            if hasattr(voucher, key):
                setattr(voucher, key, value)
        #setattr(voucher, 'originalBalance', '1000')
        xml_voucher = to_xml(voucher, 'voucher', 'serial')
        headers = {'content-type' : 'application/vnd.memento.Voucher+xml' }
        req = requests.put(post_uri + '/' + ref, headers=headers, auth=(username, password), data=xml_voucher, verify=False)
        print(req.status_code)
        print(req.content)
        if req.status_code != 200:
            abort(req.status_code)
        else:
            print(original.__dict__.items())
            print(voucher.__dict__.items())
            print(xml_voucher)
            print(args.items())
            return { 'result' : True }, 200



#def archive_voucher():
    #pass

'''def put(self, ref):
    original = get_voucher(ref)
    #print(original)
    voucher = Voucher()
    for child in original:
        if hasattr(voucher, child.tag):
            setattr(voucher, child.tag, original.find('./'+child.tag).text)
    for key, value in dict.items():
        if hasattr(voucher, key) and dict[key] != False:
            setattr(voucher, key, value)
    xml_voucher = to_xml(voucher, 'voucher')
    headers = {'content-type' : 'application/vnd.memento.Voucher+xml' }
    req = requests.put(voucher_uri + ref, headers=headers, auth=(username, password), data=xml_voucher, verify=False)
    return req.status_code'''

api.add_resource(VoucherListAPI, '/api/vouchers', endpoint='vouchers')
api.add_resource(VoucherAPI, '/api/vouchers/<ref>', endpoint='voucher')

#def update_voucher(ref):
    #req = requests.get('localhost:5000/api/vouchers/'+ref)
    #original = req.content
    #print(req)
    
#------------Clients---------------
client_get_fields = {
    
    'firstName' : fields.String,
    'lastName'  : fields.String,
    'mobile' : fields.String,
    'email' : fields.String,
    'ref' : fields.String,
    'vouchers' : fields.String
}


class ClientAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('firstName', type=str, default='', location = 'json')
        self.reqparse.add_argument('lastName', type=str, default='', location= 'json')
        self.reqparse.add_argument('mobile', type=str, location= 'json')
        super(ClientAPI, self).__init__()

    @marshal_with(client_get_fields)
    def get(self, ref):
        req = requests.get(client_uri + '/' + ref, auth=(username, password), verify=False)
        #print(req.status_code)
        #print(req.content)
        if req.status_code != 200:
            abort(req.status_code)
        else:
            root = ET.fromstring(req.content)
            client = Client()
            setattr(client, 'ref', ref)
            for child in root:
                if child.tag == 'link' and child.attrib['rel'] == 'vouchers':
                    setattr(client, 'vouchers', child.attrib['href'])
                if hasattr(client, child.tag):
                    setattr(client, child.tag, root.find('./'+child.tag).text)
            return client, 200 #to be fixed

api.add_resource(ClientAPI, '/api/client/<ref>', endpoint='client')

def create_client():
    xml = "<clientCard><firstName>Joe</firstName><lastName>Test</lastName><mobile>0833128991</mobile><archived>false</archived></clientCard>"
    headers = {'content-type' : 'application/vnd.memento.ClientCard+xml' }
    test_uri = 'https://lbh.eu-dev-0.memento-stacks.phorest.com/memento/rest/business/3Evn8Qqw6pVY4iScdZXWBA/client'
    req = requests.post(client_uri, headers=headers, auth=(username, password), data=xml, verify=False)
    print(req.status_code)
    print('Headers:', req.headers)
    print(req.content)

def update_client():
    xml = "<clientCard><firstName>Joe</firstName><lastName>Test</lastName><mobile>083317777</mobile></clientCard>"
    headers = {'content-type' : 'application/vnd.memento.ClientCard+xml' }
    test_uri = 'https://lbh.eu-dev-0.memento-stacks.phorest.com/memento/rest/business/3Evn8Qqw6pVY4iScdZXWBA/client/9mkguGy0b6xpUgaBF65CIA'
    req = requests.put(client_uri + '/' + 'XAzAN9Hwffcqp0cx_v7qJg', headers=headers, auth=(username, password), data=xml, verify=False)
    print(req.status_code)
    print('Headers:', req.headers)
    with open('client_update.xml', 'w') as f:
            f.write(str(req.content))
            f.close()

def get_client(ref):
    req = requests.get(client_uri + '/' + ref, auth=(username, password), verify=False)
    print(req.status_code)
    print(req.content)
    if req.status_code != 200:
        abort(req.status_code)
    else:
        root = ET.fromstring(req.content)
        client = Client()
        setattr(client, 'ref', ref)
        for child in root:
            if hasattr(client, child.tag):
                setattr(client, child.tag, root.find('./'+child.tag).text)
        return client, 200 #to be fixed

'''def get_client_vouchers(client_vouchers_uri):
    test_uri = 'https://lbh1.eu.phorest.com/memento/rest/business/3Evn8Qqw6pVY4iScdZXWBA/client/sH40eB0ICVBgK5KFMrokfA/voucher'
    req = requests.get(test_uri, auth=(username, password), verify=False)
    print(req.status_code)
    with open('client_vouchers.xml', 'w') as f:
            f.write(str(req.content))
            f.close'''

def get_clients():
    #test_uri = "https://lbh.eu-dev-0.memento-stacks.phorest.com/memento/rest/business/3Evn8Qqw6pVY4iScdZXWBA/voucher"
    req = requests.get(client_uri + '/' + 'Xbus3AT3eqOEJXsfXr6L_w', auth=(username, password), verify=False)
    print(req.status_code)
    print(req.content)
    if req.status_code != 200:
        abort(req.status_code)
    else:
        root = ET.fromstring(req.content)
        '''print(len(root))
        count = 0
        for child in root:
            if child.tag == 'voucher':
                count += 1
        print (count)
            #print(child.tag)'''
    '''else:
        with open('client_list.xml', 'w') as f:
            f.write(str(req.content))
            f.close'''

def vouch_trans():
    trans_uri = "https://lbh.eu-dev-0.memento-stacks.phorest.com/memento/rest/business/3Evn8Qqw6pVY4iScdZXWBA/voucher/8tpbJWlBGIB5Z4CC00npvw/transactions"
    xml = '<voucherTransaction><date>2016-02-17</date><transactionAmount>-100.00</transactionAmount><voucherRef>urn:x-memento:Voucher:8tpbJWlBGIB5Z4CC00npvw</voucherRef><branchRef>urn:x-memento:Branch:nPpLa0UY4UO5dn68TpPsiA</branchRef><creatingUserRef>urn:x-memento:User:ISLX8fGtdKIB8CMLSIlc7g</creatingUserRef><voucherUpdateType>MANUALLY_ADDED</voucherUpdateType><relatedTransactionDeleted>false</relatedTransactionDeleted><compensatingTransaction>false</compensatingTransaction></voucherTransaction>'
    headers = {'content-type' : 'application/vnd.memento.VoucherTransaction+xm' }
    req = requests.post(trans_uri, headers=headers, auth=(username, password), data=xml, verify=False)
    print(req.status_code)
    print(req.content)