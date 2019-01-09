"""
DNA
"""
from ontology.interop.Ontology.Contract import Migrate
from ontology.interop.System.Storage import GetContext, Get, Put, Delete
from ontology.interop.System.Runtime import CheckWitness, GetTime, Notify, Serialize, Deserialize
from ontology.interop.System.ExecutionEngine import GetExecutingScriptHash, GetScriptContainer
from ontology.interop.Ontology.Native import Invoke
from ontology.interop.Ontology.Runtime import GetCurrentBlockHash, Base58ToAddress
from ontology.builtins import concat, state, sha256, Exception, len, append, remove, abs
from ontology.interop.System.Transaction import GetTransactionHash


Owner = Base58ToAddress('ASwaf8mj2E3X18MHvcJtXoDsMqUjJswRWS')
ContractAddress = GetExecutingScriptHash()
context = GetContext()
TypeMagnitude = 100000000000000
GradeMagnitude = 1000000000000
NameMagnitude = 1000000000
SequenceNumMagnitude = 1000


PLAYER_ADDRESS_PRE_KEY = "P1"
ADMIN_ADDRESS_KEY = "P2"
DNA_PRE_KEY = "P3"


def Main(operation, args):
    if operation == "addAdmin":
        Account = args[0]
        return addAdmin(Account)
    if operation == "createProperty":
        createList = args[0]
        return createProperty(createList)
    if operation == "transferProperty":
        transferList = args[0]
        return transferProperty(transferList)
    if operation == "removeProperty":
        removeList = args[0]
        return removeProperty(removeList)
    if operation == "getPlayerAllDNA":
        account = args[0]
        return getPlayerAllDNA(account)
    if operation == "migrateContract":
        Require(len(args) == 8)
        code = args[0]
        needStorage = args[1]
        name = args[2]
        version = args[3]
        author = args[4]
        email = args[5]
        description = args[6]
        return migrateContract(code, needStorage, name, version, author, email, description)


def addAdmin(Account):
    """
    :param Account: new admin's address
    :return:
    """
    RequireWitness(Owner)
    adminList = Get(context, ADMIN_ADDRESS_KEY)
    adminList = Deserialize(adminList)
    adminList.append(Account)
    Put(context, ADMIN_ADDRESS_KEY, Serialize(adminList))
    Notify(["Now admin address is", adminList])
    return True


def createProperty(createList):
    """
    :param createList: [[account1, DNA1],[account2, DNA2]]
    :return: bool
    """
    RequireWitness(Owner)
    for createE in createList:
        account = createE[0]
        DNA = createE[1]
        accountCheck = Get(context, concatKey(DNA_PRE_KEY, DNA))
        Require(len(account) == 20)
        Require(DNA > 100000000000000)
        Require(DNA < 1000000000000000)
        Require(not accountCheck)
        DNAlist = Get(context, concatKey(PLAYER_ADDRESS_PRE_KEY, account))
        if not DNAlist:
            DNAlist = []
        else:
            DNAlist = Deserialize(DNAlist)
        DNAlist.append(DNA)
        Put(context, concatKey(DNA_PRE_KEY, DNA), account)
        Put(context, concatKey(PLAYER_ADDRESS_PRE_KEY, account), Serialize(DNAlist))
    Notify(["Create property successfully."])
    return True


def transferProperty(transferList):
    """
    :param transferList: [[toAccount1, DNA1],[toAccount2, DNA2]]
    :return: bool
    """
    DNACheck = transferList[0][1]
    account = Get(context, concatKey(DNA_PRE_KEY, DNACheck))
    RequireWitness(account)

    for transferE in transferList:
        toAccount = transferE[0]
        DNA = transferE[1]

        DNAlist = Get(context, concatKey(PLAYER_ADDRESS_PRE_KEY, account))
        DNAlist = Deserialize(DNAlist)

        toDNAlist = Get(context, concatKey(PLAYER_ADDRESS_PRE_KEY, toAccount))
        if not toDNAlist:
            toDNAlist = []
        else:
            toDNAlist = Deserialize(DNAlist)

        num = 0
        while num < len(DNAlist):
            if DNAlist[num] == DNA:
                Put(context, concatKey(DNA_PRE_KEY, DNA), toAccount)
                DNAlist.remove(num)
                toDNAlist.append(DNA)
                Put(context, concatKey(PLAYER_ADDRESS_PRE_KEY, account), Serialize(DNAlist))
                Put(context, concatKey(PLAYER_ADDRESS_PRE_KEY, toAccount), Serialize(toDNAlist))
            num += 1
    Notify(["Transfer property successfully"])
    return True


def removeProperty(removeList):
    """
    :param removeList: [DNA1, DNA2]
    :return: bool
    """
    DNACheck = removeList[0]
    account = Get(context, concatKey(DNA_PRE_KEY, DNACheck))
    RequireWitness(account)

    for DNA in removeList:
        DNAlist = Get(context, concatKey(PLAYER_ADDRESS_PRE_KEY, account))
        DNAlist = Deserialize(DNAlist)

        num = 0
        while num < len(DNAlist):
            if DNAlist[num] == DNA:
                Delete(context, concatKey(PLAYER_ADDRESS_PRE_KEY, account))
                Delete(context, concatKey(DNA_PRE_KEY, DNA))
                DNAlist.remove(num)
                Put(context, concatKey(PLAYER_ADDRESS_PRE_KEY, account), Serialize(DNAlist))
            num += 1
    Notify(["Remove property successfully"])
    return True


def getPlayerAllDNA(account):
    DNAlist = Get(context, concatKey(PLAYER_ADDRESS_PRE_KEY, account))
    DNAlist = Deserialize(DNAlist)
    return DNAlist


def migrateContract(code, needStorage, name, version, author, email, description):
    RequireWitness(Owner)
    res = Migrate(code, needStorage, name, version, author, email, description)
    Require(res)
    Notify(["Migrate Contract successfully"])
    return True


def concatKey(str1,str2):
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
