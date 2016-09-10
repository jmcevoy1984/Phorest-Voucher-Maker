class Voucher():
    
    def __init__(self, serial='', issueDate='', expiryDate='', originalBalance='', clientCardRef='', creatingBranchRef='', archived='false', remainingBalance='', ref=''):
        self.serial = serial
        self.issueDate = issueDate
        self.expiryDate = expiryDate
        self.originalBalance = originalBalance
        self.clientCardRef = clientCardRef
        self.creatingBranchRef = 'urn:x-memento:Branch:' + creatingBranchRef
        self.remainingBalance = remainingBalance
        self.archived = archived
        self.ref = ref

    def __str__(self):
        return str({ 'Voucher ' : { 'serial' : self.serial } })

class Client():
    
    def __init__(self, ref='', firstName='', lastName='', mobile='', email=''):
        self.ref = ref
        self.firstName = firstName
        self.lastName = lastName
        self.mobile = mobile
        self.email = email