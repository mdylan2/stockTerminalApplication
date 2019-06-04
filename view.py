'''
The Main Menu of the App
'''
def mainMenu():
    return '''
What would you like to do today?
[1] --> Login
[2] --> Register
[3] --> Quit
Enter your choice: '''

# def adminMenu(username):
#     return f'''
# What would you like to do today {username}?
# [1] --> See Leaderboard
# [2] --> Logout
# Enter your choice: '''

def userMenu(username,admin):
    if admin == 1:
        return f'''
What would you like to do today {username}?
[1] --> Search by Company Name
[2] --> Get Up-to-Date Data by Stock Ticker
[3] --> View Portfolio
[4] --> Buy Stocks
[5] --> Sell Stocks
[6] --> Leaderboard
[7] --> Logout
Enter your choice: '''
    else:
        return f'''
What would you like to do today {username}?
[1] --> Search by Company Name
[2] --> Get Up-to-Date Data by Stock Ticker
[3] --> View Portfolio
[4] --> Buy Stocks
[5] --> Sell Stocks
[6] --> Logout
Enter your choice: '''



'''
Dealing with invalid strings
'''
def invalidString(entry,menu):
    return f"Invalid {entry}. Taking you back to the {menu}."


'''
Dealing with valid strings
'''
def validString(entry,menu):
    return f"Valid {entry}. Taking you to the {menu}."

'''
Standardized query strings
'''
def queryString(parameter):
    return f"Please enter {parameter}: "

'''
Printing routing info
'''
def printRoute(message,nextPage):
    return f"{message}, taking you to {nextPage}"

'''
Page titles
'''
def printTitle(title):
    return f"----{title} Page----"

'''
Faulty API codes
'''
def faultyCode(ticker):
    return f"Faulty API status code for {ticker}."

'''
Print Dictionary
'''
def printDict(dictionary):
    string = ""
    for key, value in dictionary.items():
        string += (f"{key}: {value}\n")
    return string

'''
Success for orders
'''
def printSuccess(order_type,number_of_shares,ticker,now, account):
    return f'''Successfully executed {order_type} order for {number_of_shares} of {ticker} on {now}. 
Your new bank balance is ${account}.
    '''