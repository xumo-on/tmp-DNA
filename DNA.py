"""
DNA
"""
from ontology.interop.Ontology.Contract import Migrate
from ontology.interop.System.Storage import GetContext, Get, Put, Delete
from ontology.interop.System.Runtime import CheckWitness, Notify, Serialize, Deserialize
from ontology.interop.Ontology.Runtime import Base58ToAddress
from ontology.builtins import concat, Exception, len, append, remove


Owner = Base58ToAddress('ASwaf8mj2E3X18MHvcJtXoDsMqUjJswRWS')
context = GetContext()


PLAYER_ADDRESS_PRE_KEY = "P1"
ADMIN_ADDRESS_KEY = "P2"
DNA_PRE_KEY = "P3"
INIIT_KEY = "P4"


def Main(operation, args):
    ########## for Owner to invoke Begin ##########
    if operation == "init":
        return init()
    if operation == "addAdmin":
        Require(len(args) == 1)
        Account = args[0]
        return addAdmin(Account)
    if operation == "removeAdmin":
        Require(len(args) == 1)
        Account = args[0]
        return removeAdmin(Account)
    if operation == "migrateContract":
        Require(len(args) == 7)
        code = args[0]
        needStorage = args[1]
        name = args[2]
        version = args[3]
        author = args[4]
        email = args[5]
        description = args[6]
        return migrateContract(code, needStorage, name, version, author, email, description)
    ########## for Owner to invoke End ##########

    ########## for Owner and Admin to invoke Begin ##########
    if operation == "createProperty":
        Require(len(args) == 2)
        Account = args[0]
        createList = args[1]
        return createProperty(Account, createList)
    ########## for Owner and Admin to invoke End ##########

    ########## for Everyone to invoke Begin ##########
    if operation == "transferProperty":
        Require(len(args) == 1)
        transferList = args[0]
        return transferProperty(transferList)
    if operation == "removeProperty":
        Require(len(args) == 1)
        removeList = args[0]
        return removeProperty(removeList)
    if operation == "getPlayerAllDNA":
        Require(len(args) == 1)
        Account = args[0]
        return getPlayerAllDNA(Account)
    if operation == "getPlayerDNAFromRange":
        Require(len(args) == 3)
        Account = args[0]
        fromNum = args[1]
        toNum = args[2]
        return getPlayerDNAFromRange(Account, fromNum, toNum)
    if operation == "getPlayerDNANum":
        Require(len(args) == 1)
        Account = args[0]
        return getPlayerDNANum(Account)
    ########## for Everyone to invoke End ##########


########## Methods that only Owner can invoke Start ##########
def init():
    """
    only owner can init
    please init before use any function
    :return: bool
    """
    RequireWitness(Owner)
    inited = Get(GetContext(), INIIT_KEY)
    if inited:
        Notify(["Already inited"])
        return False
    else:
        Put(context, concatKey(ADMIN_ADDRESS_KEY, Owner), 1)
        Put(context, INIIT_KEY, 1)
        Notify(["Init successfully"])
    return True


def addAdmin(Account):
    """
    only owner can add admin
    :param Account: new admin's address
    :return: bool
    """
    RequireWitness(Owner)
    Require(Get(context, concatKey(ADMIN_ADDRESS_KEY, Account)) == 0)
    Put(context, concatKey(ADMIN_ADDRESS_KEY, Account), 1)
    Notify(["Add admin", Account])
    return True


def removeAdmin(Account):
    """
    only owner can remove admin
    cannot remove owner
    :param Account: admin's account
    :return: bool
    """
    RequireWitness(Owner)
    Require(Account != Owner)
    Require(Get(context, concatKey(ADMIN_ADDRESS_KEY, Account)) == 1)
    Delete(context, concatKey(ADMIN_ADDRESS_KEY, Account))
    Notify(["Remove admin", Account])
    return True


def migrateContract(code, needStorage, name, version, author, email, description):
    """
    only Owner can migrate contract
    can migrate this contract to a new contract
    the code is new contract's AVM code
    old contract's all data will transfer to new contract
    :param code: new contract code
    :param needStorage: True
    :param name: ""
    :param version: ""
    :param author: ""
    :param email: ""
    :param description: ""
    :return: bool
    """
    RequireWitness(Owner)
    res = Migrate(code, needStorage, name, version, author, email, description)
    Require(res)
    Notify(["Migrate Contract successfully"])
    return True
########## Methods that only Owner can invoke End ##########


########## Methods that only Owner and Admin can invoke Start ##########
def createProperty(Account, createList):
    """
    only contract owner or admin can create property
    cannot create more than 1000 property once
    :param createList: [Account, [[account1, DNA1],[account2, DNA2]]]
    :return: bool
    """
    Require(Get(context, concatKey(ADMIN_ADDRESS_KEY, Account)) == 1)
    RequireWitness(Account)
    DNAlist = Get(context, concatKey(PLAYER_ADDRESS_PRE_KEY, createList[0][0]))
    if not DNAlist:
        DNAlist = []
    else:
        DNAlist = Deserialize(DNAlist)
    Require(len(createList) <= 1000)
    for createE in createList:
        account = createE[0]
        DNA = createE[1]
        accountCheck = Get(context, concatKey(DNA_PRE_KEY, DNA))

        Require(len(account) == 20)
        # check len
        Require(DNA >= 100000000000000)
        Require(DNA < 10000000000000000)
        # check kind
        Require(DNA / 100000000000000 % 100 > 0)
        Require(DNA / 100000000000000 % 100 < 100)
        # check grade
        Require(DNA / 1000000000000 % 100 > 0)
        Require(DNA / 1000000000000 % 100 < 100)
        # check name
        Require(DNA / 1000000000 % 1000 > 0)
        Require(DNA / 1000000000 % 1000 < 1000)
        # check number
        Require(DNA / 1000 % 1000000 > 0)
        Require(DNA / 1000 % 1000000 < 1000000)
        # check random
        Require(DNA / 1 % 1000 >= 0)
        Require(DNA / 1 % 1000 < 1000)
        # check DNA
        Require(not accountCheck)

        DNAlist.append(DNA)
        Put(context, concatKey(DNA_PRE_KEY, DNA), account)
        Put(context, concatKey(PLAYER_ADDRESS_PRE_KEY, account), Serialize(DNAlist))
    Notify(["Create property successfully."])
    return True
########## Methods that only Owner and Admin can invoke End ##########


########## Methods that Evetyone can invoke Start ##########
def transferProperty(transferList):
    """
    one account can transfer many DNA to different other accounts
    :param transferList: [[toAccount1, DNA1],[toAccount2, DNA2]]
    :return: bool
    """
    DNACheck = transferList[0][1]
    account = Get(context, concatKey(DNA_PRE_KEY, DNACheck))
    RequireScriptHash(account)
    RequireWitness(account)
    DNAlist = Get(context, concatKey(PLAYER_ADDRESS_PRE_KEY, account))
    DNAlist = Deserialize(DNAlist)

    transferListLen = len(transferList)
    transferListIndex = 0
    while transferListIndex < transferListLen:
        toAccount = transferList[transferListIndex][0]
        DNA = transferList[transferListIndex][1]

        toDNAlist = Get(context, concatKey(PLAYER_ADDRESS_PRE_KEY, toAccount))
        if not toDNAlist:
            toDNAlist = []
        else:
            toDNAlist = Deserialize(toDNAlist)

        findInList = _findInList(DNA, DNAlist)
        if findInList >= 0:
            Put(context, concatKey(DNA_PRE_KEY, DNA), toAccount)
            toDNAlist.append(DNA)
            DNAlist.remove(findInList)
        else:
            raise Exception("Not found DNA to be removed")
        transferListIndex += 1
    Put(context, concatKey(PLAYER_ADDRESS_PRE_KEY, account), Serialize(DNAlist))
    Put(context, concatKey(PLAYER_ADDRESS_PRE_KEY, toAccount), Serialize(toDNAlist))
    Notify(["Transfer property successfully"])
    return True


def removeProperty(removeList):
    """
    :param removeList: [DNA1, DNA2]
    :return: bool
    """
    DNACheck = removeList[0]
    account = Get(context, concatKey(DNA_PRE_KEY, DNACheck))
    RequireScriptHash(account)
    RequireWitness(account)

    DNAlist = Get(context, concatKey(PLAYER_ADDRESS_PRE_KEY, account))

    if DNAlist:
        DNAlist = Deserialize(DNAlist)
    else:
        raise Exception("NO DNA")
    removeListLen = len(removeList)
    removeListIndex = 0

    while removeListIndex < removeListLen:
        DNA = removeList[removeListIndex]
        findInList = _findInList(DNA, DNAlist)
        if findInList >= 0:
            Delete(context, concatKey(DNA_PRE_KEY, DNA))
            DNAlist.remove(findInList)
        else:
            raise Exception("Not found DNA to be removed")
        removeListIndex += 1
    Put(context, concatKey(PLAYER_ADDRESS_PRE_KEY, account), Serialize(DNAlist))
    Notify(["Remove property successfully"])
    return True


def _findInList(DNA, DNAlist):
    DNAListIndex = 0
    DNAListLen = len(DNAlist)
    while DNAListIndex < DNAListLen:
        if DNA == DNAlist[DNAListIndex]:
            return DNAListIndex
        DNAListIndex += 1
    return -1


def getPlayerAllDNA(Account):
    """
    get player's all DNA
    if this function cannot use because player's DNA too much
    can use getPlayerDNANum and getPlayerDNAFromRange to get DNA
    :param Account: player's account
    :return: [DNA1, DNA2, DNA3]
    """
    DNAlist = Get(context, concatKey(PLAYER_ADDRESS_PRE_KEY, Account))
    DNAlist = Deserialize(DNAlist)
    return DNAlist


def getPlayerDNAFromRange(Account, fromNum, toNum):
    """
    get player's DNA list from fromNum to toNum
    toNum - fromNum must < 1000
    can only get 1000 at most once
    paramExample: [Account, fromNum, toNum]
    :param Account: player's account
    :param fromNum: int
    :param toNum: int
    :return: [DNA1, DNA2, DNA3]
    """
    Require(Sub(toNum, fromNum) < 1000)
    DNAlist = Get(context, concatKey(PLAYER_ADDRESS_PRE_KEY, Account))
    DNAlist = Deserialize(DNAlist)
    Require(Sub(toNum, fromNum) < len(DNAlist))

    tmpList = []
    while fromNum <= toNum:
        tmpList.append(DNAlist[Sub(fromNum, 1)])
        fromNum += 1
    return tmpList


def getPlayerDNANum(Account):
    """
    get one account's DNA number
    :param Account: player's account
    :return: int
    """
    DNAlist = Get(context, concatKey(PLAYER_ADDRESS_PRE_KEY, Account))
    DNAlist = Deserialize(DNAlist)
    return len(DNAlist)


########## Methods that Evetyone can invoke End ##########


######################### Utility Methods Start #########################
def concatKey(str1, str2):
    """
    connect str1 and str2 together as a key
    :param str1: string1
    :param str2:  string2
    :return: string1_string2
    """
    return concat(concat(str1, '_'), str2)

"""
https://github.com/ONT-Avocados/python-template/blob/master/libs/Utils.py
"""
def Revert():
    """
    Revert the transaction. The opcodes of this function is `09f7f6f5f4f3f2f1f000f0`,
    but it will be changed to `ffffffffffffffffffffff` since opcode THROW doesn't
    work, so, revert by calling unused opcode.
    """
    raise Exception(0xF1F1F2F2F3F3F4F4)

"""
https://github.com/ONT-Avocados/python-template/blob/master/libs/SafeCheck.py
"""
def Require(condition):
    """
	If condition is not satisfied, return false
    :param condition: required condition
    :return: True or false
	"""
    if not condition:
        Revert()
    return True

def RequireScriptHash(key):
    """
    Checks the bytearray parameter is script hash or not. Script Hash
    length should be equal to 20.
    :param key: bytearray parameter to check script hash format.
    :return: True if script hash or revert the transaction.
    """
    Require(len(key) == 20)
    return True

def RequireWitness(witness):
    """
	Checks the transaction sender is equal to the witness. If not
	satisfying, revert the transaction.
	:param witness: required transaction sender
	:return: True if transaction sender or revert the transaction.
	"""
    Require(CheckWitness(witness))
    return True

"""
https://github.com/ONT-Avocados/python-template/blob/master/libs/SafeMath.py
"""

def Add(a, b):
    """
    Adds two numbers, throws on overflow.
    """
    c = a + b
    Require(c >= a)
    return c

def Sub(a, b):
    """
    Substracts two numbers, throws on overflow (i.e. if subtrahend is greater than minuend).
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
    """
    Require(a>=b)
    return a-b

def ASub(a, b):
    if a > b:
        return a - b
    if a < b:
        return b - a
    else:
        return 0

def Mul(a, b):
    """
    Multiplies two numbers, throws on overflow.
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
    """
    if a == 0:
        return 0
    c = a * b
    Require(c / a == b)
    return c

def Div(a, b):
    """
    Integer division of two numbers, truncating the quotient.
    """
    Require(b > 0)
    c = a / b
    return c

def Pwr(a, b):
    """
    a to the power of b
    :param a the base
    :param b the power value
    :return a^b
    """
    c = 0
    if a == 0:
        c = 0
    elif b == 0:
        c = 1
    else:
        i = 0
        c = 1
        while i < b:
            c = Mul(c, a)
            i = i + 1
    return c

def Sqrt(a):
    """
    Return sqrt of a
    :param a:
    :return: sqrt(a)
    """
    c = Div(Add(a, 1), 2)
    b = a
    while(c < b):
        b = c
        c = Div(Add(Div(a, c), c), 2)
    return c
######################### Utility Methods End #########################
