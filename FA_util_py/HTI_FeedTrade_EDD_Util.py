import ael
import acm
import stat
import time
import shutil
import string
import HTI_functions
import HTI_DB_Functions
import datetime
from datetime import date

future_month_code_array = ['F','G','H','J','K','M','N','Q','U','V','X','Z']
call_month_code_array = ['A','B','C','D','E','F','G','H','I','J','K','L']
put_month_code_array = ['M','N','O','P','Q','R','S','T','U','V','W','X']

LEN_COMDY_CODE = 3

def getYear(insType, insMaturity):
    exp_day = ael.date(insMaturity).to_string("%Y%m%d")
    return exp_day[2:4]    

def getMonthCode(insType, call_option, insMaturity):
    exp_day = ael.date(insMaturity).to_string("%Y%m%d")
    
    mm = exp_day[4:6]
    
    if insType == 'Future/Forward':
        return future_month_code_array[int(mm)-1]    
    elif insType == 'Option':
        if call_option == True:
            return call_month_code_array[int(mm)-1]
        else:
            return put_month_code_array[int(mm)-1]
    
    return ''
        


def getChildPortfolio(pPf, pfarr):
    if (pPf == None):
        return pfarr    
        
    for child in pPf.children():
        pfid = child.display_id()        
        cPf = ael.Portfolio[pfid]        
        if cPf != None:
            if cPf.compound == True:
                pfarr = getChildPortfolio(cPf, pfarr)                
            else:
                pfarr.append(pfid)                
    return pfarr

def addDictError(type, header, body, errdict):
    invalidInsArray = errdict['invalidIns']
    invalidCptyArray = errdict['invalidParty']
    invalidPfArray = errdict['invalidPf']
    invalidTrdCcyArray = errdict['invalidTrdCcy']
    invalidAcqArray = errdict['invalidAcquirer']
    invalidBrokerArray = errdict['invalidBroker'] 
    invalidBuySellArray = errdict['invalidBuySell']
    invalidTraderArray = errdict['invalidTrader']
    
    print 'header=%s' % header
    
    if type == 'Instrument':                
        i = 0
        while i <= len(invalidInsArray[0])-1:            
            if len(invalidInsArray[0]) == 0:
                invalidInsArray[0].append(header)
                invalidInsArray[1].append(body)
                errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                return errdict
            else:
                if invalidInsArray[0][i] == header:
                    orgtrd = invalidInsArray[1][i]
                
                    orgtrd = invalidInsArray[1][i]
                    orgtrd = orgtrd + '|' + body
                    invalidInsArray[1][i] = orgtrd
                    errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                    return errdict
                else:                    
                    i = i + 1
        invalidInsArray[0].append(header)
        invalidInsArray[1].append(body)
        errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
        return errdict
    elif type == 'Portfolio':
        i = 0
        while i <= len(invalidPfArray[0])-1:            
            if len(invalidPfArray[0]) == 0:
                invalidPfArray[0].append(header)
                invalidPfArray[1].append(body)
                errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                return errdict
            else:
                if invalidPfArray[0][i] == header:
                    orgtrd = invalidPfArray[1][i]
                
                    orgtrd = invalidPfArray[1][i]
                    orgtrd = orgtrd + '|' + body
                    invalidPfArray[1][i] = orgtrd
                    errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                    return errdict
                else:                    
                    i = i + 1
        invalidPfArray[0].append(header)
        invalidPfArray[1].append(body)
        errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
        return errdict
    elif type == 'Counterparty':        
        i = 0
        while i <= len(invalidCptyArray[0])-1:            
            if len(invalidCptyArray[0]) == 0:
                invalidCptyArray[0].append(header)
                invalidCptyArray[1].append(body)
                errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                return errdict
            else:
                if invalidCptyArray[0][i] == header:
                    orgpty = invalidCptyArray[1][i]
                
                    orgpty = invalidCptyArray[1][i]
                    orgpty = orgpty + '|' + body
                    invalidCptyArray[1][i] = orgpty
                    errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                    return errdict
                else:                    
                    i = i + 1            
        invalidCptyArray[0].append(header)
        invalidCptyArray[1].append(body)                                
        errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
        return errdict
    elif type == 'Trade Ccy':        
        i = 0
        while i <= len(invalidTrdCcyArray[0])-1:            
            if len(invalidTrdCcyArray[0]) == 0:
                invalidTrdCcyArray[0].append(header)
                invalidTrdCcyArray[1].append(body)
                errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                return errdict
            else:
                if invalidTrdCcyArray[0][i] == header:
                    orgtrdccy = invalidTrdCcyArray[1][i]
                
                    orgtrdccy = invalidTrdCcyArray[1][i]
                    orgtrdccy = orgtrdccy + '|' + body
                    invalidTrdCcyArray[1][i] = orgtrdccy 
                    errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                    return errdict
                else:                    
                    i = i + 1            
        invalidTrdCcyArray[0].append(header)
        invalidTrdCcyArray[1].append(body)                                
        errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
        return errdict        
    elif type == 'Acquirer':        
        i = 0
        while i <= len(invalidAcqArray[0])-1:            
            if len(invalidAcqArray[0]) == 0:
                invalidAcqArray[0].append(header)
                invalidAcqArray[1].append(body)
                errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                return errdict
            else:
                if invalidAcqArray[0][i] == header:
                    orgacq = invalidAcqArray[1][i]
                
                    orgacq = invalidAcqArray[1][i]
                    orgacq = orgacq + '|' + body
                    invalidAcqArray[1][i] = orgacq 
                    errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                    return errdict
                else:                    
                    i = i + 1            
        invalidAcqArray[0].append(header)
        invalidAcqArray[1].append(body)                                
        errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
        return errdict
    elif type == 'Broker':        
        i = 0
        while i <= len(invalidBrokerArray[0])-1:            
            if len(invalidBrokerArray[0]) == 0:
                invalidBrokerArray[0].append(header)
                invalidBrokerArray[1].append(body)
                errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                return errdict
            else:
                if invalidBrokerArray[0][i] == header:
                    orgbkr = invalidBrokerArray[1][i]
                
                    orgbkr = invalidBrokerArray[1][i]
                    orgbkr = orgbkr + '|' + body
                    invalidBrokerArray[1][i] = orgbkr 
                    errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                    return errdict
                else:                    
                    i = i + 1            
        invalidBrokerArray[0].append(header)
        invalidBrokerArray[1].append(body)                                
        errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
        return errdict        
    elif type == 'BuySell':
        i = 0
        while i <= len(invalidBuySellArray[0])-1:            
            if len(invalidBuySellArray[0]) == 0:
                invalidBuySellArray[0].append(header)
                invalidBuySellArray[1].append(body)
                errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                return errdict
            else:
                if invalidBuySellArray[0][i] == header:
                    orgbs = invalidBuySellArray[1][i]
                
                    orgbs = invalidBuySellArray[1][i]
                    orgbs = orgbs + '|' + body
                    invalidBuySellArray[1][i] = orgbs
                    errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                    return errdict
                else:                    
                    i = i + 1            
        invalidBuySellArray[0].append(header)
        invalidBuySellArray[1].append(body)                                
        errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                            
    elif type == 'Trader':
        i = 0
        while i <= len(invalidTraderArray[0])-1:            
            if len(invalidTraderArray[0]) == 0:
                invalidTraderArray[0].append(header)
                invalidTraderArray[1].append(body)
                errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                return errdict
            else:
                if invalidTraderArray[0][i] == header:
                    orgbs = invalidTraderArray[1][i]
                
                    orgbs = invalidTraderArray[1][i]
                    orgbs = orgbs + '|' + body
                    invalidTraderArray[1][i] = orgbs
                    errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                    return errdict
                else:                    
                    i = i + 1            
        invalidTraderArray[0].append(header)
        invalidTraderArray[1].append(body)                                
        errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                            
        return errdict
            
def validStatus(status):    
    if status.strip() in ('FO Confirmed', 'Simulated', ''):
        return True
    else:
        return False   

def get_dates():
    dates = []
    dates.append("TODAY")
    dates.append(ael.date('2015-05-28'))
    return dates

def ClearArray(arr):
    i = 0
    cnt = len(arr)
    while i < cnt:
        arr.pop()
        i = i + 1

'''
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

def get_yesno():
    ret = []
    ret.append("Y")
    ret.append("N")
    return ret

def get_feedcode():
    ret = []
    ret.append(LOCAL_EXCHANGE_CODE)
    ret.append(BLOOMBERG_TICKER)
    ret.append(ISIN)
    return ret
'''

def getHorizonPfbyFAPf(fa_prfid):
    horizon_pf = ''
    
    strSql = """select a.value
                from portfolio pf, additionalinfo a, additionalinfospec s
                where pf.prfnbr = a.recaddr and a.addinf_specnbr = s.specnbr and s.field_name = 'HORIZON_PORTFOLIO'
                and s.rec_type = 'Portfolio'
                and pf.prfid = \'%s\'""" % (fa_prfid)
                
    #print strSql
    rs = ael.asql(strSql)
    
    columns, buf = rs
    for table in buf:                        
        for row in table:
            horizon_pf = row[0].strip()
            break
        break
            
    return horizon_pf 
    
def formatFOTradeId(fo_trade_id, channel):
    return channel.strip() + '-' + fo_trade_id + '-' + ael.date_today().to_string('%Y%m%d')
    
def getTrade(fo_trade_id, channel):
    trdnbr = -1
    
    fo_trade_id = formatFOTradeId(fo_trade_id, channel)
    
    strSql = """select trdnbr
                from trade t, additionalinfo at, additionalinfospec st, additionalinfo ac, additionalinfospec sc
                where t.trdnbr = at.recaddr and at.addinf_specnbr = st.specnbr and st.field_name = 'FO Trade Id' and st.rec_type = 'Trade'
                and t.trdnbr = ac.recaddr and ac.addinf_specnbr = sc.specnbr and sc.field_name = 'Trade Source' and sc.rec_type = 'Trade'
                and at.value = \'%s\' and ac.value = \'%s\' and status ~= 'Void'""" % (fo_trade_id, channel)
    
    #print channel.strip(), 'louis'
    print strSql
    rs = ael.asql(strSql)

    insid = ''
    columns, buf = rs
    for table in buf:                        
        for row in table:
            trdnbr = row[0]
            break
        break
            
    return trdnbr    

def getBroker(ptyid):   
    strSql = """SELECT pty.ptyid
                FROM party pty
                WHERE pty.ptyid = \'%s\' and type = 'Broker' """ % (ptyid)
    #print strSql
    rs = ael.asql(strSql)
    
    ptyid  = ''
    columns, buf = rs
    for table in buf:                        
        for row in table:
            ptyid = row[0]
    
    return ptyid

def getCounterparty(ptyid):   
    strSql = """SELECT pty.ptyid
                FROM party pty
                WHERE pty.ptyid = \'%s\' and type = 'Counterparty' """ % (ptyid)
    #print strSql
    rs = ael.asql(strSql)
    
    ptyid  = ''
    columns, buf = rs
    for table in buf:                        
        for row in table:
            ptyid = row[0]
    
    return ptyid
    
def createInstrumentAlias(insid, aliasType, aliasValue):    
    ael_ins = ael.Instrument[insid]
    acm_ins = acm.FInstrument[insid]
    if ael_ins != None:
        for aliase in acm_ins.Aliases():
            if aliase.Type().Name() == 'BB_TICKER':
                if aliase.Alias().strip() != '': # no override existing
                    return            
        
        ael_ins_clone = ael_ins.clone()
        a = ael.InstrumentAlias.new(ael_ins_clone)
        a.type = aliasType
        a.alias = aliasValue
        a.commit()
        ael.poll()
    else:
        print 'Instrument %s cannot be found, so no alias is added' % (insid)


def quoteToUnitValue(insid, quote):
    acmIns = acm.FInstrument[insid]
    return acmIns.QuoteToUnitValue(1, quote, 1)

def unitValueToQuote(insid, quote):
    acmIns = acm.FInstrument[insid]
    return acmIns.UnitValueToQuote(1, quote, 1)
    
def quoteTo(ins, date, quoteType, quote):
    insC = ins.clone()
    insC.quote_type = quoteType
    premium = insC.premium_from_quote(date, quote)
    return premium
    
    
def FeedQuoteToFAQuote(insid, feedprice, quot, Source):
    faPrice = 0
    if quot == 'FA':
        faPrice = feedprice
    elif quot == 'PER_UNIT':
        faPrice = unitValueToQuote(insid, feedprice)
    else:
        faPrice = feedprice
            
    return faPrice

def getAcquirer(ptyid):
    strSql = """SELECT pty.ptyid
                FROM party pty
                WHERE pty.ptyid = \'%s\' and type = 'Intern Dept' """ % (ptyid)
    #print strSql
    rs = ael.asql(strSql)
    
    ptyid  = ''
    columns, buf = rs
    for table in buf:                        
        for row in table:
            ptyid = row[0]
    
    return ptyid    
    
def getInstrumentByMapping(localcode, insMic):
    insid = ''
    strSql = """select i.insid
                from instrument i,
                AdditionalInfoSpec mis, AdditionalInfo mi,
                AdditionalInfoSpec lis, AdditionalInfo li
                where i.insaddr = mi.recaddr
                    and i.generic = \'No\'
                    and mi.addinf_specnbr = mis.specnbr
                    and mis.field_name = 'MIC'
                    and mi.value = '%s'
                    and i.insaddr = li.recaddr
                    and li.addinf_specnbr = lis.specnbr
                    and lis.field_name = 'Local Exchange Code'
                    and (li.value = '%s' or li.value like '%s' or li.value like '%s')""" % (insMic, localcode, localcode+',%', '%,'+localcode)
                                        
    print strSql
    rs = ael.asql(strSql)
    columns, buf = rs
    for table in buf:                        
        for row in table:
            insid = row[0].strip()
            return insid
    
    return insid

def CreateInsAdditionalInfo(ins_new_insid, insMic, insDesc, insName, localcode, insType, insUnderlying_mktId):
    acm_ins = acm.FInstrument[ins_new_insid]
    
    if insMic.strip() != '':
        #print 'A', acm_ins.AdditionalInfo().MIC()
        if acm_ins.AdditionalInfo().MIC() == None:            
            addInfoMicSpec = acm.FAdditionalInfoSpec['MIC']
            addInfoMic = acm.FAdditionalInfo()
            addInfoMic.AddInf(addInfoMicSpec.Oid())                
            addInfoMic.Recaddr(acm_ins.Oid())
            addInfoMic.FieldValue(insMic)       
            addInfoMic.Commit()
        else:
            if acm_ins.AdditionalInfo().MIC().strip() == '':
                acm_ins.AdditionalInfo().MIC(insMic)
                
        if insMic in ('XHKG','XHKF'):
            priceSource = 'Bloomberg_5PM'
        else:
            priceSource = ''

        if priceSource != '':
            if acm_ins.AdditionalInfo().Snaps_Pce_Source() == None:
                addInfoPSSpec = acm.FAdditionalInfoSpec['Snaps Pce Source']
                addInfoPS = acm.FAdditionalInfo()
                addInfoPS.AddInf(addInfoPSSpec.Oid())                
                addInfoPS.Recaddr(acm_ins.Oid())
                addInfoPS.FieldValue(priceSource)       
                addInfoPS.Commit()
            else:
                if acm_ins.AdditionalInfo().Snaps_Pce_Source().strip() == '':
                    acm_ins.AdditionalInfo().Snaps_Pce_Source(priceSource)
            
    
    if insDesc.strip() != '':
        #print 'desc', insDesc
        if acm_ins.AdditionalInfo().Ins_Description() == None:
            addInfoDescSpec = acm.FAdditionalInfoSpec['Ins Description']
            addInfoDesc = acm.FAdditionalInfo()
            addInfoDesc.AddInf(addInfoDescSpec.Oid())                
            addInfoDesc.Recaddr(acm_ins.Oid())
            addInfoDesc.FieldValue(insDesc) 
            addInfoDesc.Commit()                           
        else:
            if acm_ins.AdditionalInfo().Ins_Description().strip() == '':
                acm_ins.AdditionalInfo().Ins_Description(insDesc)        
    
    if localcode != '':
        if acm_ins.AdditionalInfo().Local_Exchange_Code() == None:
            addInfoLocalCodeSpec = acm.FAdditionalInfoSpec['Local Exchange Code']
            addInfoLocalCode = acm.FAdditionalInfo()
            addInfoLocalCode.AddInf(addInfoLocalCodeSpec.Oid())                
            addInfoLocalCode.Recaddr(acm_ins.Oid())
            addInfoLocalCode.FieldValue(localcode)    
            addInfoLocalCode.Commit()
        else:
            if acm_ins.AdditionalInfo().Local_Exchange_Code().strip() == '':
                acm_ins.AdditionalInfo().Local_Exchange_Code(localcode)        
        
    if insName != '':
        #print 'name', insName
        if acm_ins.AdditionalInfo().Ins_Short_Name() == None:
            addInfoShortNameSpec = acm.FAdditionalInfoSpec['Ins Short Name']
            addInfoShortName = acm.FAdditionalInfo()
            addInfoShortName.AddInf(addInfoShortNameSpec.Oid())                
            addInfoShortName.Recaddr(acm_ins.Oid())
            addInfoShortName.FieldValue(insName) 
            addInfoShortName.Commit()
        else:
            if acm_ins.AdditionalInfo().Ins_Short_Name().strip() == '':
                acm_ins.AdditionalInfo().Ins_Short_Name(insName)
                
    if insType in ('OPTION', 'FUTURE'):
        if insUnderlying_mktId != '':
            comdycode = insUnderlying_mktId
        else:
            if localcode != '':
                len_localcode = len(localcode)
                if len_localcode >= LEN_COMDY_CODE:
                    comdycode = localcode[0:LEN_COMDY_CODE]
                else:
                    comdycode = localcode
        
        if acm_ins.AdditionalInfo().Commodity_Code() == None:
            addInfoComdyCodeSpec = acm.FAdditionalInfoSpec['Commodity Code']
            addInfoComdyCode = acm.FAdditionalInfo()
            addInfoComdyCode.AddInf(addInfoComdyCodeSpec.Oid())                
            addInfoComdyCode.Recaddr(acm_ins.Oid())
            addInfoComdyCode.FieldValue(comdycode)
            addInfoComdyCode.Commit()
        else:
            if acm_ins.AdditionalInfo().Commodity_Code().strip() == '':
                acm_ins.AdditionalInfo().Commodity_Code(comdycode)
        

'''
def createEquityIndexInstr(insCcy, insMic, insDesc, insName, localcode):
    insid = ''
    
    prodId = localcode + '@' + insMic
    #print prodId
    insTemplateId = 'Template EquityIndex'     
    ins_template = acm.FInstrument[insTemplateId]
    ins_new = ins_template.Clone()
    ins_new.Name(prodId)
    ins_new.Currency(insCcy)
    ins_new.Commit()
    
    # Create Stock Additional Infos
    CreateInsAdditionalInfo(ins_new.Name(), insMic, insDesc, insName, localcode)
    
    # Create BB_TICKER alias    
    bb_ticker = localcode + ' Index'
    if bb_ticker != '':
        createInstrumentAlias(ins_new.Name(), 'BB_TICKER', bb_ticker)
    
    insid = ins_new.Name()
    return insid
'''

'''
def map_bb_exch_code(insCcy):
    bb_exch_code = ''
    
    if insCcy == 'HKD':
        bb_exch_code = 'HK'        
    elif insCcy in ('SGD'):
        bb_exch_code = 'SP'
        
    return bb_exch_code
'''

def map_bb_exch_code(mic):
    bb_exch_code = ''
    
    if mic in ('XHKG','XHKF'):
        bb_exch_code = 'HK'        
    elif mic in ('XSGD'):
        bb_exch_code = 'SP'
        
    return bb_exch_code
    
def getInsidByBBTicker(bb_ticker):
    ael_ins = ael.Instrument[bb_ticker]
    if ael_ins != None:
        return ael_ins.insid.strip()
    else:
        return ''
        
def getTemplateBBTicker(insTemplateId, insType, insULType, insMaturity, insCallPut='CALL', insStrikePrice=0):
    ins_template = acm.FInstrument[insTemplateId]
    # BB_TICKER alias
    bb_ticker = ''
    for aliase in ins_template.Aliases():
        if aliase.Type().Name() == 'BB_TICKER':
            bb_ticker = aliase.Alias()
            if insType == 'FUTURE':
                yy = str(getYear('Future/Forward', insMaturity))
                bb_ticker = bb_ticker.replace('my', getMonthCode('Future/Forward', False, insMaturity)+yy[1:2])
            elif insType == 'OPTION':
                bb_ticker = bb_ticker.replace('mm/dd/yy', ael.date(insMaturity).to_string('%m/%d/%Y'))
                if insCallPut == 'CALL' or insCallPut == 'C':
                    bb_ticker = bb_ticker.replace('[e]', 'C')
                else:
                    bb_ticker = bb_ticker.replace('[e]', 'P')
                if insULType == 'INDEX':
                    bb_ticker = bb_ticker.replace('[x]', str(int(float(insStrikePrice))))
                else:
                    bb_ticker = bb_ticker.replace('[x]', str('{0:.2f}'.format(insStrikePrice)))
            else:
                bb_ticker = ''
    return bb_ticker
    
def formatBBTicker(mic, insCcy, insType, localcode, insMaturity=None, underlying_insid='', insPointValue=0, insULType='', insCallPut='CALL', insStrikePrice='0'):
    bb_ticker = ''
    
    print insType
    if insType in ('STOCK','WARRANT','CBBC'):
        #bb_exch_code = map_bb_exch_code(insCcy)
        print mic
        bb_exch_code = map_bb_exch_code(mic)
        bb_db_code = 'Equity'
        bb_ticker = localcode + ' ' + bb_exch_code + ' ' + bb_db_code                
    elif insType in ('FUTURE'):
        if insULType == 'INDEX':
            insTemplateId = getIndexFutureTemplate(underlying_insid, insPointValue)
            if insTemplateId != '':
                bb_ticker = getTemplateBBTicker(insTemplateId, insType, insULType, insMaturity, insCallPut, insStrikePrice)
        elif insULType == 'STOCK':
            acm_und_ins = acm.FInstrument[underlying_insid]
            if acm_und_ins != None:
                #bb_exch_code = map_bb_exch_code(acm_und_ins.Currency().Name().strip())    
                bb_exch_code = map_bb_exch_code(acm_und_ins.AdditionalInfo().MIC().strip())
                bb_db_code = 'Equity'
                yy = str(getYear('Future/Forward', insMaturity))
                if acm_und_ins.AdditionalInfo().Local_Exchange_Code() != None:                    
                    bb_ticker = acm_und_ins.AdditionalInfo().Local_Exchange_Code() + '=' + getMonthCode('Future/Forward', False, insMaturity) + yy[1:2] + ' ' + bb_exch_code + ' ' + bb_db_code
            
    elif insType in ('OPTION'):
        if insULType == 'INDEX':
            insTemplateId = getIndexOptionTemplate(underlying_insid, insPointValue)
            if insTemplateId != '':
                bb_ticker = getTemplateBBTicker(insTemplateId, insType, insULType, insMaturity, insCallPut, insStrikePrice)
        elif insULType == 'STOCK':      
            acm_und_ins = acm.FInstrument[underlying_insid]
            if acm_und_ins != None:
                #bb_exch_code = map_bb_exch_code(acm_und_ins.Currency().Name().strip())    
                bb_exch_code = map_bb_exch_code(acm_und_ins.AdditionalInfo().MIC().strip())
                bb_db_code = 'Equity'
                if acm_und_ins.AdditionalInfo().Local_Exchange_Code() != None:
                    if insCallPut == 'CALL' or insCallPut == 'C':
                        CP = 'C'
                    else:
                        CP = 'P'
                    bb_ticker = acm_und_ins.AdditionalInfo().Local_Exchange_Code() + ' ' + bb_exch_code + ' ' + ael.date(insMaturity).to_string('%m/%d/%Y') + ' ' + CP + str(insStrikePrice) + ' ' + bb_db_code                    
    #print 'C', bb_ticker
    return bb_ticker
        
      
def createStockInstr(insCcy, insMic, insDesc, insName, localcode):
    insid = ''
    
    #print 'A'
    '''
    bb_ticker = ''
    bb_exch_code = map_bb_exch_code(insCcy)
    bb_db_code = 'Equity'
    bb_ticker = localcode + ' ' + bb_exch_code + ' ' + bb_db_code
    '''
    #bb_ticker = formatBBTicker(insCcy, 'STOCK', localcode)
    bb_ticker = formatBBTicker(insMic, insCcy, 'STOCK', localcode)
    
    if bb_ticker == '':
        return insid
    
    insid = getInsidByBBTicker(bb_ticker)
    if insid != '':
        CreateInsAdditionalInfo(insid, insMic, insDesc, insName, localcode, 'STOCK', '')
        if bb_ticker != '':    
            # Create BB_TICKER alias
            createInstrumentAlias(insid, 'BB_TICKER', bb_ticker)
        return insid
    
    #prodId = localcode + '@' + insMic
    prodId = bb_ticker
    insTemplateId = 'Template Stock'            
    ins_template = acm.FInstrument[insTemplateId]
    ins_new = ins_template.Clone()
    ins_new.Name(prodId)
    ins_new.Currency(insCcy)
    ins_new.Commit()
    
    # Create Stock Additional Infos
    CreateInsAdditionalInfo(ins_new.Name(), insMic, insDesc, insName, localcode, 'STOCK', '')
    
    if bb_ticker != '':    
        # Create BB_TICKER alias
        createInstrumentAlias(ins_new.Name(), 'BB_TICKER', bb_ticker)
    
    insid = ins_new.Name()
    return insid
    
    
def createStockFutureInstr(insCcy, insMic, insDesc, localcode, insMaturity, insPointValue, insName, underlying_insid, insULType, insUnderlying_mktId, insDeliveryType):
    insid = ''
    #prodId = localcode + '@' + insMic
    
    print 'CC', insCcy, 'FUTURE', localcode, insMaturity, underlying_insid, insPointValue, insULType
    #def formatBBTicker(insCcy, insType, localcode, insMaturity=None, underlying_insid='', insPointValue=0, insULType='', insCallPut='CALL', insStrikePrice='0'):

    #bb_ticker = formatBBTicker(insCcy, 'FUTURE', localcode, insMaturity, underlying_insid, insPointValue, insULType)
    bb_ticker = formatBBTicker(insMic, insCcy, 'FUTURE', localcode, insMaturity, underlying_insid, insPointValue, insULType)
    
    if bb_ticker == '':
        return insid
    
    insid = getInsidByBBTicker(bb_ticker)
    if insid != '':
        CreateInsAdditionalInfo(insid, insMic, insDesc, insName, localcode, 'FUTURE', insUnderlying_mktId)
        if bb_ticker != '':    
            # Create BB_TICKER alias
            createInstrumentAlias(insid, 'BB_TICKER', bb_ticker)
        return insid
    
    prodId = bb_ticker
    insTemplateId = 'Template Future'    
    ins_template = acm.FInstrument[insTemplateId]
    ins_new = ins_template.Clone()
    ins_new.Generic(False) 
    ins_new.Name(prodId)
    ins_new.ExpiryDate(insMaturity)
    ins_new.ContractSize(float(insPointValue))
    ins_new.Currency(insCcy)
    ins_new.Underlying = acm.FInstrument[underlying_insid]
    
    # Underlying Type
    insUnderlyingInsType = ins_new.Underlying().InsType()
    ins_new.ValuationGrpChlItem('Listed Equity Future')
    if insDeliveryType.upper() == 'CASH':
        ins_new.SettlementType('Cash')
    else:
        ins_new.SettlementType('Physical Delivery')
    ins_new.Commit()    
        
    # Create Future Additional Infos
    CreateInsAdditionalInfo(ins_new.Name(), insMic, insDesc, insName, localcode, 'FUTURE', insUnderlying_mktId)
        
    # Create BB_TICKER alias    
    if bb_ticker != '':
        createInstrumentAlias(ins_new.Name(), 'BB_TICKER', bb_ticker)
    
    insid = ins_new.Name()
    return insid
    
def getIndexFutureTemplate(underlying_insid, insPointValue):
    strSql = """
            select i.insid
            from instrument i, instrument ui
            where i.instype = 'Future/Forward'
            and i.generic = 'Yes'
            and i.und_insaddr = ui.insaddr
            and ui.insid = '%s'
            and i.contr_size = %s
            """ % (underlying_insid, insPointValue)
            
    print strSql
    rs = ael.asql(strSql)
    
    insid = ''
    columns, buf = rs
    for table in buf:                        
        for row in table:
            insid = row[0].strip()
            
    return insid
    
def createIndexFutureInstr(insCcy, insMic, insDesc, localcode, insMaturity, insPointValue, insName, underlying_insid, insULType, insUnderlying_mktId):
    insid = ''
    #prodId = localcode + '@' + insMic
        
    #bb_ticker = formatBBTicker(insCcy, 'FUTURE', localcode, insMaturity, underlying_insid, insPointValue, insULType)
    bb_ticker = formatBBTicker(insMic, insCcy, 'FUTURE', localcode, insMaturity, underlying_insid, insPointValue, insULType)
    
    if bb_ticker == '':
        return insid
    
    insid = getInsidByBBTicker(bb_ticker)
    if insid != '':
        CreateInsAdditionalInfo(insid, insMic, insDesc, insName, localcode, 'FUTURE', insUnderlying_mktId)
        if bb_ticker != '':    
            # Create BB_TICKER alias
            createInstrumentAlias(insid, 'BB_TICKER', bb_ticker)
        return insid
    
    #prodId = localcode + '@' + insMic
    prodId = bb_ticker
    
    
    insTemplateId = getIndexFutureTemplate(underlying_insid, insPointValue)
    if insTemplateId == '':
        return insid
        
    ins_template = acm.FInstrument[insTemplateId]
    ins_new = ins_template.Clone()
    ins_new.Generic(False) 
    ins_new.Name(prodId)
    ins_new.ExpiryDate(insMaturity)
    ins_new.ContractSize(float(insPointValue))
    ins_new.Currency(insCcy)
    ins_new.Underlying = acm.FInstrument[underlying_insid]
    
    # Underlying Type
    insUnderlyingInsType = ins_new.Underlying().InsType()
    ins_new.ValuationGrpChlItem('Listed Index Future')
    
    # BB_TICKER alias
    if bb_ticker != '':
        for aliase in ins_new.Aliases():
            if aliase.Type().Name() == 'BB_TICKER':
                aliase.Alias(bb_ticker)
                break
    
    #if bb_ticker != '':
    #    createInstrumentAlias(ins_new.Name(), 'BB_TICKER', bb_ticker, True)
        
    ins_new.Commit()    
        
    # Create Future Additional Infos
    CreateInsAdditionalInfo(ins_new.Name(), insMic, insDesc, insName, localcode, 'FUTURE', insUnderlying_mktId)
        
    insid = ins_new.Name()
    return insid
    
def createCBBCInstr(insMaturity, insCcy, insPointValue, insDeliveryType, insOptionType, insExecType, insStrike, insMic, 
                    insDesc, localcode, insBullBear, insBarrier, insIssueSize, insIssueDate, insBarrierType, issuer_ptyid, insName, ins_underlying_insid):
    insid = ''
    #prodId = localcode + '@' + insMic
    
    #bb_ticker = formatBBTicker(insCcy, 'CBBC', localcode, insMaturity, ins_underlying_insid, insPointValue)
    bb_ticker = formatBBTicker(insMic, insCcy, 'CBBC', localcode, insMaturity, ins_underlying_insid, insPointValue)
    
    if bb_ticker == '':
        return insid
    
    prodId = bb_ticker
    insid = getInsidByBBTicker(bb_ticker)
    if insid != '':
        CreateInsAdditionalInfo(insid, insMic, insDesc, insName, localcode, 'CBBC', '')
        if bb_ticker != '':    
            # Create BB_TICKER alias
            createInstrumentAlias(insid, 'BB_TICKER', bb_ticker)
        return insid
    
    insTemplateId = 'Template CBBC'
    ins_template = acm.FInstrument[insTemplateId]
    ins_new = ins_template.Clone()
    ins_new.Name(prodId)
    ins_new.Underlying(ins_underlying_insid)        
    ins_new.ExpiryDate(insMaturity)
    ins_new.Currency(insCcy)
    insOptionType = insOptionType.upper()
    if insOptionType == 'CALL' or insOptionType == 'C':
        ins_new.IsCallOption(True)
    else:
        ins_new.IsCallOption(False)
    
    if insExecType.upper() == 'EUROPEAN' or insExecType.upper() == 'E':
        ins_new.ExerciseType('European')
    else:
        ins_new.ExerciseType('American')
    if insDeliveryType.upper() == 'CASH' or insDeliveryType.upper() == 'C':
        ins_new.SettlementType('Cash')
    else:
        ins_new.SettlementType('Physical Delivery')    
        
    ins_new.ContractSize(float(insPointValue))
    ins_new.StrikeCurrency(insCcy)
    ins_new.StrikePrice(float(insStrike))    
    ins_new.ValuationGrpChlItem('CBBC Warrant')    
    ins_new.Barrier(float(insBarrier))    
    
    if insIssueSize != '':
        ins_new.TotalIssued(float(insIssueSize))
    
    if insIssueDate != '':
        ins_new.IssueDay(insIssueDate)
            
    insBarrierType = insBarrierType.upper()
    for exotic in ins_new.Exotics():
        if insBarrierType == '':
            if insBullBear == 'BULL' and (insOptionType == 'CALL' or insOptionType == 'C'):
                exotic.BarrierOptionType('Up & Out')
            else:
                exotic.BarrierOptionType('Down & Out')
        else:
            if insBarrierType == 'UPANDOUT':
                exotic.BarrierOptionType('Up & Out')
            elif insBarrierType == 'DOWNANDOUT':
                exotic.BarrierOptionType('Down & Out')
            elif insBarrierType == 'DOWNANDIN':
                exotic.BarrierOptionType('Down & In')
            else:
                exotic.BarrierOptionType('UP & In')
                
    if issuer_ptyid != '':
        ins_new.Issuer(issuer_ptyid)
    
    ins_new.Commit()
    
    # Create Additional Infos
    CreateInsAdditionalInfo(ins_new.Name(), insMic, insDesc, insName, localcode, 'CBBC', '')
    
    if bb_ticker != '':
        createInstrumentAlias(ins_new.Name(), 'BB_TICKER', bb_ticker)
        
    insid = ins_new.Name()
    return insid
    
def createWarrantInstr(insMaturity, insCcy, insPointValue, insDeliveryType, insOptionType, insExecType, insStrike, 
                    insMic, insDesc, localcode, insIssueSize, insIssueDate, issuer_ptyid, insName, ins_underlying_insid):
    insid = ''
    
    #bb_ticker = formatBBTicker(insCcy, 'WARRANT', localcode, insMaturity, ins_underlying_insid, insPointValue)
    bb_ticker = formatBBTicker(insMic, insCcy, 'WARRANT', localcode, insMaturity, ins_underlying_insid, insPointValue)
    
    if bb_ticker == '':
        return insid
    
    insid = getInsidByBBTicker(bb_ticker)
    if insid != '':
        CreateInsAdditionalInfo(insid, insMic, insDesc, insName, localcode, 'WARRANT', '')
        if bb_ticker != '':    
            # Create BB_TICKER alias
            createInstrumentAlias(insid, 'BB_TICKER', bb_ticker)
        return insid
    
    prodId = bb_ticker
    
    insTemplateId = 'Template Warrant'
    ins_template = acm.FInstrument[insTemplateId]
    ins_new = ins_template.Clone()
    ins_new.Name(prodId)
    ins_new.Underlying(ins_underlying_insid)    
    ins_new.ExpiryDate(insMaturity)
    ins_new.Currency(insCcy)
    if insOptionType.upper() == 'CALL' or insOptionType.upper() == 'C':
        ins_new.IsCallOption(True)
    else:
        ins_new.IsCallOption(False)
    
    if insExecType.upper() == 'EUROPEAN' or insExecType.upper() == 'E':
        ins_new.ExerciseType('European')
    else:
        ins_new.ExerciseType('American')
    if insDeliveryType.upper() == 'CASH':
        ins_new.SettlementType('Cash')
    else:
        ins_new.SettlementType('Physical Delivery')
        
    if insIssueSize != '':
         ins_new.TotalIssued(float(insIssueSize))
         
    if insIssueDate != '':
        ins_new.IssueDay(insIssueDate)
        
    ins_new.ContractSize(float(insPointValue))
    ins_new.StrikeCurrency(insCcy)
    ins_new.StrikePrice(float(insStrike))    
    ins_new.ValuationGrpChlItem('Listed Warrant')   

    if issuer_ptyid != '':
        ins_new.Issuer(issuer_ptyid)
    
    ins_new.Commit()
    
    # Create Additional Infos
    CreateInsAdditionalInfo(ins_new.Name(), insMic, insDesc, insName, localcode, 'WARRANT', '')
        
    if bb_ticker != '':
        createInstrumentAlias(ins_new.Name(), 'BB_TICKER', bb_ticker)
        
    insid = ins_new.Name()
    return insid
    
def getIndexOptionTemplate(underlying_insid, insPointValue):
    strSql = """
            select i.insid
            from instrument i, instrument ui
            where i.instype = 'Option'
            and i.generic = 'Yes'
            and i.und_insaddr = ui.insaddr
            and ui.insid = '%s'
            and i.contr_size = %s
            """ % (underlying_insid, insPointValue)
            
    print strSql
    rs = ael.asql(strSql)
    
    insid = ''
    columns, buf = rs
    for table in buf:                        
        for row in table:
            insid = row[0].strip()
            
    return insid
    
def createIndexOptionInstr(insMaturity, insCcy, insPointValue, insDeliveryType, insOptionType, insExecType, insStrike, insMic, insDesc, localcode, insName, insULType, ins_underlying_insid, insUnderlying_mktId):
    insid = ''
    #prodId = localcode + '@' + insMic
    
    #bb_ticker = formatBBTicker(insCcy, 'OPTION', localcode, insMaturity, ins_underlying_insid, insPointValue, insULType, insOptionType, insStrike)    
    bb_ticker = formatBBTicker(insMic, insCcy, 'OPTION', localcode, insMaturity, ins_underlying_insid, insPointValue, insULType, insOptionType, insStrike)    
    if bb_ticker == '':
        return insid
    
    prodId = bb_ticker
    insid = getInsidByBBTicker(bb_ticker)
    if insid != '':
        CreateInsAdditionalInfo(insid, insMic, insDesc, insName, localcode, 'OPTION', insUnderlying_mktId)
        if bb_ticker != '':    
            # Create BB_TICKER alias
            createInstrumentAlias(insid, 'BB_TICKER', bb_ticker)
        return insid
    
    insTemplateId = getIndexOptionTemplate(ins_underlying_insid, insPointValue)
    if insTemplateId == '':
        return insid
    
    ins_template = acm.FInstrument[insTemplateId]
    ins_new = ins_template.Clone()
    ins_new.Generic(False)
    ins_new.Name(prodId)
    ins_new.Underlying(ins_underlying_insid)    
    ins_new.ExpiryDate(insMaturity)
    ins_new.Currency(insCcy)
    print 'insOptionType', insOptionType
    if insOptionType.upper() == 'CALL' or insOptionType.upper() == 'C':
        ins_new.IsCallOption(True)
    else:
        ins_new.IsCallOption(False)
        
    if insExecType.upper() == 'EUROPEAN' or insExecType.upper() == 'E':
        ins_new.ExerciseType('European')
    else:
        ins_new.ExerciseType('American')
    if insDeliveryType.upper() == 'CASH' or insDeliveryType.upper() == 'C':
        ins_new.SettlementType('Cash')
    else:
        ins_new.SettlementType('Physical Delivery')
    
    ins_new.StrikeCurrency(insCcy)
    ins_new.StrikePrice(float(insStrike))
    ins_new.ContractSize(float(insPointValue))
    
    # Underlying Type
    insUnderlyingInsType = ins_new.Underlying().InsType()
    ins_new.ValuationGrpChlItem('Listed Index Option')
    
    # BB_TICKER alias
    '''
    for aliase in ins_new.Aliases():
        if aliase.Type().Name() == 'BB_TICKER':
            bb_ticker = aliase.Alias()
            #print bb_ticker, getMonthCode('Option', ins_new.IsCallOption(), insMaturity)
            bb_ticker = bb_ticker.replace('mm/dd/yy', ael.date(insMaturity).to_string('%m/%d/%Y'))
            if ins_new.IsCallOption():
                bb_ticker = bb_ticker.replace('[e]', 'C')
            else:
                bb_ticker = bb_ticker.replace('[e]', 'P')
            bb_ticker = bb_ticker.replace('[x]', str(int(ins_new.StrikePrice())))
            #print 'B1', bb_ticker
            aliase.Alias(bb_ticker)
            break
    '''
    
    # BB_TICKER alias
    if bb_ticker != '':
        for aliase in ins_new.Aliases():
            if aliase.Type().Name() == 'BB_TICKER':
                aliase.Alias(bb_ticker)
                break
    
    ins_new.Commit()    
    
    # Create Additional Infos
    CreateInsAdditionalInfo(ins_new.Name(), insMic, insDesc, insName, localcode, 'OPTION', insUnderlying_mktId)
        
    '''
    bb_ticker = ''
    if insCcy == 'HKD':
        bb_ticker = localcode + ' HK Option'
    elif insCcy in ('CNY', 'CNH'):
        bb_ticker = localcode + ' CN Option'
    if bb_ticker != '':
        createInstrumentAlias(ins_new.Name(), 'BB_TICKER', bb_ticker)
    '''
    insid = ins_new.Name()
    return insid    

def createStockOptionInstr(insMaturity, insCcy, insPointValue, insDeliveryType, insOptionType, insExecType, insStrike, insMic, insDesc, localcode, insName, insULType, ins_underlying_insid, insUnderlying_mktId):
    insid = ''
    #prodId = localcode + '@' + insMic
    
    print 'I1', insCcy, 'OPTION', localcode, insMaturity, ins_underlying_insid, insPointValue, insULType, insOptionType, insStrike
    #bb_ticker = formatBBTicker(insCcy, 'OPTION', localcode, insMaturity, ins_underlying_insid, insPointValue, insULType, insOptionType, insStrike)    
    bb_ticker = formatBBTicker(insMic, insCcy, 'OPTION', localcode, insMaturity, ins_underlying_insid, insPointValue, insULType, insOptionType, insStrike)    
    print 'I2', bb_ticker
    if bb_ticker == '':
        return insid
        
    prodId = bb_ticker
    insid = getInsidByBBTicker(bb_ticker)
    if insid != '':
        CreateInsAdditionalInfo(insid, insMic, insDesc, insName, localcode, 'OPTION', insUnderlying_mktId)
        if bb_ticker != '':    
            # Create BB_TICKER alias
            createInstrumentAlias(insid, 'BB_TICKER', bb_ticker)
        return insid
    
    print 'I3'
    insTemplateId = 'Template Option'
    ins_template = acm.FInstrument[insTemplateId]
    ins_new = ins_template.Clone()
    ins_new.Generic(False)
    ins_new.Name(prodId)
    ins_new.Underlying(ins_underlying_insid)    
    ins_new.ExpiryDate(insMaturity)
    ins_new.Currency(insCcy)
    print 'I'
    if insOptionType.upper() == 'CALL' or insOptionType.upper() == 'C':
        ins_new.IsCallOption(True)
    else:
        ins_new.IsCallOption(False)
    print 'J'
    
    if insExecType.upper() == 'EUROPEAN' or insExecType.upper() == 'E':
        ins_new.ExerciseType('European')
    else:
        ins_new.ExerciseType('American')
    if insDeliveryType.upper() == 'CASH' or insDeliveryType.upper() == 'C':
        ins_new.SettlementType('Cash')
    else:
        ins_new.SettlementType('Physical Delivery')
    
    ins_new.StrikeCurrency(insCcy)
    ins_new.StrikePrice(float(insStrike))
    ins_new.ContractSize(float(insPointValue))
    
    # Underlying Type
    insUnderlyingInsType = ins_new.Underlying().InsType()
    ins_new.ValuationGrpChlItem('Listed Equity Option')
        
    ins_new.Commit()    
    
    # Create Additional Infos
    CreateInsAdditionalInfo(ins_new.Name(), insMic, insDesc, insName, localcode, 'OPTION', insUnderlying_mktId)
        
    if bb_ticker != '':
        createInstrumentAlias(ins_new.Name(), 'BB_TICKER', bb_ticker)
        
    insid = ins_new.Name()
    return insid

def getInstrument(tradeId, way, qty, price, insLocalCode,
                trdCcy, insMic, insCcy, insDesc, insProdType,
                insMaturity, insPointValue, insStrike, insOptionType,
                insExecType, insBullBear, insBarrier, insOtc, insDeliveryType,
                insUlLocalCode, insULProdType, insULMic, insULCcy, insULDesc,
                trdChannel, insIssueSize, insIssueDate, insBarrierType, issuer_ptyid, 
                insName, insULName, insUnderlying_mktId, new_arr_ins, errdict):
    newIns = False
    trd_insid = ''
    
    insProdType = insProdType.upper()    
    insULProdType = insULProdType.upper()
    insOptionType = insOptionType.upper()
    insExecType = insExecType.upper()
    insBullBear = insBullBear.upper()
    insOtc = insOtc.upper()
    insDeliveryType = insDeliveryType.upper()    
    if insProdType == 'STOCK':      
        ins_insid = getInstrumentByMapping(insLocalCode, insMic)
        if ins_insid == '':            
            ins_new_insid = createStockInstr(insCcy, insMic, insDesc, insName, insLocalCode)            
            if ins_new_insid != '':
                trd_insid = ins_new_insid
                new_arr_ins.append(ins_new_insid)
                newIns = True
        else:
            acm_ins = acm.FInstrument[ins_insid]
            CreateInsAdditionalInfo(acm_ins.Name(), insMic, insDesc, insName, insLocalCode, insProdType, '')
            #bb_ticker = formatBBTicker(insCcy, insProdType, insLocalCode)
            bb_ticker = formatBBTicker(insMic, insCcy, insProdType, insLocalCode)
            if bb_ticker != '':
                createInstrumentAlias(ins_insid, 'BB_TICKER', bb_ticker)            
            trd_insid = ins_insid
            newIns = False        
    elif insProdType == 'FUTURE':
        ins_insid = getInstrumentByMapping(insLocalCode, insMic)
        if ins_insid == '':            
            # get Underlying
            ins_underlying_insid = getInstrumentByMapping(insUlLocalCode, insULMic)
            if ins_underlying_insid == '':              
                if insULProdType == 'STOCK':
                    ins_underlying_insid = createStockInstr(insULCcy, insULMic, insULDesc, insULName, insUlLocalCode)                    
                elif insULProdType == 'INDEX':
                    ins_underlying_insid = ''
                    #ins_underlying_insid = createEquityIndexInstr(insULCcy, insULMic, insULDesc, insULName, insUlLocalCode)
                                        
                if ins_underlying_insid != '':
                    new_arr_ins.append(ins_underlying_insid)
            else:
                acm_ins = acm.FInstrument[ins_underlying_insid]
                CreateInsAdditionalInfo(acm_ins.Name(), insULMic, insULDesc, insULName, insUlLocalCode, insULProdType, '')
                #ul_bb_ticker = formatBBTicker(insULCcy, insULProdType, insUlLocalCode)
                ul_bb_ticker = formatBBTicker(insULMic, insULCcy, insULProdType, insUlLocalCode)
                if ul_bb_ticker != '':
                    createInstrumentAlias(ins_underlying_insid, 'BB_TICKER', ul_bb_ticker)
            
            # Create Future
            if ins_underlying_insid != '':
                ins_new_insid = ''                
                if insULProdType == 'STOCK':
                    ins_new_insid = createStockFutureInstr(insCcy, insMic, insDesc, insLocalCode, insMaturity, insPointValue, insName, ins_underlying_insid, insULProdType, insUnderlying_mktId, insDeliveryType)                                    
                elif insULProdType == 'INDEX':                    
                    ins_new_insid = createIndexFutureInstr(insCcy, insMic, insDesc, insLocalCode, insMaturity, insPointValue, insName, ins_underlying_insid, insULProdType, insUnderlying_mktId)                                    
                if ins_new_insid != '':
                    trd_insid = ins_new_insid
                    new_arr_ins.append(ins_new_insid)
                    newIns = True 
        else:
            acm_ins = acm.FInstrument[ins_insid]
            CreateInsAdditionalInfo(acm_ins.Name(), insMic, insDesc, insName, insLocalCode, insProdType, insUnderlying_mktId)
            #bb_ticker = formatBBTicker(insCcy, insProdType, insLocalCode, insMaturity, acm_ins.Underlying().Name(), acm_ins.ContractSize(), insULProdType)
            bb_ticker = formatBBTicker(insMic, insCcy, insProdType, insLocalCode, insMaturity, acm_ins.Underlying().Name(), acm_ins.ContractSize(), insULProdType)
            if bb_ticker != '':
                createInstrumentAlias(ins_insid, 'BB_TICKER', bb_ticker)
            trd_insid = ins_insid
            newIns = False
    
    elif insProdType == 'OPTION':
        ins_insid = getInstrumentByMapping(insLocalCode, insMic)
        if ins_insid == '':
            # get Underlying
            ins_underlying_insid = getInstrumentByMapping(insUlLocalCode, insULMic)
            if ins_underlying_insid == '': 
                if insULProdType == 'STOCK':
                    ins_underlying_insid = createStockInstr(insULCcy, insULMic, insULDesc, insULName, insUlLocalCode)                                    
                elif insULProdType == 'INDEX':
                    ins_underlying_insid = ''
                    #ins_underlying_insid = createEquityIndexInstr(insULCcy, insULMic, insULDesc, insULName, insUlLocalCode)  
              
                if ins_underlying_insid != '':
                    new_arr_ins.append(ins_underlying_insid)
            else:
                acm_ins = acm.FInstrument[ins_underlying_insid]
                CreateInsAdditionalInfo(acm_ins.Name(), insULMic, insULDesc, insULName, insUlLocalCode, insULProdType, '')
                #ul_bb_ticker = formatBBTicker(insULCcy, insULProdType, insUlLocalCode)
                ul_bb_ticker = formatBBTicker(insULMic, insULCcy, insULProdType, insUlLocalCode)
                if ul_bb_ticker != '':
                    createInstrumentAlias(ins_underlying_insid, 'BB_TICKER', ul_bb_ticker)
            
            # Create Option
            if ins_underlying_insid != '':
                ins_new_insid = '' 
                if insULProdType == 'STOCK':
                    print 'G'
                    ins_new_insid = createStockOptionInstr(insMaturity, insCcy, insPointValue, insDeliveryType, insOptionType, insExecType, insStrike, insMic, insDesc, insLocalCode, insName, insULProdType, ins_underlying_insid, insUnderlying_mktId)
                    print 'H'
                elif insULProdType == 'INDEX':
                    ins_new_insid = createIndexOptionInstr(insMaturity, insCcy, insPointValue, insDeliveryType, insOptionType, insExecType, insStrike, insMic, insDesc, insLocalCode, insName, insULProdType, ins_underlying_insid, insUnderlying_mktId)                                        
                if ins_new_insid != '':
                    trd_insid = ins_new_insid
                    new_arr_ins.append(ins_new_insid)
                    newIns = True
        else:
            acm_ins = acm.FInstrument[ins_insid]
            CreateInsAdditionalInfo(acm_ins.Name(), insMic, insDesc, insName, insLocalCode, insProdType, insUnderlying_mktId)
            #bb_ticker = formatBBTicker(insCcy, insProdType, insLocalCode, insMaturity, acm_ins.Underlying().Name(), acm_ins.ContractSize(), insULProdType, insOptionType, insStrike)
            bb_ticker = formatBBTicker(insMic, insCcy, insProdType, insLocalCode, insMaturity, acm_ins.Underlying().Name(), acm_ins.ContractSize(), insULProdType, insOptionType, insStrike)
            if bb_ticker != '':
                createInstrumentAlias(ins_insid, 'BB_TICKER', bb_ticker)                
            trd_insid = ins_insid
            newIns = False        
    elif insProdType == 'WARRANT':
        ins_insid = getInstrumentByMapping(insLocalCode, insMic)
        if ins_insid == '':
            ins_underlying_insid = getInstrumentByMapping(insUlLocalCode, insULMic)
            if ins_underlying_insid == '':
                # Create Underlying Stock
                if insULProdType == 'STOCK':                    
                    ins_underlying_insid = createStockInstr(insULCcy, insULMic, insULDesc, insULName, insUlLocalCode)                    
                elif insULProdType == 'INDEX':
                    ins_underlying_insid = ''
                    #ins_underlying_insid = createEquityIndexInstr(insULCcy, insULMic, insULDesc, insULName, insUlLocalCode)
                
                if ins_underlying_insid != '':
                    new_arr_ins.append(ins_underlying_insid)                    
            else:
                acm_ins = acm.FInstrument[ins_underlying_insid]
                CreateInsAdditionalInfo(acm_ins.Name(), insULMic, insULDesc, insULName, insUlLocalCode, insULProdType, '')
                #ul_bb_ticker = formatBBTicker(insULCcy, insULProdType, insUlLocalCode)
                ul_bb_ticker = formatBBTicker(insULMic, insULCcy, insULProdType, insUlLocalCode)
                if ul_bb_ticker != '':
                    createInstrumentAlias(ins_underlying_insid, 'BB_TICKER', ul_bb_ticker)
                    
            # Create Warrant
            if ins_underlying_insid != '':
                print 'A'
                ins_new_insid = createWarrantInstr(insMaturity, insCcy, insPointValue, insDeliveryType, insOptionType, \
                                insExecType, insStrike, insMic, insDesc, insLocalCode, insIssueSize, insIssueDate, \
                                issuer_ptyid, insName, ins_underlying_insid)    

                print 'B'
                if ins_new_insid != '':
                    trd_insid = ins_new_insid
                    new_arr_ins.append(ins_new_insid)
                    newIns = True                
        else:
            acm_ins = acm.FInstrument[ins_insid]
            CreateInsAdditionalInfo(acm_ins.Name(), insMic, insDesc, insName, insLocalCode, insProdType, '')
            #bb_ticker = formatBBTicker(insCcy, insProdType, insLocalCode)
            bb_ticker = formatBBTicker(insMic, insCcy, insProdType, insLocalCode)
            if bb_ticker != '':
                createInstrumentAlias(ins_insid, 'BB_TICKER', bb_ticker)  
                
            trd_insid = ins_insid
            newIns = False  
    elif insProdType == 'CBBC':
        ins_insid = getInstrumentByMapping(insLocalCode, insMic)
        if ins_insid == '':
            ins_underlying_insid = getInstrumentByMapping(insUlLocalCode, insULMic)
            if ins_underlying_insid == '':
                # Create Underlying Stock
                if insULProdType == 'STOCK':
                    ins_underlying_insid = createStockInstr(insULCcy, insULMic, insULDesc, insULName, insUlLocalCode)                 
                elif insULProdType == 'INDEX':
                    ins_underlying_insid = ''
                    #ins_underlying_insid = createEquityIndexInstr(insULCcy, insULMic, insULDesc, insULName, insUlLocalCode)
                
                if ins_underlying_insid != '':
                    new_arr_ins.append(ins_underlying_insid)
            else:
                acm_ins = acm.FInstrument[ins_underlying_insid]
                CreateInsAdditionalInfo(acm_ins.Name(), insULMic, insULDesc, insULName, insUlLocalCode, insULProdType, '')
                #ul_bb_ticker = formatBBTicker(insULCcy, insULProdType, insUlLocalCode)
                ul_bb_ticker = formatBBTicker(insULMic, insULCcy, insULProdType, insUlLocalCode)
                if ul_bb_ticker != '':
                    createInstrumentAlias(ins_underlying_insid, 'BB_TICKER', ul_bb_ticker)
                    
            # Create CBBC
            if ins_underlying_insid != '':
                ins_new_insid = createCBBCInstr(insMaturity, insCcy, insPointValue, insDeliveryType, insOptionType, \
                                insExecType, insStrike, insMic, insDesc, insLocalCode, insBullBear, insBarrier, \
                                insIssueSize, insIssueDate, insBarrierType, issuer_ptyid, insName, ins_underlying_insid)
                if ins_new_insid != '':
                    trd_insid = ins_new_insid
                    new_arr_ins.append(ins_new_insid)
                    newIns = True                
        else:
            acm_ins = acm.FInstrument[ins_insid]
            CreateInsAdditionalInfo(acm_ins.Name(), insMic, insDesc, insName, insLocalCode, insProdType, '')
            #bb_ticker = formatBBTicker(insCcy, insProdType, insLocalCode)
            bb_ticker = formatBBTicker(insMic, insCcy, insProdType, insLocalCode)
            if bb_ticker != '':
                createInstrumentAlias(ins_insid, 'BB_TICKER', bb_ticker)  
                
            trd_insid = ins_insid
            newIns = False        
        
    return trd_insid, newIns


def createTrade(asofdate, trd_insid, tradeId, way, qty, price, trdCcy, DEFAULT_PF, DEFAULT_CPTY, \
                DEFAULT_BKR, DEFAULT_ACQ, DEFAULT_STATUS, DEFAULT_TRADER, channel, \
                trdAcquirer, trdCounterparty, trdPortfolio, trd_td, trd_vd, mss_acc_id, trd_ae_aces_grp_cde, \
                fo_userid, timestamp, errdict):
    #return 1234, 'Success'
    
    trdnbr = -1
    tradeSituation = 'Fail'
    
    print 'trdPortfolio', trdPortfolio
    print 'trdCounterparty', trdCounterparty
    print 'trdAcquirer', trdAcquirer
    
    # Portfolio
    if trdPortfolio == '':        
        pf = ael.Portfolio[DEFAULT_PF]
        #print 'louis1', DEFAULT_PF, pf
        if pf != None:
            prfid = pf.prfid.strip()
        else:
            prfid = ''
    else:
        prfid = trdPortfolio

    #print 'prfid100', prfid
    #return false

    # Counterparty
    if trdCounterparty == '':
        ptyid = getCounterparty(DEFAULT_CPTY)
    else:
        ptyid = trdCounterparty
    
    # Broker
    #broker_ptyid = getBroker(DEFAULT_BKR)
    
    # Acquirer
    if trdAcquirer == '':
        acq_ptyid = getAcquirer(DEFAULT_ACQ)
    else:
        acq_ptyid = trdAcquirer
        
    # B/S
    if way.upper() in ('B', 'S'):
        buysell = way.upper()
    else:
        buysell = ''
        
    # Instrument
    ael_ins = ael.Instrument[trd_insid]
    if ael_ins != None:
        insid = ael_ins.insid.strip()
    else:
        insid = ''
        
    curr = ael.Instrument[trdCcy]
    if curr != None:
        curr_insid = curr.insid.strip()
    else:
        curr_insid = ''
        
    #Trader
    traderId = DEFAULT_TRADER
    
    if insid != '' and prfid != '' and curr_insid != '' and ptyid != '' and acq_ptyid != '' \
        and buysell != '' and traderId != '':
        ael_ins = ael.Instrument[insid]
        ael_trd = ael.Trade.new(ael_ins)
        ael_trd.prfnbr = ael.Portfolio[prfid]        
        ael_trd.acquirer_ptynbr = ael.Party[acq_ptyid]
        ael_trd.counterparty_ptynbr = ael.Party[ptyid]
        #ael_trd.broker_ptynbr = ael.Party[broker_ptyid]
        ael_trd.curr = ael.Instrument[curr_insid]
        if trd_td == '':
            # Horizon
            #td = ael.date(asofdate).to_ymd()
            yy = timestamp[0:4]
            mm = timestamp[4:6]
            dd = timestamp[6:8]
            hh = timestamp[9:11]
            mi = timestamp[11:13]
            ss = timestamp[13:15]
            td_tm = datetime.datetime(int(yy), int(mm), int(dd), int(hh), int(mi), int(ss))
        else:
            # MSS
            td = ael.date(trd_td).to_ymd()
            print td
            td_tm = datetime.datetime(td[0], td[1], td[2], 0, 0, 0)
        print td_tm
        ael_trd.time = int(time.mktime(td_tm.timetuple()))
        # use instrument currency calendar to skip holiday
        print 'time', ael_trd.time
        
        if trd_vd == '':
            if trd_td == '':
                ael_trd.value_day = ael.date(asofdate).add_banking_day(ael_ins.curr, ael_ins.spot_banking_days_offset)
            else:
                ael_trd.value_day = ael.date(trd_td).add_banking_day(ael_ins.curr, ael_ins.spot_banking_days_offset)
        else:
            ael_trd.value_day = ael.date(trd_vd)
            
        print 'time', ael_trd.value_day
        ael_trd.acquire_day = ael_trd.value_day
        if way == 'B':
            ael_trd.quantity = abs(float(qty))
        else:
            ael_trd.quantity = -abs(float(qty))
        ael_trd.price = float(price)        
        ael_trd.premium = quoteTo(ael_ins, ael_trd.acquire_day, ael_ins.quote_type, ael_trd.price) *  ael_trd.quantity  
        ael_trd.status = DEFAULT_STATUS
        ael_trd.type = 'Normal'
        if tradeId.strip() != '':
            FOTradeIdAddinfo = ael.AdditionalInfo.new(ael_trd)
            FOTradeIdAddinfo.addinf_specnbr = 'FO Trade Id'
            FOTradeIdAddinfo.value = formatFOTradeId(tradeId, channel) 
            
        FOSystemAddinfo = ael.AdditionalInfo.new(ael_trd)
        FOSystemAddinfo.addinf_specnbr = 'Trade Source'
        FOSystemAddinfo.value = channel
                
        if mss_acc_id.strip() != '':
            MSSACCAddinfo = ael.AdditionalInfo.new(ael_trd)
            MSSACCAddinfo.addinf_specnbr = 'MSS_Account'
            MSSACCAddinfo.value = mss_acc_id
            
        if channel == 'Horizon':
            #print 'Z', prfid, ael_ins.insid.strip()
            mss_acc_id = mapMssAccCode(prfid, ael_ins.insid.strip())
            #print 'Z1', mss_acc_id
            if mss_acc_id.strip() != '':
                MSSACCAddinfo = ael.AdditionalInfo.new(ael_trd)
                MSSACCAddinfo.addinf_specnbr = 'MSS_Account'
                MSSACCAddinfo.value = mss_acc_id
        
        if trd_ae_aces_grp_cde.strip() != '':
            if channel == 'Horizon':
                HorizonPfAddinfo = ael.AdditionalInfo.new(ael_trd)
                HorizonPfAddinfo.addinf_specnbr = 'Horizon Portfolio'
                HorizonPfAddinfo.value = trd_ae_aces_grp_cde                
            else:                
                AEACESAddinfo = ael.AdditionalInfo.new(ael_trd)
                AEACESAddinfo.addinf_specnbr = 'AE_Aces_Code'
                AEACESAddinfo.value = trd_ae_aces_grp_cde
                
        if fo_userid.strip() != '':
            FOUserIdAddinfo = ael.AdditionalInfo.new(ael_trd)
            FOUserIdAddinfo.addinf_specnbr = 'Horizon User Id'
            FOUserIdAddinfo.value = fo_userid                    
        
        ael_trd.trader_usrnbr = ael.User[traderId]        
        ael_trd.commit()
        ael.poll()        
        trdnbr = ael_trd.trdnbr
        tradeSituation = 'Success'                
    else:
        if insid == '':            
            errdict = addDictError('Instrument', 'Invalid instrument of trade %s' % (tradeId), 'Portfolio=%s, CCY=%s, Counterparty=%s, Acquirer=%s, Way=%s, TraderId=%s, TradeId=%s' % (prfid, curr_insid, ptyid, acq_ptyid, way, traderId, tradeId), errdict)
                        
        if prfid == '':
            errdict = addDictError('Portfolio', 'Invalid portfolio of trade %s' % (tradeId), 'Portfolio=%s, CCY=%s, Counterparty=%s, Acquirer=%s, Way=%s, TraderId=%s, TradeId=%s' % (prfid, curr_insid, ptyid, acq_ptyid, way, traderId, tradeId), errdict)
            
        if ptyid == '':
            errdict = addDictError('Counterparty', 'Invalid counterparty of trade %s' % (tradeId), 'Portfolio=%s, CCY=%s, Counterparty=%s, Acquirer=%s, Way=%s, TraderId=%s, TradeId=%s' % (prfid, curr_insid, ptyid, acq_ptyid, way, traderId, tradeId), errdict)
            
        if curr_insid == '':
            errdict = addDictError('Trade Ccy', 'Invalid trade currency of trade %s' % (tradeId), 'Portfolio=%s, CCY=%s, Counterparty=%s, Acquirer=%s, Way=%s, TraderId=%s, TradeId=%s' % (prfid, curr_insid, ptyid, acq_ptyid, way, traderId, tradeId), errdict)
            
        if acq_ptyid == '':
            errdict = addDictError('Acquirer', 'Invalid acquirer of trade %s' % (tradeId), 'Portfolio=%s, CCY=%s, Counterparty=%s, Acquirer=%s, Way=%s, TraderId=%s, TradeId=%s' % (prfid, curr_insid, ptyid, acq_ptyid, way, traderId, tradeId), errdict)
                        
        if buysell == '':
            errdict = addDictError('BuySell', 'Invalid buy/sell of trade %s' % (tradeId), 'Portfolio=%s, CCY=%s, Counterparty=%s, Acquirer=%s, Way=%s, TraderId=%s, TradeId=%s' % (prfid, curr_insid, ptyid, acq_ptyid, way, traderId, tradeId), errdict)
            
        if traderId == '':
            errdict = addDictError('Trader', 'Invalid trader of trade %s' % (tradeId), 'Portfolio=%s, CCY=%s, Counterparty=%s, Acquirer=%s, Way=%s, TraderId=%s, TradeId=%s' % (prfid, curr_insid, ptyid, acq_ptyid, way, traderId, tradeId), errdict)
            
    return trdnbr, tradeSituation

def LoopValidationErrMsg(errdict):    
    errmsg = ''
    # Instrument
    invalidInsArray = errdict['invalidIns']    
    i = 0
    while i <= len(invalidInsArray[0])-1:
        errmsg = errmsg + invalidInsArray[0][i].strip()
        body = invalidInsArray[1][i].split('|')
        j = 0
        while j <= len(body)-1:
            errmsg = errmsg + '\n\t' + body[j] 
            j = j + 1
        i = i + 1                    
        
        if errmsg != '':
            errmsg = errmsg + '\n\n'
    
    #print 'errmsg=%s' % errmsg
    invalidCptyArray = errdict['invalidParty']    
    i = 0
    while i <= len(invalidCptyArray[0])-1:
        errmsg = errmsg + invalidCptyArray[0][i].strip()
        body = invalidCptyArray[1][i].split('|')
        j = 0
        while j <= len(body)-1:
            errmsg = errmsg + '\n\t' + body[j] 
            j = j + 1
        i = i + 1         

        if errmsg != '':
            errmsg = errmsg + '\n\n'
            
    invalidPfArray = errdict['invalidPf']    
    i = 0
    while i <= len(invalidPfArray[0])-1:
        errmsg = errmsg + invalidPfArray[0][i].strip()
        body = invalidPfArray[1][i].split('|')
        j = 0
        while j <= len(body)-1:
            errmsg = errmsg + '\n\t' + body[j] 
            j = j + 1
        i = i + 1         

        if errmsg != '':
            errmsg = errmsg + '\n\n'
    
    invalidTrdCcyArray = errdict['invalidTrdCcy']    
    i = 0
    while i <= len(invalidTrdCcyArray[0])-1:
        errmsg = errmsg + invalidTrdCcyArray[0][i].strip()
        body = invalidTrdCcyArray[1][i].split('|')
        j = 0
        while j <= len(body)-1:
            errmsg = errmsg + '\n\t' + body[j] 
            j = j + 1
        i = i + 1         

        if errmsg != '':
            errmsg = errmsg + '\n\n'
            
    invalidAcqArray = errdict['invalidAcquirer']    
    i = 0
    while i <= len(invalidAcqArray[0])-1:
        errmsg = errmsg + invalidAcqArray[0][i].strip()
        body = invalidAcqArray[1][i].split('|')
        j = 0
        while j <= len(body)-1:
            errmsg = errmsg + '\n\t' + body[j] 
            j = j + 1
        i = i + 1         

        if errmsg != '':
            errmsg = errmsg + '\n\n'
    
    invalidBrokerArray = errdict['invalidBroker']    
    i = 0
    while i <= len(invalidBrokerArray[0])-1:
        errmsg = errmsg + invalidBrokerArray[0][i].strip()
        body = invalidBrokerArray[1][i].split('|')
        j = 0
        while j <= len(body)-1:
            errmsg = errmsg + '\n\t' + body[j] 
            j = j + 1
        i = i + 1         

        if errmsg != '':
            errmsg = errmsg + '\n\n'    
            
    return errmsg

def mapCounterparty(acc, addinfo_fieldname):
    strSql = """select p.ptyid
            from party p, additionalinfo a, additionalinfospec s
            where p.ptynbr = a.recaddr
            and a.addinf_specnbr = s.specnbr
            and s.field_name = '%s'
            and s.rec_type = 'Party'
            and (a.value = '%s' or a.value like '%s' or a.value like '%s')""" % (addinfo_fieldname, acc, acc+',%', '%,'+acc)

    print strSql
    rs = ael.asql(strSql)
    
    ptyid = ''
    columns, buf = rs
    for table in buf:                        
        for row in table:
            ptyid = row[0]
            
    return ptyid
    
def mapMssAccCode(prfid, insid):
    acm_pf = acm.FPhysicalPortfolio[prfid]
    acm_ins = acm.FInstrument[insid]    
    if acm_pf != None and acm_ins != None:
        if acm_ins.Otc() == False:            
            if acm_ins.InsType() in ('Stock', 'Warrant'):
                return acm_pf.AdditionalInfo().MSSACC_STOCK().strip()
            elif acm_ins.InsType() == 'Future/Forward':
                return acm_pf.AdditionalInfo().MSSACC_FUTURE_OPT().strip()
            elif acm_ins.InsType() == 'Option':
                if acm_ins.Underlying().InsType() == 'Stock':
                    return acm_pf.AdditionalInfo().MSSACC_STOCK_OPT().strip()
                elif acm_ins.Underlying().InsType() == 'EquityIndex':
                    return acm_pf.AdditionalInfo().MSSACC_FUTURE_OPT().strip()
                else:
                    return ""
            else:
                return ""
        else:
            return acm_pf.AdditionalInfo().MSSACC_OTC().strip()
    else:
        return ""
    
def mapPfByMssAcc(trd_mss_acc, insid):
    acm_ins = acm.FInstrument[insid]
    if acm_ins == None:
        return ""
    
    pf_type = ''
    if acm_ins.Otc() == False:
        if acm_ins.InsType() in ('Stock', 'Warrant'):
            pf_type = "MSSACC_STOCK"            
        elif acm_ins.InsType() == 'Future/Forward':
            pf_type = "MSSACC_FUTURE_OPT"            
        elif acm_ins.InsType() == 'Option':
            if acm_ins.Underlying().InsType() == 'Stock':
                pf_type = "MSSACC_STOCK_OPT"                
            elif acm_ins.Underlying().InsType() == 'EquityIndex':
                pf_type = "MSSACC_FUTURE_OPT"                
            else:
                return ""
        else:
            return ""
    else:
        pf_type = "MSSACC_OTC"
     
    prfid = ''
    strSql = """select pf.prfid
            from portfolio pf, additionalinfo ai, additionalinfospec ais
            where pf.prfnbr = ai.recaddr
            and ai.addinf_specnbr = ais.specnbr
            and ais.field_name = '%s'
            and ai.value = '%s'
            and ais.rec_type = 'Portfolio'""" % (pf_type, trd_mss_acc)
                
    print strSql
    rs = ael.asql(strSql)    
    columns, buf = rs
    trdnbr = 0
    for table in buf:                        
        for row in table:
            prfid = row[0].strip()
            break
    
    return prfid
    
def mapPf(pf, addinfo_fieldname):
    
    strSql = """select p.prfid
            from portfolio p, additionalinfo a, additionalinfospec s
            where p.prfnbr = a.recaddr
            and a.addinf_specnbr = s.specnbr
            and s.field_name = '%s'
            and s.rec_type = 'Portfolio'
            and (a.value = '%s' or a.value like '%s' or a.value like '%s')""" % (addinfo_fieldname, pf, pf+',%', '%,'+pf)

    print strSql
    rs = ael.asql(strSql)
    
    prfid = ''
    columns, buf = rs
    for table in buf:                        
        for row in table:
            prfid = row[0]
            
    return prfid

def getIssuerByWarrantName(warrant_name, addinfo_fieldname):
    issuer_ptyid = ''
    #print 'A'
    if len(warrant_name) >= 2:
        #print 'B'
        strSql = """select p.ptyid
                from party p, additionalinfo a, additionalinfospec s
                where p.ptynbr = a.recaddr
                and a.addinf_specnbr = s.specnbr
                and s.field_name = '%s'
                and s.rec_type = 'Party'
                and a.value = '%s'""" % (addinfo_fieldname, warrant_name[0:2])
            
        print strSql
        rs = ael.asql(strSql)
            
        columns, buf = rs
        for table in buf:                        
            for row in table:
                issuer_ptyid = row[0]
            
    return issuer_ptyid


'''
def mapMSSAccAgainstHorizonPf(horizon_pf)
    strSql = """select a.value
                from portfolio p, additionalinfo a, additionalinfospec s
                where pf.prfnbr = a.recaddr
                and a.addinf_specnbr = s.specnbr
                and s.field_name = '%s'
                and s.rec_type = 'Portfolio'
                and a.value = '%s'""" % (addinfo_fieldname, warrant_name[0:2])
'''
