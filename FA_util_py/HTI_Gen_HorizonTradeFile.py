import ael
import acm
import os
import stat
import time
import shutil
import string
import smtplib
import HTI_functions
import HTI_DB_Functions
import datetime
from datetime import date
import HTI_FeedTrade_EDD_Util
import HTI_Util
import HTI_Email_Util
#import sys

#row details
COL_TRADE_ID = 0
COL_WAY = 1
COL_QTY = 2
COL_PRICE = 3
COL_PROD_ID = 4
COL_EXCH_FEE = 5
COL_CLEARING_FEE = 6
COL_BROK_FEE = 7
COL_TRD_CCY = 8
COL_INS_MIC = 9
COL_INS_CCY = 10
COL_INS_DESC = 11
COL_INS_LOCAL_CODE = 12
COL_INS_PROD_TYPE = 13
COL_INS_UNDERLYING = 14
COL_INS_UNDERLYING_MKTID = 15
COL_INS_MATURITY = 16
COL_INS_POINT_VALUE = 17
COL_INS_STRIKE = 18
COL_INS_OPTION_TYPE = 19
COL_INS_EXEC_TYPE = 20
COL_INS_OPTION_MODEL = 21
COL_INS_OTC = 22
COL_INS_DELIVERY_TYPE = 23
COL_INS_UL_MIC = 24
COL_INS_UL_INS_CCY = 25
COL_INS_UL_DESC = 26
COL_INS_UL_LOCAL_CODE = 27
COL_INS_ISSUE_SIZE = 28
COL_INS_ISSUE_DATE = 29
COL_INS_BARRIER_LEVEL = 30
COL_INS_BARRIER_TYPE = 31
COL_INS_UL_TYPE = 32
COL_TRD_BKR_EXCH_ID = 33
COL_TRD_PF_ID = 34
COL_INS_NAME = 35
COL_INS_UL_NAME = 36
COL_USER_ID = 37
COL_TIMESTAMP = 38
COL_WARRANTPARITY = 39

ael_variables = [['asofdate', 'Date', 'string', HTI_Util.get_dates(), "TODAY", 1, 0, 'Date', None, 1], \
                ['fileName', 'File Name', 'string', None, 'c:\\temp\\HorizonTrade_YYYYMMDD.csv', 1, 0, 'File Name', None, 1], \
                ['success_email_subj', 'Success Email Subject', 'string', None, 'FA (PROD) : FICC Bond Trade File Upload - SUCCESS', 1, 0, 'Sucess Email Subject', None, 1], \
                ['success_emaillist', 'Success Email List', 'string', None, 'louis.ck.wong@htisec.com', 1, 0, 'Success Email List', None, 1], \
                ['successEmail', 'Send Success Email', 'string', HTI_Util.get_yesno(), 'N', 0, 0, 'Send Success Email', None, 1], \
                ['failure_email_subj', 'Failure Email Subject', 'string', None, 'FA (PROD) : FICC Bond Trade File Upload - FAILED', 1, 0, 'Failure Email Subject', None, 1], \
                ['failure_emaillist', 'Failure Email List', 'string', None, 'louis.ck.wong@htisec.com', 1, 0, 'Failure Email List', None, 1], \
                ['failureEmail', 'Send Failure Email', 'string', HTI_Util.get_yesno(), 'N', 0, 0, 'Send Failure Email', None, 1], \
                ['fo_system', 'FO System', 'string', None, 'Horizon', 1, 0, 'FO System', None, 1], \
                ['bypass_ullink', 'Bypass Ullink', 'string', None, 'ULLINK', 1, 0, 'Ullink Channel Code in Horizon', None, 1], \
                ['warrant_ins_only', 'Warrant Instrument Only', 'string', HTI_Util.get_yesno(), 'N', 0, 0, 'Generate File for Warrant Instrument Only', None, 1], \
                ['phone_tradeid', 'Phone Trade Id', 'string', None, 'PHONE TRADE', 1, 0, 'Skip Phone Trade', None, 1]]


def genTradeFile(dict, FeedTrade):    
    ret = True
    
    tdt = ael.date_today()
    
    asofdate = dict['asofdate']
    if asofdate == 'TODAY':
        dtplus1 = tdt.add_days(1).to_string('%Y%m%d')
        asofdate = tdt.to_string('%Y%m%d')
    else:
        dtplus1 = ael.date(asofdate).add_days(1).to_string('%Y%m%d')
        asofdate = ael.date(asofdate).to_string('%Y%m%d')
    
    FAILURE_EMAILLIST = dict['failure_emaillist']
    print 'Failure Email List:', FAILURE_EMAILLIST
    FAILURE_RECIPIENTS = FAILURE_EMAILLIST.split(',')
    
    SUCCESS_EMAILLIST = dict['success_emaillist']
    print 'Success Email List:', SUCCESS_EMAILLIST
    SUCCESS_RECIPIENTS = SUCCESS_EMAILLIST.split(',')
    
    successSubject = dict['success_email_subj']
    errSubject = dict['failure_email_subj']
    
    send_failureEmail = dict['failureEmail']
    send_successEmail = dict['successEmail']    
    fo_system = dict['fo_system']
    bypass_ullink = dict['bypass_ullink']
    
    phone_tradeid = dict['phone_tradeid']
    
    warrant_ins_only = dict['warrant_ins_only']
    
    fileName = dict['fileName']
    fileName = fileName.replace("YYYYMMDD", tdt.to_string("%Y%m%d"))
    
    f = open(fileName, "w")
        
    print 'Reading %s database ' % (fo_system)
    print 'Process run date: ' + tdt.to_string('%Y-%m-%d')
    
    errmsg = ''
    ins_creation_cnt = 0
    success_trd_cnt = 0
    fail_trd_cnt = 0
    already_upload_cnt = 0
    skip_trd_cnt = 0
    ttl_trd_cnt = 0
    
    rs = None
    try:            
        # read database (start)            
        dsn = 'HorizonConnString'        
        if warrant_ins_only == 'Y':
            strSql = """
                    select ' ' as tradeId, ' ' as way, 0 as quantity, 0 as price, wp.productId,
                          0 as exchangeFees, 0 as clearingFees, 0 as brokerageFees, ' ' as tradeccy,
                          wp.mic, wp.currencyId as insccy, wp.description, wp.productId as localcode, 
                          case when b.productId is null then 'Warrant' else 'CBBC' end as productType, 
                          wp.ulId as underlying, wp.marketUlId as marketUlId, to_char(wp.maturity, 'YYYYMMDD') as maturity, 1 as pointValue, 
                          wp.strike, wp.optionType, wp.exerciseStyle, wp.optionModel, ' ' as isOtc, wp.deliveryType,
                          pp.mic as ul_mic, pp.currencyId as ul_insccy, pp.description as ul_description, pp.productId as ul_localcode,
                          ip.issueSize, to_char(ip.issueDate, 'YYYYMMDD') as issueDate, b.barrierLevel, b.barrierType, pp.productType as ul_type,
                          ' ' as brokerExchangeId, ' ' as portfolioId, wp.name as insname, pp.name as ul_insname, ' ' as userid,
                          ' ' as timestamp, wp.warrantparity 
                    from EDDMMAPP.WarrantProduct wp
                    inner join EDDMMAPP.PrimaryProduct pp on wp.ulId = pp.productId
                    left outer join EDDMMAPP.IssueParameters ip on wp.productId = ip.productId
                    left outer join EDDMMAPP.Barrier b on wp.productId = b.productId
                    where to_char(wp.maturity, 'YYYYMMDD') >= '%s'
                    and wp.isOtc = 0
                    and (b.rank = 0 or b.rank is null)
                    and wp.mic is not null

                    union

                    select 
                            ' ' as tradeId, ' ' as way, 0 as quantity, 0 as price, wp.productId,
                            0 as exchangeFees, 0 as clearingFees, 0 as brokerageFees, ' ' as tradeccy,
                            wp.mic, wp.currencyId as insccy, wp.description, wp.productId as localcode, 
                            case when b.productId is null then 'Warrant' else 'CBBC' end as productType, 
                            wp.ulId as underlying, wp.marketUlId as marketUlId, to_char(wp.maturity, 'YYYYMMDD') as maturity, 1 as pointValue, 
                            wp.strike, wp.optionType, wp.exerciseStyle, wp.optionModel, ' ' as isOtc, wp.deliveryType,
                            pp.mic as ul_mic, pp.currencyId as ul_insccy, pp.description as ul_description, pp.productId as ul_localcode,
                            ip.issueSize, to_char(ip.issueDate, 'YYYYMMDD') as issueDate, b.barrierLevel, b.barrierType, pp.productType as ul_type,
                            ' ' as brokerExchangeId, ' ' as portfolioId, wp.name as insname, pp.name as ul_insname, ' ' as userid,
                            ' ' as timestamp, wp.warrantparity
                    from EDDMMAPP.WarrantProduct wp
                            inner join EDDMMAPP.FutureProduct fp on wp.ulId = fp.productId
                            inner join EDDMMAPP.PrimaryProduct pp on fp.ulId = pp.productId
                            left outer join EDDMMAPP.IssueParameters ip on wp.productId = ip.productId
                            left outer join EDDMMAPP.Barrier b on wp.productId = b.productId
                    where to_char(wp.maturity, 'YYYYMMDD') >= '%s'
                    and wp.isOtc = 0
                    and (b.rank = 0 or b.rank is null)
                    and wp.mic is not null
                    """ % (asofdate, asofdate)
        else:
            strSql = """
                    select cexec.tradeId, cexec.way, cexec.quantity, cexec.price, cexec.productId, 
                            cexec.exchangeFees, cexec.clearingFees, cexec.brokerageFees, cexec.currencyId as tradeccy, 
                            pp.mic, pp.currencyId as insccy, pp.description, pp.productId as localcode, pp.productType, 
                            '' as underlying, '' as marketUlId, '29991231' as maturity, 1 as pointValue,
                            0 as strike, '' as optionType, '' as exerciseStyle, '' as optionModel, '' as isOtc, '' as deliveryType,
                            '' as wp_ul_mic, '' as wp_ul_insccy, cast('' as NVARCHAR2(255)) as wp_ul_description, '' as wp_ul_localcode,
                            0 as issueSize, '29991231' as issueDate, 0 as barrierLevel, '' as barrierType, '' as ul_type,
                            cexec.brokerExchangeId, cexec.portfolioId, pp.name as insname, '' as ul_insname, cexec.userid,
                            to_char(cexec.timestamp, 'YYYYMMDD HH24MISS') as timestamp, 0 as warrantparity
                    from EDDMMAPP.CashExecution cexec, EDDMMAPP.PrimaryProduct pp
                    where cexec.productId = pp.productId
                    and cexec.imsid not in ('%s')
                    and to_char(cexec.timestamp, 'YYYYMMDD') >= '%s' and to_char(cexec.timestamp, 'YYYYMMDD') < '%s'
                    and cexec.imsuserid <> '%s' and cexec.SESSIONID <> '%s'

                    union

                    select
                            dexec.tradeId, dexec.way, dexec.quantity, dexec.price, dexec.productId,
                            dexec.exchangeFees, dexec.clearingFees, dexec.brokerageFees, dexec.currencyId as tradeccy,
                            fp.mic, fp.currencyId as insccy, fp.description, fp.productId as localcode, 'Future' as productType, 
                            fp.ulId as underlying, fp.marketUlId as marketUlId, to_char(fp.maturity, 'YYYYMMDD') as maturity, fp.pointValue,
                            0 as strike, '' as optionType, '' as exerciseStyle, '' as optionModel, '' as isOtc, 'Cash' as deliveryType,
                            pp.mic as ul_mic, pp.currencyId as ul_insccy, pp.description as ul_description, pp.productId as ul_localcode,
                            0 as issueSize, '29991231' as issueDate, 0 as barrierLevel, '' as barrierType, pp.productType as ul_type,
                            dexec.brokerExchangeId, dexec.portfolioId, fp.name as insname, pp.name as ul_insname, dexec.userid,
                            to_char(dexec.timestamp, 'YYYYMMDD HH24MISS') as timestamp, 0 as warrantparity
                    from EDDMMAPP.DerivativeExecution dexec, EDDMMAPP.FutureProduct fp, EDDMMAPP.PrimaryProduct pp
                    where dexec.productId = fp.productId
                    and fp.ulId = pp.productId
                    and dexec.imsid not in ('%s')
                    and to_char(dexec.timestamp, 'YYYYMMDD') >= '%s' and to_char(dexec.timestamp, 'YYYYMMDD') < '%s'
                    and dexec.imsuserid <> '%s' and dexec.SESSIONID <> '%s'
                    
                    union

                    select 
                            dexec.tradeId, dexec.way, dexec.quantity, dexec.price, dexec.productId,
                            dexec.exchangeFees, dexec.clearingFees, dexec.brokerageFees, dexec.currencyId as tradeccy,
                            op.mic, op.currencyId as insccy, op.description, op.productId as localcode, 'Option' as productType, 
                            op.ulId as underlying, op.marketUlId as marketUlId, to_char(op.maturity, 'YYYYMMDD') as maturity, op.pointValue, 
                            op.strike, op.optionType, op.exerciseStyle, op.optionModel, '' as isOtc, op.deliveryType,
                            pp.mic as ul_mic, pp.currencyId as ul_insccy, pp.description as ul_description, pp.productId as ul_localcode,
                            0 as issueSize, '29991231' as issueDate, 0 as barrierLevel, '' as barrierType, pp.productType as ul_type,
                            dexec.brokerExchangeId, dexec.portfolioId, op.name as insname, pp.name as ul_insname, dexec.userid,
                            to_char(dexec.timestamp, 'YYYYMMDD HH24MISS') as timestamp, 0 as warrantparity
                    from EDDMMAPP.DerivativeExecution dexec, EDDMMAPP.OptionProduct op, EDDMMAPP.PrimaryProduct pp
                    where dexec.productId = op.productId
                    and op.ulId = pp.productId and op.isOtc = 0
                    and dexec.imsid not in ('%s')
                    and to_char(dexec.timestamp, 'YYYYMMDD') >= '%s' and to_char(dexec.timestamp, 'YYYYMMDD') < '%s'
                    and dexec.imsuserid <> '%s' and dexec.SESSIONID <> '%s'
                    
                    union
                    
                    select 
                            dexec.tradeId, dexec.way, dexec.quantity, dexec.price, dexec.productId,
                            dexec.exchangeFees, dexec.clearingFees, dexec.brokerageFees, dexec.currencyId as tradeccy,
                            op.mic, op.currencyId as insccy, op.description, op.productId as localcode, 'Option' as productType, 
                            op.ulId as underlying, op.marketUlId as marketUlId, to_char(op.maturity, 'YYYYMMDD') as maturity, op.pointValue, 
                            op.strike, op.optionType, op.exerciseStyle, op.optionModel, '' as isOtc, op.deliveryType,
                            pp.mic as ul_mic, pp.currencyId as ul_insccy, pp.description as ul_description, pp.productId as ul_localcode,
                            0 as issueSize, '29991231' as issueDate, 0 as barrierLevel, '' as barrierType, pp.productType as ul_type,
                            dexec.brokerExchangeId, dexec.portfolioId, op.name as insname, pp.name as ul_insname, dexec.userid,
                            to_char(dexec.timestamp, 'YYYYMMDD HH24MISS') as timestamp, 0 as warrantparity
                    from EDDMMAPP.DerivativeExecution dexec, EDDMMAPP.OptionProduct op, EDDMMAPP.FutureProduct fp, EDDMMAPP.PrimaryProduct pp
                    where dexec.productId = op.productId and op.isOtc = 0
                    and op.ulId = fp.productId
                    and fp.ulId = pp.productId
                    and dexec.imsid not in ('%s')
                    and to_char(dexec.timestamp, 'YYYYMMDD') >= '%s' and to_char(dexec.timestamp, 'YYYYMMDD') < '%s'
                    and pp.productType = 'index'
                    and dexec.imsuserid <> '%s' and dexec.SESSIONID <> '%s'
                    
                    union
                    
                    select 
                            dexec.tradeId, dexec.way, dexec.quantity, dexec.price, dexec.productId,
                            dexec.exchangeFees, dexec.clearingFees, dexec.brokerageFees, dexec.currencyId as tradeccy,
                            wp.mic, wp.currencyId as insccy, wp.description, wp.productId as localcode, 
                            case when b.productId is null then 'Warrant' else 'CBBC' end as productType, 
                            wp.ulId as underlying, wp.marketUlId as marketUlId, to_char(wp.maturity, 'YYYYMMDD') as maturity, 1 as pointValue, 
                            wp.strike, wp.optionType, wp.exerciseStyle, wp.optionModel, '' as isOtc, wp.deliveryType,
                            pp.mic as ul_mic, pp.currencyId as ul_insccy, pp.description as ul_description, pp.productId as ul_localcode,
                            ip.issueSize, to_char(ip.issueDate, 'YYYYMMDD') as issueDate, b.barrierLevel, b.barrierType, pp.productType as ul_type,
                            dexec.brokerExchangeId, dexec.portfolioId, wp.name as insname, pp.name as ul_insname, dexec.userid,
                            to_char(dexec.timestamp, 'YYYYMMDD HH24MISS') as timestamp, wp.warrantparity
                    from EDDMMAPP.DerivativeExecution dexec
                            inner join EDDMMAPP.WarrantProduct wp on dexec.productId = wp.productId
                            inner join EDDMMAPP.PrimaryProduct pp on wp.ulId = pp.productId
                            left outer join EDDMMAPP.IssueParameters ip on dexec.productId = ip.productId
                            left outer join EDDMMAPP.Barrier b on dexec.productId = b.productId
                    where wp.isOtc = 0
                    and dexec.imsid not in ('%s')
                    and to_char(dexec.timestamp, 'YYYYMMDD') >= '%s' and to_char(dexec.timestamp, 'YYYYMMDD') < '%s'
                    and (b.rank = 0 or b.rank is null)
                    and dexec.imsuserid <> '%s' and dexec.SESSIONID <> '%s'
                    
                    union
                    
                    select 
                            dexec.tradeId, dexec.way, dexec.quantity, dexec.price, dexec.productId,
                            dexec.exchangeFees, dexec.clearingFees, dexec.brokerageFees, dexec.currencyId as tradeccy,
                            wp.mic, wp.currencyId as insccy, wp.description, wp.productId as localcode, 
                            case when b.productId is null then 'Warrant' else 'CBBC' end as productType, 
                            wp.ulId as underlying, wp.marketUlId as marketUlId, to_char(wp.maturity, 'YYYYMMDD') as maturity, 1 as pointValue, 
                            wp.strike, wp.optionType, wp.exerciseStyle, wp.optionModel, '' as isOtc, wp.deliveryType,
                            pp.mic as ul_mic, pp.currencyId as ul_insccy, pp.description as ul_description, pp.productId as ul_localcode,
                            ip.issueSize, to_char(ip.issueDate, 'YYYYMMDD') as issueDate, b.barrierLevel, b.barrierType, pp.productType as ul_type,
                            dexec.brokerExchangeId, dexec.portfolioId, wp.name as insname, pp.name as ul_insname, dexec.userid,
                            to_char(dexec.timestamp, 'YYYYMMDD HH24MISS') as timestamp, wp.warrantparity
                    from EDDMMAPP.DerivativeExecution dexec
                            inner join EDDMMAPP.WarrantProduct wp on dexec.productId = wp.productId
                            inner join EDDMMAPP.FutureProduct fp on wp.ulId = fp.productId
                            inner join EDDMMAPP.PrimaryProduct pp on fp.ulId = pp.productId
                            left outer join EDDMMAPP.IssueParameters ip on dexec.productId = ip.productId
                            left outer join EDDMMAPP.Barrier b on dexec.productId = b.productId
                    where wp.isOtc = 0
                    and dexec.imsid not in ('%s')
                    and to_char(dexec.timestamp, 'YYYYMMDD') >= '%s' and to_char(dexec.timestamp, 'YYYYMMDD') < '%s'
                    and (b.rank = 0 or b.rank is null)
                    and dexec.imsuserid <> '%s' and dexec.SESSIONID <> '%s'                
                    """ % (bypass_ullink,asofdate,dtplus1,phone_tradeid,phone_tradeid,bypass_ullink,asofdate,dtplus1,phone_tradeid,phone_tradeid,bypass_ullink,asofdate,dtplus1,phone_tradeid,phone_tradeid,bypass_ullink,asofdate,dtplus1,phone_tradeid,phone_tradeid,bypass_ullink,asofdate,dtplus1,phone_tradeid,phone_tradeid,bypass_ullink,asofdate,dtplus1,phone_tradeid,phone_tradeid)
        
        print strSql        
        rs = HTI_DB_Functions.exec_sql_return_table(strSql, dsn, 'V', False)
        
        DataTable = []
        while(rs.EOF == False): 
            Row = []
            for GetField in rs.Fields:                                
                Row.append(GetField.Value)    
            DataTable.append(Row)
            ttl_trd_cnt = ttl_trd_cnt + 1
            rs.MoveNext()
        rs.Close()
        rs = None
        
        print DataTable
        #return
        
        for row in DataTable:
            tradeId = row[COL_TRADE_ID].strip()
            way = row[COL_WAY].strip()
            qty = str(float(row[COL_QTY]))
            price = str(float(row[COL_PRICE]))
            prodId = row[COL_PROD_ID].strip()
            exchFee = row[COL_EXCH_FEE]
            clearingFee = row[COL_CLEARING_FEE]
            print 'A'
            brokFee = row[COL_BROK_FEE]
            print 'A1'
            trdCcy = row[COL_TRD_CCY].strip()
            print 'A2', row[COL_INS_MIC]
            insMic = row[COL_INS_MIC].strip()
            print 'A3'
            insCcy = row[COL_INS_CCY].strip()
            print 'A4'
            insDesc = row[COL_INS_DESC].strip()
            print 'A5'
            insLocalCode = row[COL_INS_LOCAL_CODE].strip()
            print 'A6'
            insProdType = row[COL_INS_PROD_TYPE].strip().upper()
            print 'B'
            if row[COL_INS_UNDERLYING] != None:
                insUnderlying = row[COL_INS_UNDERLYING].strip()
            else:
                insUnderlying = ''
            if insProdType.upper() in ('OPTION', 'FUTURE'):
                if row[COL_INS_UNDERLYING_MKTID] != None:
                    insUnderlying_mktId = row[COL_INS_UNDERLYING_MKTID].strip()
                else:
                    insUnderlying_mktId = ''
            else:
                insUnderlying_mktId = ''
                insUnderlying_mktId = ''
            print 'B1'
            insMaturity = row[COL_INS_MATURITY].strip()
            
            print 'C'
            
            insPointValue = str(float(row[COL_INS_POINT_VALUE]))
            insStrike = str(float(row[COL_INS_STRIKE]))
            print 'D'
            if row[COL_INS_OPTION_TYPE] != None:
                insOptionType = row[COL_INS_OPTION_TYPE].strip()
            else:
                insOptionType = ''
            print 'E'
            if row[COL_INS_EXEC_TYPE] != None:
                insExecType = row[COL_INS_EXEC_TYPE].strip()
            else:
                insExecType = ''
            print 'F'
            if row[COL_INS_OPTION_MODEL] != None:
                insOptionModel = row[COL_INS_OPTION_MODEL].strip()                
            else:
                insOptionModel = ''
            print 'G'
            insOtc = row[COL_INS_OTC]
            if row[COL_INS_DELIVERY_TYPE] != None:
                insDeliveryType = row[COL_INS_DELIVERY_TYPE].strip()
            else:
                insDeliveryType = ''
            print 'H'
            if row[COL_INS_UL_MIC] != None:
                insUlMic = row[COL_INS_UL_MIC].strip()
            else:
                insUlMic = ''
            if row[COL_INS_UL_INS_CCY] != None:
                insUlInsCcy = row[COL_INS_UL_INS_CCY].strip()
            else:
                insUlInsCcy = ''
            #print 'A3'
            if row[COL_INS_UL_DESC] != None:
                insUlDesc = row[COL_INS_UL_DESC].strip().replace(",", "")
            else:
                insUlDesc = ''
            if row[COL_INS_UL_LOCAL_CODE] != None:
                insUlLocalCode = row[COL_INS_UL_LOCAL_CODE].strip()
            else:
                insUlLocalCode = ''   
            #print 'A4', row[COL_INS_ISSUE_SIZE], row[COL_INS_BARRIER_LEVEL], insProdType, row[COL_INS_ISSUE_SIZE]
            
            if row[COL_INS_ISSUE_SIZE] != None:
                insIssueSize = str(float(row[COL_INS_ISSUE_SIZE]))
            else:
                insIssueSize = str(float(0))
            #print 'A41', insIssueSize
            if row[COL_INS_BARRIER_LEVEL] != None:
                insBarrierLevel = str(float(row[COL_INS_BARRIER_LEVEL]))
            else:
                insBarrierLevel = str(float(0))
            #print 'A5', insBarrierLevel, row[COL_INS_BARRIER_TYPE]
            if row[COL_INS_BARRIER_TYPE] != None:
                insBarrierType = row[COL_INS_BARRIER_TYPE].strip()
            else:
                insBarrierType = ''
            #print 'A6'
            if row[COL_TRD_BKR_EXCH_ID] != None:
                trdBkrExchId = row[COL_TRD_BKR_EXCH_ID].strip()
            else:
                trdBkrExchId = ''
            trdPfid = row[COL_TRD_PF_ID].strip()
            insName = row[COL_INS_NAME].strip().replace(",", "")
            if row[COL_INS_UL_NAME] != None:
                insUlName = row[COL_INS_UL_NAME].strip().replace(",", "")
            else:
                insUlName = ''
                
            if row[COL_USER_ID] != None:
                fo_userid = row[COL_USER_ID].strip().replace(",", "")
            else:
                fo_userid = ''
                
            trdTimeStamp = row[COL_TIMESTAMP].strip()
            
            warrantParity = row[COL_WARRANTPARITY].strip()
                
            #print 'B'
            trdAcquirer = ''
            trdCounterparty = ''
            trdPortfolio = ''
            trd_td = ''
            trd_vd = ''
            
            '''
            if trdBkrExchId != '':
                trdCounterparty = HTI_FeedTrade_EDD_Util.mapCounterparty(trdBkrExchId, 'HORIZON_PARTY_ID')
            
            if trdPfid != '':
                #trdPortfolio = HTI_FeedTrade_EDD_Util.mapPf(trdPfid, 'MSS_AE_ACES_GRP_CDE')
                trdPortfolio = HTI_FeedTrade_EDD_Util.mapPf(trdPfid, 'HORIZON_PORTFOLIO')
            '''
            
            if insProdType == 'CBBC':
                if insOptionType == 'C' and insBarrierType == 'upAndOut':
                    insBullBear = 'BULL'
                elif insOptionType == 'P' and insBarrierType == 'downAndOut':
                    insBullBear = 'BEAR'
                else:
                    insBullBear = 'BULL'
            else:
                insBullBear = ''
                   
            if row[COL_INS_ISSUE_DATE] != None:
                insIssueDate = row[COL_INS_ISSUE_DATE].strip()
            else:
                insIssueDate = ''
            
            if row[COL_INS_UL_TYPE] != None:
                insUlProdType = row[COL_INS_UL_TYPE].strip().upper()
            else:
                insUlProdType = ''
            
            trd_mss_acc = ''                                
            
            #print 'C'
            
            pos = insLocalCode.find('@')
            if pos < 0:
                pos = len(insLocalCode) - 1
            
            detailLine = ''
            #print 'C1', insProdType, trdTimeStamp
            
            trdBkrExchId = ''           # empty mss_acc_code
            
            if insProdType == 'STOCK':            
                #25365,S,2000,5.5,8,HKD,XHKG,HKD,PCCW,Stock,,1,,,,,,No,Physical,,,,,,ATP,,,,,01-0241377-00,L98,20151109,20151111,,,
                detailLine = tradeId + ',' + way + ',' + str(qty) + ',' + str(price) + ',' + insLocalCode[0:pos] + ',' + trdCcy + ',' + insMic + ',' + insCcy + ',' + insDesc + ',' + \
                        insProdType + ',,' + str(insPointValue) + ',,,,,,No,Physical,,,,,,' + fo_system + ',,,,,' + trdBkrExchId + ',' + trdPfid + ',' + trd_td + ',' + trd_vd + ',' + \
                        insName + ',' + insUlName + ',' + insUnderlying_mktId + ',' + fo_userid + ',' + trdTimeStamp + ',' + warrantParity + '\n'
            elif insProdType == 'FUTURE':
                ulpos = insUlLocalCode.find('@')
                if ulpos < 0:
                    ulpos= len(insUlLocalCode) - 1                    
                #25366,B,1,9077,HHIZ5,HKD,XHKF,HKD,FUT Dec15 on HSCEI,Future,20151230,50,,,,,,No,Cash,HHI,Index,XHKG,HKD,HANG SENG CHINA ENTERPRISES IDX.,ATP,,,,,01-0241377-00,L98,20151109,20151111,,,
                detailLine = tradeId + ',' + way + ',' + str(qty) + ',' + str(price) + ',' + insLocalCode[0:pos] + ',' + trdCcy + ',' + insMic + ',' + insCcy + ',' + insDesc + ',' + \
                        insProdType + ',' + insMaturity + ',' + str(insPointValue) + ',,,,,,No,' + insDeliveryType + ',' + insUlLocalCode[0:ulpos] + ',' + insUlProdType + ',' + \
                        insUlMic + ',' + insUlInsCcy + ',' + insUlDesc + ',' + fo_system + ',,,,,' + trdBkrExchId + ',' + trdPfid + ',' + trd_td + ',' + trd_vd + ',' + insName + ',' + \
                        insUlName + ',' + insUnderlying_mktId + ',' + fo_userid + ',' + trdTimeStamp + ',' + warrantParity + '\n'
            elif insProdType == 'OPTION':
                ulpos = insUlLocalCode.find('@')
                detailLine = tradeId + ',' + way + ',' + str(qty) + ',' + str(price) + ',' + insLocalCode[0:pos] + ',' + trdCcy + ',' + insMic + ',' + insCcy + ',' + insDesc + ',' + \
                        insProdType + ',' + insMaturity + ',' + str(insPointValue) + ',' + insStrike + ',' + insOptionType + ',' + insExecType + ',,,No,' + insDeliveryType + ',' + \
                        insUlLocalCode[0:ulpos] + ',' + insUlProdType + ',' + insUlMic + ',' + insUlInsCcy + ',' + insUlDesc + ',' + fo_system + ',,,,,' + trdBkrExchId + ',' + trdPfid + ',' + \
                        trd_td + ',' + trd_vd + ',' + insName + ',' + insUlName + ',' + insUnderlying_mktId + ',' + fo_userid + ',' + trdTimeStamp + ',' + warrantParity + '\n'                
            elif insProdType == 'WARRANT':
                ulpos = insUlLocalCode.find('@')
                #25371,B,100000,0.035,22698,HKD,XHKG,HKD,CSGEELY@EC1512B,Warrant,20151214,1,4.5,Call,European,,,No,Cash,176,Stock,XHKG,HKD,Geely Autombile Holdings Limited,MSS,1234546.56,20151010,,,01-0241377-00,L98,20151109,20151111,NM-L&F @EC1606A,,                
                detailLine = tradeId + ',' + way + ',' + str(qty) + ',' + str(price) + ',' + insLocalCode[0:pos] + ',' + trdCcy + ',' + insMic + ',' + insCcy + ',' + insDesc + ',' + \
                        insProdType + ',' + insMaturity + ',' + str(insPointValue) + ',' + insStrike + ',' + insOptionType + ',' + insExecType + ',,,No,' + insDeliveryType + ',' + \
                        insUlLocalCode[0:ulpos] + ',' + insUlProdType + ',' + insUlMic + ',' + insUlInsCcy + ',' + insUlDesc + ',' + fo_system + ',' + str(insIssueSize) + ',' + insIssueDate + ',,,' + \
                        trdBkrExchId + ',' + trdPfid + ',' + trd_td + ',' + trd_vd + ',' + insName + ',' + insUlName + ',' + insUnderlying_mktId + ',' + fo_userid + ',' + trdTimeStamp + ',' + warrantParity + '\n'
            elif insProdType == 'CBBC':
                ulpos = insUlLocalCode.find('@')
                #25372,B,1,0.07,69080,HKD,XHKG,HKD,JP#HSI RC1611Z (HSI Bull),CBBC,20151119,1,21750,Call,European,Bull,21950,No,Cash,HSI,Index,XHKG,HKD,HANG SENG INDEX,ATP,999999.15,20150102,upAndOut,,01-0241377-00,L98,20151109,20151111,NM-L&F @EC1606A,,
                detailLine = tradeId + ',' + way + ',' + str(qty) + ',' + str(price) + ',' + insLocalCode[0:pos] + ',' + trdCcy + ',' + insMic + ',' + insCcy + ',' + insDesc + ',' + \
                        insProdType + ',' + insMaturity + ',' + str(insPointValue) + ',' + insStrike + ',' + insOptionType + ',' + insExecType + ',' + insBullBear + ',' + str(insBarrierLevel) + ',No,' + insDeliveryType + ',' + \
                        insUlLocalCode[0:ulpos] + ',' + insUlProdType + ',' + insUlMic + ',' + insUlInsCcy + ',' + insUlDesc + ',' + fo_system + ',' + str(insIssueSize) + ',' + insIssueDate + ',' + insBarrierType + ',,' + \
                        trdBkrExchId + ',' + trdPfid + ',' + trd_td + ',' + trd_vd + ',' + insName + ',' + insUlName + ',' + insUnderlying_mktId + ',' + fo_userid + ',' + trdTimeStamp + ',' + warrantParity + '\n'
            
            #print 'D'
            print detailLine
            f.write(detailLine)
        f.close()
        
        email_content = 'Date: %s' % tdt.to_string('%Y-%m-%d') + '\n'
        if send_successEmail == 'Y':
            
            attached_filename = os.path.basename(fileName)
            attached_filedir = os.path.dirname(fileName) + "\\" 
        
            HTI_Email_Util.SendAttachment(SUCCESS_RECIPIENTS, successSubject, email_content, [attached_filedir], [attached_filename], True)                
        else:            
            print successSubject
            print SUCCESS_RECIPIENTS
            print email_content
            print fileName            
    except:
        #print sys.exc_info()[0]

        email_content = 'Date: %s' % tdt.to_string('%Y-%m-%d') + '\n'
        if send_failureEmail == 'Y':        
            HTI_Email_Util.EmailNotify(errSubject, email_content, FAILURE_RECIPIENTS)                
        else:
            print errSubject
            print FAILURE_RECIPIENTS      
            print email_content
    finally:     
        if f != None:
            f.close()
            f = None
        
        if rs != None:
            rs.Close()
            rs = None
                
    return ret
    

def ael_main(dict): 
    '''
    # test email connection
    subject = "Currency price capture"
    body = "Process is run successfully"
    HTI_Email_Util.EmailNotify(subject, body, 'noreply_testing_fa@htisectesting.com')
    return
    '''
    
    ret = genTradeFile(dict, True)
    #ret = test_getInstrument()
