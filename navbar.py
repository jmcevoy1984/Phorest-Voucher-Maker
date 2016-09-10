from flask_nav import Nav
from flask_nav.elements import Navbar, View



nav = Nav()
nav.register_element('top', 
	Navbar(
		View('Voucher Maker', 'index'), 
		View('Voucher List', 'voucher_list')
		#View('Client Vouchers', 'client_vouchers')
		)
	)

