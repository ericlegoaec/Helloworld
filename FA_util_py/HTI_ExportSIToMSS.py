import ael
import acm
import time
import datetime
import os
import stat
import smtplib
import shutil
import string
#import HTI_DB_Functions
from datetime import date
from datetime import datetime
import shlex
#import HTI_MailFunction
import os

SEQNBR = 0
TRDNBR = 1
SETTTYPE = 2
VALUEDAY = 3
TEXT1 = 4
PRFID = 5
AMOUNT = 6
ISIN = 7
INSTYPE = 8
UI_ISIN = 9

'''
select s.seqnbr, t.trdnbr, s.type, s.value_day, t.text1
from settlement s, trade t, instrument i
where s.trdnbr = t.trdnbr
and t.insaddr = i.insaddr
and s.status = 'Released'
and s.updat_time >= Today and s.updat_time < Today + 1
and s.type in ('Security Nominal', 'End Security')
'''

dsn = "HTIConnString"

msse_fa_acc_mapping = {'Trading Book 5': '02-0238771-22', 
                        'Trading Book 6': '02-0228640-30',
                        'Trading Book 7': '02-0228640-30',
                        'Trading Book 8': '02-0228640-30',
                        'Trading Book 13': '02-0263880-22',
                        'Trading Book 14': '02-0228640-30',
                        'Trading Book 17': '02-0238771-22'}

pfs = acm.FPhysicalPortfolio.Select('')

def get_dates():
    dates = []
    dates.append("TODAY")
    dates.append(ael.date('2015-05-28'))
    return dates
    
def get_all_setttypes():
    settType = []
    settType.append('Coupon')
    settType.append('Coupon Transfer')             
    
def get_all_instypes():
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
    
def get_all_portfolios():
    portfolios = []
    for port in ael.Portfolio.select():
        portfolios.append(port.display_id())
    portfolios.sort()
    return portfolios    
    
def get_all_acquirers():
    acquirers = []
    for acq in ael.Party.select("type = 'Intern Dept'"):
        acquirers.append(acq.display_id())
    acquirers.sort()
    return acquirers
            
def get_all_fileMsgType():
    msgType = []
    msgType.append("SI")                # Sec In/Out
    msgType.sort()
    return msgType
    
def disable_variables(variables, enable = 0):
    for i in variables:            
        for j in ael_variables:
            if i == j[0]:
                j[9] = enable    
                
def get_all_status():
    status = []
    status.append('Released')
    status.append('Pending Closure')
    status.append('Closed')
    status.sort()
    return status                
    
ael_variables = [['acquirers', 'Acquirers', 'string', get_all_acquirers(), 'HTIFP', 1, 1, 'Acquirers', None, 1], \
                ['sett_status', 'Settlement Status', 'string', get_all_status(), 'Released', 1, 1, 'Settlement Status', None, 1], \
                ['instypes', 'Instrument Types', 'string', get_all_instypes(), 'Bond', 1, 1, 'Instrument Types', None, 1], \
                ['not_setttypes', 'Not Settlement Types', 'string', get_all_setttypes(), 'Coupon,Coupon Transfer', 1, 1, 'Not Settlement Types', None, 1], \
                ['pf', 'Portfolio', 'string', get_all_portfolios(), None, 1, 1, 'Portfolio', None, 1], \
                ['filePath', 'File Path', 'string', None, 'c:\\temp', 1, 0, 'File Name', None, 1], \
                ['fileName', 'File Name', 'string', None, '<FileMsgType>_<YYYYMMDDhhmmss>.csv', 1, 0, 'File Name', None, 0], \
                ['participant_id', 'Participant Id', 'string', None, 'B01143', 1, 0, 'Haitong Participant Id', None, 1], \
                ['asofdate', 'Date', 'string', get_dates(), "TODAY", 1, 0, 'Date', None, 1], \
                ['fileMsgType', 'File Message Type', 'string', get_all_fileMsgType(), 'SI', 1, 0, 'File Message Type', None, 0]]

def EmailNotify(subject, messg, RECIPIENTS):    
    session = smtplib.SMTP(smtpserver)
    
    BODY = string.join((
        "From: %s" % SENDER,
        "To: %s" % RECIPIENTS,
        "Subject: %s" % subject,
        "",
        messg
        ), "\r\n")
    
    #print BODY    
    if AUTHREQUIRED:
        session.login(smtpuser, smtppass)
        
    smtpresult = session.sendmail(SENDER, RECIPIENTS, BODY)
    
    if smtpresult:
        errstr = ''
        for recip in smtpresult.keys():
            errstr = 'Could not delivery mail to: %s Server said: %s %s %s' % (recip, smtpresult[recip][0], smtpresult[recip][1])
            raise smtplib.SMTPException, errstr
    
    session.quit() 
    
def ValidPortfolio(array_pf, portfolio):
    for pf in array_pf:
        if portfolio == pf:
            return True
    return False
    
def getExecBroker(ptyid):
    p = ael.Party[ptyid]
    for ai in p.additional_infos():
        if ai.addinf_specnbr.field_name == 'Broker Ref':
            return ai.value.strip()
    
    return ''
                    
def ConvertDateToYYYYMMDD(dt):
    d = ael.date(dt).to_ymd()
    yy = str(d[0])
    mm = str(d[1])
    if d[1] < 10:
        mm = "0" + mm
    dd = str(d[2])
    if d[2] < 10:
        dd = "0" + dd
    return yy+mm+dd
    
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


def ael_main(dict):
    # Acquirers
    acq_array_list = dict['acquirers']
    
    acq_list = ''
    for acq in acq_array_list:
        if acq_list == '':
            acq_list = "'" + acq + "'"
        else:
            acq_list = acq_list + ",'" + acq + "'"
            
    # instypes
    instype_array_list = dict['instypes']
    
    instype_list = ''
    for instype in instype_array_list:
        if instype_list == '':
            instype_list = "'" + instype + "'"
        else:
            instype_list = instype_list + ",'" + instype + "'"
            
    # settlement status
    sett_status_array_list = dict['sett_status']
    
    sett_status_list = ''
    for sett_status in sett_status_array_list:
        if sett_status_list == '':
            sett_status_list = "'" + sett_status + "'"
        else:
            sett_status_list = sett_status_list + ",'" + sett_status + "'"
        
    # Portfolios
    pf_array_list = dict['pf'] 
    
    pf_list = ''
    for pf in pf_array_list:
        if pf_list == '':
            pf_list = "'" + pf + "'"
        else:
            pf_list = pf_list + ",'" + pf + "'"
            
    # sett_types
    not_setttype_array_list = dict['not_setttypes']
    
    not_setttype_list = ''
    for setttype in not_setttype_array_list:
        if not_setttype_list == '':
            not_setttype_list = "'" + setttype + "'"
        else:
            not_setttype_list = not_setttype_list + ",'" + setttype + "'"
            
    participant_id = dict['participant_id']
            
    
    print 'pf_list', pf_list
    
    print 'acq_list', acq_list
    print 'sett_status_list', sett_status_list
    print 'not_setttype_list', not_setttype_list
    print 'instype_list', instype_list
            
    # File Message Type
    fileMsgType = dict['fileMsgType']    
        
    # Asof Date
    asofdate = dict['asofdate']
    if asofdate == 'TODAY':
        d = ael.date_today().to_ymd()        
        d1 = ael.date_today().add_days(1).to_ymd()    
    else:
        d = ael.date(asofdate).to_ymd() 
        d1 = ael.date(asofdate).add_days(1).to_ymd()    
       
    
    yy = str(d[0])
    mm = str(d[1]) 
    mm = "%02d" % int(mm)
    dd = str(d[2])
    dd = "%02d" % int(dd)
    asofdate = yy+'-'+mm+'-'+dd
    
    yy = str(d1[0])
    mm = str(d1[1])
    mm = "%02d" % int(mm)
    dd = str(d1[2])
    dd = "%02d" % int(dd)
    d1_date = yy+'-'+mm+'-'+dd
        
    
    # File Name
    filePath = dict['filePath']
    fileName = dict['fileName']
    fileName = filePath + '\\' + fileName
    genDate = ael.date_today()
    timeStamp = time.strftime("%Y%m%d%H%M%S")       
    fileName = fileName.replace("<YYYYMMDDhhmmss>", timeStamp)
    fileName = fileName.replace("<FileMsgType>", fileMsgType)
    
    errMsg = ''
    
    print fileName
    
    f = open(fileName, "w")
        
    # trade details
    if fileMsgType == 'SI': 
        # Header
        headerLine = "settleDate,instructionType,settleMethod,haitongParticipantId,market,stockCode,shares,payment,ccassClientAccountNo,haitongClientAccountNo"
        headerLine = str(headerLine) + '\n'
        print headerLine
        f.write(headerLine)
    
        strSql = """select s.seqnbr, t.trdnbr, s.type, s.value_day, t.text1, pf.prfid, s.amount, i.isin, i.instype, ui.isin
                    from settlement s, trade t, instrument i, party acq, portfolio pf, instrument ui
                    where s.trdnbr = t.trdnbr
                    and t.insaddr = i.insaddr
                    and t.acquirer_ptynbr = acq.ptynbr
                    and t.prfnbr = pf.prfnbr
                    and acq.ptyid in (%s)
                    and s.status in (%s)
                    and s.updat_time >= '%s' and s.updat_time < '%s'
                    and i.instype in (%s)
                    and t.category ~= 'Collateral'
                    and pf.prfid in (%s)
                    and i.und_insaddr *= ui.insaddr
                    and s.type in ('Security Nominal', 'End Security')""" % (acq_list, sett_status_list, asofdate, d1_date, instype_list, pf_list)
                    
        print strSql          
        
        recCnt = 0
        rs = ael.asql(strSql)    
        columns, buf = rs
        for table in buf:                        
            for row in table:                
                print row
                seqnbr = str(row[SEQNBR]).strip() 
                trdnbr = str(row[TRDNBR]).strip() 
                setttype = str(row[SETTTYPE]).strip() 
                valueday = str(row[VALUEDAY]).strip() 
                text1 = str(row[TEXT1]).strip()                 
                sec_amount = str(row[AMOUNT]).strip()
                instype = str(row[INSTYPE]).strip()
                print 'louis1'
                if instype == 'Repo/Reverse':
                    if text1 == '':
                        prfid = str(row[PRFID]).strip()
                    else:
                        prfid = text1
                    isin = str(row[UI_ISIN]).strip()
                else:
                    prfid = str(row[PRFID]).strip()
                    isin = str(row[ISIN]).strip()
                
                accountId = ''    
                
                try:
                    accountId = msse_fa_acc_mapping[prfid]
                except:
                    print 'cannot get accountId'
                
                settledt = ael.date(valueday).to_string("%Y-%m-%d")
                
                if float(sec_amount) >= 0:
                    instructionType = 'DELIVER'
                else:
                    instructionType = 'RECEIVE'
                    
                settlemethod = 'FOP'
                marketcode = 'OTC'
                
                payment = '0.00'
                sec_amount = str(abs(float(sec_amount)))
                                
                payment_strSql = """select sum(s.amount) 'amount'
                        from settlement s, trade t, instrument i, party acq, portfolio pf, instrument ui
                        where s.trdnbr = t.trdnbr
                        and t.insaddr = i.insaddr
                        and t.acquirer_ptynbr = acq.ptynbr
                        and t.prfnbr = pf.prfnbr
                        and acq.ptyid in (%s)
                        and s.status in (%s)
                        and i.instype in (%s)
                        and t.category ~= 'Collateral'
                        and pf.prfid in (%s)
                        and i.und_insaddr *= ui.insaddr
                        and s.type not in ('Security Nominal', 'End Security')
                        and s.type not in (%s)
                        and s.value_day = '%s'
                        and t.trdnbr = %s""" % (acq_list, sett_status_list, instype_list, pf_list, not_setttype_list, settledt, int(trdnbr))
                        
                print payment_strSql
                
                
                payment_rs = ael.asql(payment_strSql)    
                payment_columns, payment_buf = payment_rs
                for payment_table in payment_buf:                        
                    for payment_row in payment_table:
                        payment = str(abs(float(str(payment_row[0]).strip())))
                        settlemethod = 'DVP'                
                        print 'payment', payment
                                        
                detailLine = settledt + ',' + instructionType + ',' + settlemethod + ',' + participant_id + ',' + marketcode + ',' + isin + ',' + sec_amount + ',' + payment + ',' + '' + ',' + accountId                                            
                detailLine = str(detailLine) + '\n'
                
                recCnt = recCnt + 1
                print detailLine
                f.write(detailLine)
    
    else:
        recCnt = 0
        
    f.close()    
    
    mb = acm.GetFunction("msgBox", 3)
    if mb != None:
        mb("Message", "File has been generated successfully at " + fileName, 0)
    mb = None
    
    return
