def dictlist_mf(mf_holdings):
        list = []
        for mf in mf_holdings:
                dict_mf = {}
                dict_mf['label'] = mf['fund']
                dict_mf['value'] = round(float(mf['last_price']*mf['quantity']))
                list.append(dict_mf)
        return list