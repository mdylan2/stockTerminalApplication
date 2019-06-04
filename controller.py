from datetime import datetime

import view
import controller
import model
import wrapper

'''
The main app entry point
'''
def app():
    ask = input(view.mainMenu()).strip()
    if ask == str(1):
        user = userLogin()
        userApp(user)
    elif ask == str(2):
        userRegistration()
    elif ask == str(3):
        print(view.printRoute("Quitting the application","the real world."))
        return
    else:
        print(view.invalidString("Input","Main Menu"))
        app()


'''
The login controller
'''
def userLogin():
    username = input(view.queryString("username"))
    password = input(view.queryString("password"))
    user_info = model.getUserInfo(username)
    if not user_info == []:
        if user_info[0]['password'] == password:
            print(view.validString("Credentials","User Menu"))
            return user_info[0]
        else:
            print(view.invalidString("Credentials","Main Menu"))
            app()
    else:
        print(view.invalidString("Credentials","Main Menu"))
        app()

'''
Handling log outs
'''
def userLogout():
    view.printRoute("Logged you out","main menu")
    app()

'''
The registration controller
'''
def userRegistration():
    print(view.printTitle("Registration"))
    username = input(view.queryString("username"))
    if not model.getUserInfo(username) == []:
        print(view.invalidString("username","registration menu"))
        userRegistration()
    else:
        password = input(view.queryString("password"))
        model.registerUser(username,password)
        print(view.printRoute(f"Registered {username} with password {password}.","main menu"))
        app()

'''
User app controller
'''
def userApp(user):
    ask = input(view.userMenu(user['username'],user['admin'])).strip()
    if ask == str(1):
        companySearch(user)
        userApp(user)
    elif ask == str(2):
        stockTickerSearch(user)
        userApp(user)
    elif ask == str(3):
        stockPortfolio(user)
        userApp(user)
    elif ask == str(4):
        transactStock("buy", user)
        userApp(user)
    elif ask == str(5):
        transactStock("sell", user)
        userApp(user)
    elif ask == str(6):
        if user['admin'] == 0:
            userLogout()
        else:
            leaderboard()
            userApp(user)
    elif ask == str(7) and user['admin'] == 1:
            userLogout()
    else:
        print(view.invalidString("input","main menu"))
        userApp(user)

'''
Company search controller
'''
def companySearch(user):
    print(view.printTitle("Company Search"))
    company_name = input(view.queryString("Company Name"))
    companies = wrapper.Markit().company_search(company_name)
    if companies.empty:
        print(view.invalidString("company name","user page"))
    else:
        print(f"Company list that matches {company_name}:")
        print(companies.to_string(index = False))

'''
Stock ticker search controller
'''
def stockTickerSearch(user):
    print(view.printTitle("Stock Ticker Search"))
    ticker_input = input(view.queryString("Stock Ticker: ")).strip().upper()
    quote = wrapper.Markit().get_quote(ticker_input,'Name','Symbol','LastPrice','Open','Timestamp')
    if quote == {}:
        print(view.invalidString("stock ticker","user page"))
    else:
        print(f"Information on {ticker_input}:")
        print(view.printDict(quote))

'''
Stock portfolio controller
'''
def stockPortfolio(user):
    portfolio = model.stockPortfolio(user['username'])
    if portfolio.empty:
        print("You don't have any stocks.")
    else:
        print("A table of the stocks you own:")
        print(portfolio.to_string(index = False))

'''
Buy stock controller
'''
def transactStock(order_type,user):
    ask = input(view.queryString(f"stock ticker and number of shares you'd like to {order_type} (Eg: AAPL 5)")).split()
    ticker, quote, number_of_shares = transactErrorCheck(ask,order_type,user)
    print(f"Latest price of {ticker} as of {quote['Timestamp']}:")
    print(f"Price: ${quote['LastPrice']}")
    if confirmOrder(order_type,user):
        now = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        if order_type == "buy":
            model.buyStock(user['username'],ticker,quote['LastPrice'],number_of_shares,now)
            new_acc_balance = model.deductAccount(user['username'],quote['LastPrice'],number_of_shares)
            print(view.printSuccess(order_type,number_of_shares,ticker,now,new_acc_balance))
        elif order_type == "sell":
            model.sellStock(user['username'],ticker,quote['LastPrice'],number_of_shares,now)
            new_acc_balance = model.creditAccount(user['username'],quote['LastPrice'],number_of_shares)
            print(view.printSuccess(order_type,number_of_shares,ticker,now,new_acc_balance))

'''
Leaderboard controllers
'''
def leaderboard():
    print("Fetching current market data...")
    data = model.leaderboard()
    print("Here's the leaderboard in terms of net worth (Portfolio Value + Bank Balance):")
    print(data.to_string(index = False))


'''
Checking for errors in inputs for buy/sell transactions.
Returns the split inputs if correctly entered
'''
def transactErrorCheck(order_list, order_type, user):
    if len(order_list) != 2:
        print(view.invalidString("input",f"{order_type} menu"))
        transactStock(order_type,user)
    try:
        number_of_shares = int(order_list[1])
    except:
        print(view.invalidString("number of shares input",f"{order_type} menu"))
        transactStock(order_type,user)
    if int(number_of_shares) != float(number_of_shares):
        print(view.invalidString("number of shares input (decimals)",f"{order_type} menu"))
        transactStock(order_type,user)
    ticker = order_list[0].strip().upper()
    quote = wrapper.Markit().get_quote(ticker,"LastPrice","Timestamp")
    if quote == {}:
        print(view.invalidString("stock ticker input",f"{order_type} menu"))
        transactStock(order_type,user)
    if order_type == "buy":
        if not model.checkFunds(user['username'],quote['LastPrice'],number_of_shares):
            print(view.invalidString("funds to execute the buy order",f"{order_type} menu"))
            transactStock(order_type,user)
        else:
            return ticker, quote, number_of_shares
    elif order_type == "sell":
        if not model.checkStocks(user['username'],ticker,number_of_shares):
            print(view.invalidString(f"number of stocks entered. You don't have that many stocks of {ticker}",f"{order_type} menu"))
            transactStock(order_type,user)
        else:
            return ticker, quote, number_of_shares

'''
Controller for buy/sell order confirmations
'''
def confirmOrder(order_type,user):
    print("Confirm Order?")
    confirmation = input(view.queryString("Yes or No")).lower().strip()
    if confirmation not in ["yes","no"]:
        print(view.invalidString("input",f"{order_type} menu"))
        transactStock(order_type,user)
    elif confirmation == "no":
        print(view.printRoute("Order cancelled","main menu"))
        userApp(user)
    elif confirmation == "yes":
        return True
        

if __name__ == '__main__':
    app()