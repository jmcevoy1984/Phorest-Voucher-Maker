from shared import *

#-------------helper functions-------------

#Fetch a unique voucher serial number and parse the XML to output as a string.
#This is done using the xml.etree (Element Tree) module. This is a standard Python module for parsing XML.
def get_voucher_serial():
    req = requests.get(get_serial_uri , auth=(username, password), verify=False)
    print(req.status_code)
    print(req.content)
    if req.status_code != 200:
        abort(req.status_code)
    else:
        root = ET.fromstring(req.content)
        voucher_number = root[0].text
    return voucher_number
    
#Takes an object and a string that represents the type of object eg 'voucher', 'clientCard' and outputs with xml tags.
#This function converts the attributes of an object passed to it into XML tags which surround the attribute value.
def to_xml(object, string, *exclude):
    attrib = object.__dict__
    output_xml = '<'+string+'>'
    for key, val in attrib.items():
        if not (key in exclude):
            open_tag = '<'+str(key)+'>'
            close_tag = '</'+str(key)+'>'
            output_xml += open_tag + str(val) + close_tag
    output_xml += '</'+string+'>'
    return output_xml

def get_voucher(ref):
    req = requests.get( post_uri +'/'+ ref, auth=(username, password), verify=False)
    if req.status_code != 200:
        abort(req.status_code)
    else:
        root = ET.fromstring(req.content)
        voucher = Voucher()
        setattr(voucher, 'ref', ref)
        for child in root:
            if hasattr(voucher, child.tag):
                setattr(voucher, child.tag, root.find('./'+child.tag).text)
        return voucher

def serialize(object):
    attributes = object.__dict__
    return {key:value for key, value in attributes.items() if key != 'creatingBranchRef'}

def get_voucher_list(start, max_results):
    params = {'start' : start, 'max' : max_results}
    req = requests.get( voucher_uri, auth=(username, password), params=params, verify=False)
    if req.status_code != 200:
        abort(req.status_code)
    else:
        root = ET.fromstring(req.content)
        #print(root.attrib['totalResults'])
        #print(root)
        return root

def find_voucher(serial):
    start, max_results = 0 , 50
    found = ''
    count = 0
    while not found and count < max_results:
        vouchers = get_voucher_list(start, max_results)
        max_results = int(vouchers.attrib['totalResults'])
        for child in vouchers:
            count += 1
            for subchild in child.iter('serial'):
                if subchild.text == serial:
                    found = True
                    #print('FOUND!')
                    voucher = Voucher()
                    voucher = xml_to_object(child, voucher)
                    #print(voucher)
                    return voucher
                    break
            if found:
                break
    return False

def xml_to_object(xml, object):
    for child in xml:
        if hasattr(object, child.tag):
            setattr(object, child.tag, xml.find('./'+child.tag).text)
        if child.tag == 'identity':
            ref_str = child.attrib['id'][::-1].split(':')
            #ref_str = ref_str.split(':')
            ref_str = ref_str[0][::-1]
            #ref_str = ref_str[::-1]
            #print(ref_str)
            #print(child.attrib['id'][ref_str:])
            setattr(object, 'ref', ref_str) #add unique ref
        if child.tag == 'clientCardRef':
            ref_str = child.text[::-1]
            ref_str = ref_str.split(':')
            ref_str = ref_str[0]
            ref_str = ref_str[::-1]
            setattr(object, 'clientCardRef', ref_str)
            #print('child: ' + ref_str)
    return object

def convert_vouchers(xml):
    '''voucher_list = []
    for child in xml:
        if child.tag == 'voucher':
            voucher_list.append(serialize(xml_to_object(child, Voucher())))
    return voucher_list'''
    return [serialize(xml_to_object(child, Voucher())) for child in xml if child.tag == 'voucher']

def get_client_vouchers(client_vouchers_uri):
    req = requests.get(client_vouchers_uri, auth=(username, password), verify=False)
    print(req.status_code)
    root = ET.fromstring(req.content)
    return convert_vouchers(root)
