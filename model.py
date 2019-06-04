import pandas as pd
import wrapper

'''
Wrapper function to connect, commit and close a database connection
'''
def connect(query_function):
    import sqlite3

    def wrapper(*args,**kwargs):
        con = sqlite3.connect("stock_trading.db")
        result = query_function(*args,**kwargs,con = con)
        con.commit()
        con.close()
        return result

    return wrapper

'''
Get user information matching the username in a dictionary
'''
@connect
def getUserInfo(username,**kwargs):
    result = pd.read_sql(f"SELECT * FROM users WHERE username = '{username}'",**kwargs)
    return result.to_dict('records')

'''
Register user
'''
@connect
def registerUser(username,password,**kwargs):
    con = kwargs.get("con",None)
    con.execute(
        '''
        INSERT INTO users (username,password)
        VALUES (?,?)
        ''', (username,password)
    )

'''
Stock Portfolio for a specified user
'''
@connect
def stockPortfolio(username,**kwargs):
    query = f'''
    SELECT stock_ticker, SUM(number_of_shares) AS number_of_shares_owned
    FROM orders 
    WHERE order_made_by = "{username}"
    GROUP BY stock_ticker
    '''
    data = pd.read_sql(query,**kwargs)
    return data[data['number_of_shares_owned'] > 0]

'''
Get a specific users current bank balance
'''
@connect
def getBankBalance(username, **kwargs):
    current_account = pd.read_sql("SELECT bank_account FROM users WHERE username = '{0}'".format(username),**kwargs)
    return current_account.iloc[0,0]

'''
Check whether user has enough funds to execute the buy order
'''
@connect
def checkFunds(username, stock_price, number_of_shares, **kwargs):
    bank_account = getBankBalance(username)
    if stock_price*number_of_shares > bank_account:
        return False
    else:
        return True

'''
Check whether user owns enough stocks to execute the sell order
'''
def checkStocks(username, stock_ticker, number_of_shares):
    net_stocks = stockPortfolio(username)
    num_stocks_ticker = net_stocks[net_stocks['stock_ticker'] == stock_ticker]['number_of_shares_owned'].values[0]
    if number_of_shares > num_stocks_ticker:
        return False
    else:
        return True

'''
Execute a buy order and write it to the database
'''
@connect
def buyStock(username,ticker,price,number_of_shares,datetime, **kwargs):
    con = kwargs.get("con",None)
    con.execute(
        '''
        INSERT INTO orders (order_type,order_made_by,order_timestamp,stock_ticker,strike_price,number_of_shares)
        VALUES (?,?,?,?,?,?)
        ''', ("buy",username,datetime,ticker,price,number_of_shares)
    )

'''
Execute a sell order and write it to the database
'''
@connect
def sellStock(username,ticker,price,number_of_shares,time,**kwargs):
    con = kwargs.get("con",None)
    con.execute(
    '''
    INSERT INTO orders (order_type,order_made_by,order_timestamp,stock_ticker,strike_price,number_of_shares)
    VALUES (?,?,?,?,?,?)
    ''', ("sell",username,time,ticker,price,-number_of_shares)
    )

'''
Add money to the users bank account after a sell order
'''
@connect
def creditAccount(username,price,number_of_shares,**kwargs):
    current_account = getBankBalance(username)
    new_balance = current_account + (price*number_of_shares)
    con = kwargs.get("con",None)
    con.execute(
        '''
        UPDATE users
        SET bank_account = ?
        WHERE username = ?
        ''', (new_balance,username)
    )
    return new_balance

'''
Deduct money from a users account after a buy order
'''
@connect
def deductAccount(username,price,number_of_shares,**kwargs):
    current_account = getBankBalance(username)   
    new_balance = current_account - (price*number_of_shares)
    con = kwargs.get("con",None)
    con.execute(
        '''
        UPDATE users
        SET bank_account = ?
        WHERE username = ?
        ''', (new_balance,username)
    )
    return new_balance

'''
Get all users portfolio
'''
@connect
def getAllPortfolios(**kwargs):
    query = '''
    SELECT order_made_by AS username, stock_ticker, SUM(number_of_shares) AS number_of_shares_owned
    FROM orders 
    GROUP BY stock_ticker, order_made_by
    ORDER BY order_made_by ASC
    '''
    con = kwargs.get("con",None)
    all_p = pd.read_sql(query,con)
    return all_p

'''
Get all users and their bank accounts
'''
@connect
def getAllBanks(**kwargs):
    con = kwargs.get("con",None)
    data = pd.read_sql("SELECT username,bank_account FROM users",con)
    return data

'''
Create a leaderboard of users
'''
def leaderboard(**kwargs):
    all_p = getAllPortfolios()
    all_p['current_price'] = all_p.apply(lambda x: wrapper.Markit().get_price(x['stock_ticker']), axis = 1)
    all_p['worth'] = all_p['number_of_shares_owned']*all_p['current_price']
    all_p = all_p[['username','worth']].groupby('username').sum().reset_index()
    banks = getAllBanks()
    final = pd.merge(all_p,banks,how = 'outer',on = ['username','username'])
    final.fillna(0,inplace = True)
    final['net_worth'] = final['worth'] + final['bank_account']
    return final.sort_values(['net_worth','username'],ascending = [0,1])[['username','net_worth']]