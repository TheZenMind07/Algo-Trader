def dictlist_mf(mf_holdings):
        list = []
        for mf in mf_holdings:
                dict_mf = {}
                dict_mf['label'] = mf['fund']
                dict_mf['value'] = round(float(mf['last_price']*mf['quantity']))
                list.append(dict_mf)
        return list


def dictlist_stock(holdings):
        list = []
        for stock in holdings:
                dict_mf = {}
                dict_mf['label'] = stock['tradingsymbol']
                dict_mf['value'] = round(float(stock['last_price']*stock['quantity']))
                list.append(dict_mf)
        return list

def dictlist_position(positions):
        list = []
        for position in positions:
                dict_mf = {}
                dict_mf['label'] = position['tradingsymbol'] + " " + ( "long" if position['value'] < 0 else "short")
                dict_mf['value'] = abs(position['value'])
                list.append(dict_mf)
        return list