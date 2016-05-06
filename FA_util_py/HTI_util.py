import ael

LOCAL_EXCHANGE_CODE = 'Local Exchange Code and MIC'
BLOOMBERG_TICKER = 'Bloomberg Ticker'
ISIN = 'ISIN'

market_code_array = ['HKEX', 'HKFE']
market_mic_array = ['XHKG','XHKF']

exchange_code_array = ['HK','SG']
mic_array = ['XHKG','XSGG']

def exchangeToMICByProdType(exchange_code, product_type):
    if exchange_code == 'HK':
        if product_type == 'Stock':
            return 'XHKG'
        else:
            return 'XHKF'
    return exchange_code

def marketToMIC(market):
    #market = HKEX, HKFE etc.
    index = 0    
    found = False
    for market_code in market_code_array:        
        if market == market_code:            
            found = True
            break
        index = index + 1
    if found:
        return market_mic_array[index]
    else:
        return market

def exchangeToMIC(exchange_code):
    #exchange = HK, SG etc.
    
    index = 0    
    found = False
    for exchange in exchange_code_array:        
        if exchange == exchange_code:
            found = True
            break
        index = index + 1
    if found:
        return mic_array[index]
    else:
        return exchange_code
        
def micToExchange(mic_code):
    index = 0    
    found = False
    for mic in mic_array:        
        if mic == mic_code:
            found = True
            break
        index = index + 1
    if found:
        return exchange_code_array[index]
    else:
        return mic_code
            
def getCommodityCodeFileTypes():
    types = []
    types.append("Equity")
    types.append("Derivative")
    return types

def getAllFOSystems():
    fosystems = []
    rs = None
    strSql = """select entry
                from ChoiceList
                where list = 'Trade Source'"""
                
    rs = ael.asql(strSql) 
    columns, buf = rs
    for table in buf:                          
        for row in table:          
            fosystems.append(row[0].strip())
    fosystems.sort()
    return fosystems
    
def getAllMarkets():
    market = []
    for pty in ael.Party.select("type = 'Market'"):
        market.append(pty.display_id())
    market.sort()
    return market
    
def getAllMTMMarkets():
    market = []
    for pty in ael.Party.select("type = 'MTM Market'"):
        market.append(pty.display_id())
    market.sort()
    return market


def get_dates():
    dates = []
    dates.append("TODAY")
    dates.append(ael.date('2015-05-28'))
    return dates
    
def get_yesno():
    ret = []
    ret.append("Y")
    ret.append("N")
    return ret
    
def getAllAcquirers():
    acquirers = []
    for acq in ael.Party.select("type = 'Intern Dept'"):
        acquirers.append(acq.display_id())
    acquirers.sort()
    return acquirers
    
def getAllIssuers():
    issuers = []
    for issuer in ael.Party.select("type = 'Issuer'"):
        issuers.append(issuer.display_id())
    issuers.sort()
    return issuers
    
def getAllStatus():
    status = []
    status.append('Simulated')
    status.append('FO Confirmed')
    status.append('BO Confirmed')
    status.append('BO-BO Confirmed')
    status.sort()
    return status   

def get_feedcode():
    ret = []
    ret.append(LOCAL_EXCHANGE_CODE)
    ret.append(BLOOMBERG_TICKER)
    ret.append(ISIN)
    return ret
    
def getAllBrokers():
    parties = []
    for pty in ael.Party.select("type = 'Broker'"):
        parties.append(pty.display_id())
    parties.sort()
    return parties
        
def getAllPortfolios():
    portfolios = []
    for port in ael.Portfolio.select():
        portfolios.append(port.display_id())
    portfolios.sort()
    return portfolios
    
def getAllParties():
    parties = []
    for pty in ael.Party.select("type = 'Client'"):
        parties.append(pty.display_id())
    for pty in ael.Party.select("type = 'Broker'"):
        parties.append(pty.display_id())
    for pty in ael.Party.select("type = 'Counterparty'"):
        parties.append(pty.display_id())
    parties.sort()
    return parties

def getAllAcquirers():
    acquirers = []
    for acq in ael.Party.select("type = 'Intern Dept'"):
        acquirers.append(acq.display_id())
    acquirers.sort()
    return acquirers
    
def getAllIssuers():
    issuers = []
    for issuer in ael.Party.select("type = 'Issuer'"):
        issuers.append(issuer.display_id())
    issuers.sort()
    return issuers
    
def getAllStatus():
    status = []
    status.append('Simulated')
    status.append('FO Confirmed')
    status.sort()
    return status    
        
def get_quot():
    ret = []
    ret.append("FA")
    ret.append("PER UNIT")
    return ret


def MatchTradeAgainstSystem(system, acm_ins):
    insType = acm_ins.InsType()
    
    if system == '':
        return True
    elif system == 'MSSE':
        if insType == 'Stock':
            return True
        elif insType == 'Future/Forward':
            return False            
        elif insType == 'Option':
            acm_ins_und_type = acm_ins.Underlying().InsType()
            if acm_ins_und_type != 'Stock':
                return False
            else:
                return True
    elif system == 'MSSD':
        if insType == 'Stock':
            return False
        elif insType == 'Future/Forward':
            return True 
        elif insType == 'Option':
            acm_ins_und_type = acm_ins.Underlying().InsType()
            if acm_ins_und_type != 'Stock':
                return True
            else:
                return False
                
    return False
        
                    
def getAllInstypes():
    insType = []
    insType.append('BasketRepo/Reverse')
    insType.append('BasketSecurityLoan')             
    insType.append('Bill')                           
    insType.append('Bond')                           
    insType.append('BondIndex')                      
    insType.append('BuySellback')                    
    insType.append('CallAccount')                    
    insType.append('Cap')                            
    insType.append('CashCollateral')
    insType.append('CD')                             
    insType.append('Certificate')                    
    insType.append('CFD')
    insType.append('CLN')                            
    insType.append('Collar')                         
    insType.append('Collateral')                     
    insType.append('Combination')                    
    insType.append('Commodity')                      
    insType.append('Commodity Index')                
    insType.append('Commodity Variant')              
    insType.append('Convertible')
    insType.append('Credit Balance')                 
    insType.append('CreditDefaultSwap')              
    insType.append('CreditIndex')
    insType.append('Curr')
    insType.append('CurrSwap')                       
    insType.append('Deposit')                        
    insType.append('Depositary Receipt')             
    insType.append('Dividend Point Index')           
    insType.append('DualCurrBond')                   
    insType.append('EquityIndex')                    
    insType.append('EquitySwap')                     
    insType.append('ETF')                            
    insType.append('Flexi Bond')                     
    insType.append('Floor')                          
    insType.append('FRA')                            
    insType.append('FreeDefCF')                      
    insType.append('FRN')                            
    insType.append('Fund')                           
    insType.append('Future/Forward')                 
    insType.append('Fx Rate')                        
    insType.append('FXOptionDatedFwd')               
    insType.append('FxSwap')                         
    insType.append('IndexLinkedBond')                
    insType.append('IndexLinkedSwap')                
    insType.append('LEPO')                           
    insType.append('MBS/ABS')                        
    insType.append('MultiAsset')                     
    insType.append('MultiOption')                    
    insType.append('None')                           
    insType.append('Option')                         
    insType.append('Portfolio Swap')                 
    insType.append('PriceIndex')                     
    insType.append('PriceSwap')                      
    insType.append('PromisLoan')                     
    insType.append('RateIndex')                      
    insType.append('Repo/Reverse')                   
    insType.append('SecurityLoan')                   
    insType.append('Stock')                          
    insType.append('StockRight')                     
    insType.append('Swap')                           
    insType.append('TotalReturnSwap')                
    insType.append('UnKnown')                        
    insType.append('VarianceSwap')                   
    insType.append('VolatilitySwap')                 
    insType.append('Warrant')                        
    insType.append('Zero')        
    insType.sort()
    return insType