totalOptions={
    "BTC":"0.01",
    "ETH":"0.1",
    "SOL":"1.0",
    "MNT":"10",
    "XRP":"10",
    "DOGE":"1000",
    "HYPE":"1.0"}


"""Нужно найти фючерс который есть в totalOptions но нет option и 
при этом не закрыть futures котоый

    """

futures =  {'ETH':[], 'SOL':[],'1000PEPE': [{'symbol': '1000PEPE/USDT:USDT', 'side': 'buy', 'size': 13100.0, 'openPrice': 0.004071, 'leverage': 1.0, 'initMargin': 53.3563, 'positionIdx': 1}], 'HYPE': [{'symbol': 'HYPE/USDT:USDT', 'side': 'sell', 'size': 3.0, 'openPrice': 85.925, 'leverage': 10.0, 'initMargin': 25.1019525, 'positionIdx': 2}]}

option = {'XRP': [{'symbol': 'XRP/USDT:USDT-261014-1.38-C', 'ccxt_symbol': 'XRP/USDT:USDT-261014-1.38-C', 'buyOrSell': 'sell', 'size': 150.0, 'entry_price': 0.0116, 'hours_to_expiration': 26.98, 'strike': 1.38, 'type': 'CALL', 'futures_symbol': 'XRP/USDT:USDT', 'initMargin': 41.0686875}, {'symbol': 'XRP/USDT:USDT-261014-1.36-P', 'ccxt_symbol': 'XRP/USDT:USDT-261014-1.36-P', 'buyOrSell': 'sell', 'size': 150.0, 'entry_price': 0.0126, 'hours_to_expiration': 26.98, 'strike': 1.36, 'type': 'PUT', 'futures_symbol': 'XRP/USDT:USDT', 'initMargin': 41.874981}], 'HYPE': [{'symbol': 'HYPE/USDT:USDT-261013-87-C', 'ccxt_symbol': 'HYPE/USDT:USDT-261013-87-C', 'buyOrSell': 'sell', 'size': 3.0, 'entry_price': 0.82, 'hours_to_expiration': 99.0, 'strike': 87.0, 'type': 'C', 'futures_symbol': 'HYPE/USDT:USDT', 'initMargin': 27.26524007},{'symbol': 'HYPE/USDT:USDT-261013-86-P', 'ccxt_symbol': 'HYPE/USDT:USDT-261013-86-P', 'buyOrSell': 'sell', 'size': 3.0, 'entry_price': 0.76, 'hours_to_expiration': 99.0, 'strike': 86.0, 'type': 'P', 'futures_symbol': 'HYPE/USDT:USDT', 'initMargin': 47.14828184}]}

for coin in totalOptions:
# for coin in option:
    # print("все монеты которые могут быть опционы", coin)
    if coin in futures:
        # print("все монеты которые открыты фючи под опционы", coin)
        if coin not in option:
            print("монеты под которые истекли опционы", coin)
        
    
    
