from flask import Flask, render_template, request, redirect, session
import os
from time import time
from wallet import Wallet
from wallet import Account
from wallet import setweb3
import firebase_admin
from firebase_admin import credentials

STATIC_DIR = os.path.abspath('static')

app = Flask(__name__, static_folder=STATIC_DIR)
app.use_static_for_root = True

myWallet =  Wallet()
account = None
allAccounts = []
user= None
isSignedIn = False
# Create isTestnetSelected flag variable that tells if testnet is selected or not and set it to false initially
isTestnetSelected = False
# Create testneturl string to pass the addres of selected testnet and set it to empty string initially
testneturl = ""


def firebaseInitialization():
    cred = credentials.Certificate("config/serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://blockchain-wallet-a2812-default-rtdb.firebaseio.com'})
    print("🔥🔥🔥🔥🔥 Firebase Connected! 🔥🔥🔥🔥🔥")

firebaseInitialization()

@app.route("/", methods= ["GET", "POST"])
def home():
    global myWallet, account, allAccounts, isSignedIn, isTestnetSelected
    isConnected = False
    if isTestnetSelected == True:
         
        isConnected = myWallet.checkConnection()
   
    balance = "No Balance"
    transactions = None

    if(isSignedIn):
        allAccounts = myWallet.getAccounts()
        if(account == None and allAccounts):
            account = allAccounts[0]

        if(account):
            if(type(account) == dict):
                balance = myWallet.getBalance(account['address'])
                transactions = myWallet.getTransactions(account['address'])
            else:
                balance = myWallet.getBalance(account.address)
                transactions = myWallet.getTransactions(account.address)
        
    return render_template('index.html', 
                        isTestnetSelected=isTestnetSelected,
                        isConnected=isConnected,  
                        account= account, 
                        balance = balance, 
                        transactions = transactions, 
                        allAccounts=allAccounts,
                        isSignedIn = isSignedIn)



@app.route("/makeTransaction", methods = ["GET", "POST"])
def makeTransaction():
    global myWallet, account
    receiver = request.form.get("receiverAddress")
    amount = request.form.get("amount")

    privateKey = None
    if(type(account) == dict):
            privateKey = account['privateKey']
            sender= account['address']
    else:
            privateKey = account.privateKey
            sender= account.address

    privateKey = account['privateKey']

    tnxHash = myWallet.makeTransactions(sender, receiver, amount, privateKey)
    myWallet.addTransactionHash(tnxHash, sender, receiver,amount)
    return redirect("/")


@app.route("/createAccount", methods= ["GET", "POST"])
def createAccount(): 
    global account, myWallet
    username = myWallet.username
    account = Account(username)
    return redirect("/")

@app.route("/changeAccount", methods= ["GET", "POST"])
def changeAccount(): 
    global account, allAccounts
    
    newAccountAddress = int(request.args.get("address"))
    account = allAccounts[newAccountAddress]
    return redirect("/")

@app.route("/signIn", methods= ["GET", "POST"])
def signIn(): 
    global account, allAccounts, isSignedIn, myWallet
    isSignedIn = True
    
    username = request.form.get("user")
    password = request.form.get("password")
    
    isSignedIn = myWallet.addUser(username, password)
    return redirect("/")

@app.route("/signOut", methods= ["GET", "POST"])
def signOut(): 
    global account, allAccounts, isSignedIn
    isSignedIn = False
    return redirect("/")

#Create /selectTestnet path to select the testnet either sepolia or goerli
@app.route("/selectTestnet", methods= ["GET", "POST"])
# Define selectTestnet() function
def selectTestnet(): 
    # Access account, allAccounts, myWallet and isTestnetSelected as global
    global account, allAccounts, myWallet, isTestnetSelected
   
    # Access the testnet argument sent on the path and store it in slectedTestnet variable. 
    slectedTestnet = request.form.get("testnet")
    print(slectedTestnet)

    # Check the value of slectedTestnet variable, if its sepolia or goerli. 
    if slectedTestnet == "sepolia":
        # Set the testneturl to the sepolia API with key and set the isTestnetSelected to true. 
         testneturl = "https://sepolia.infura.io/v3/5f29b851d6984f498f84032f3ccae759"
         isTestnetSelected = True
        #Call the setweb3() function and pass the testneturl to set the sepolia testnet
         setweb3(testneturl)
    else:
        # Else, set the testneturl to the goerli API with key and and set the isTestnetSelected to true. 
         testneturl = "https://goerli.infura.io/v3/5f29b851d6984f498f84032f3ccae759"
         isTestnetSelected = True
        #Call the setweb3() function and pass the testneturl to set the goerli testnet
         setweb3(testneturl)
    return redirect("/")


if __name__ == '__main__':
    app.run(debug = True, port=4001)



