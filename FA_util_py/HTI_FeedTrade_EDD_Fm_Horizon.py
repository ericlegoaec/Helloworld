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
COL_INS_UNDERLYING_MKT = 15
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

ael_variables = [['asofdate', 'Date', 'string', HTI_Util.get_dates(), "TODAY", 1, 0, 'Date', None, 1], \
                ['quot', 'Quotation', 'string', HTI_Util.get_quot(), 'FA', 0, 0, 'Quotation', None, 1], \
                ['feedcodetype', 'Feed Code', 'string', HTI_Util.get_feedcode(), HTI_Util.ISIN, 0, 0, 'Feed Code', None, 1], \
                ['own_issuer', 'Own Issuer', 'string', HTI_Util.getAllIssuers(), '', 1, 0, 'Mark this issuer to the warrant issued by us', None, 1], \
                ['success_email_subj', 'Success Email Subject', 'string', None, 'FA (PROD) : FICC Bond Trade File Upload - SUCCESS', 1, 0, 'Sucess Email Subject', None, 1], \
                ['success_emaillist', 'Success Email List', 'string', None, 'louis.ck.wong@htisec.com', 1, 0, 'Success Email List', None, 1], \
                ['successEmail', 'Send Success Email', 'string', HTI_Util.get_yesno(), 'N', 0, 0, 'Send Success Email', None, 1], \
                ['failure_email_subj', 'Failure Email Subject', 'string', None, 'FA (PROD) : FICC Bond Trade File Upload - FAILED', 1, 0, 'Failure Email Subject', None, 1], \
                ['failure_emaillist', 'Failure Email List', 'string', None, 'louis.ck.wong@htisec.com', 1, 0, 'Failure Email List', None, 1], \
                ['failureEmail', 'Send Failure Email', 'string', HTI_Util.get_yesno(), 'N', 0, 0, 'Send Failure Email', None, 1], \
                ['default_pf', 'Default Portfolio', 'string', HTI_Util.getAllPortfolios(), 'Trading Book 1', 1, 0, 'Default Portfolio', None, 1], \
                ['default_bkr', 'Default Broker', 'string', HTI_Util.getAllBrokers(), 'Haitong Intl Securities Company Ltd.', 1, 0, 'Default Broker', None, 1], \
                ['default_cpty', 'Default Counterparty', 'string', HTI_Util.getAllParties(), 'Access Asia Investment Holdings', 1, 0, 'Default Counterparty', None, 1], \
                ['default_acq', 'Default Acquirer', 'string', HTI_Util.getAllAcquirers(), 'HTISEC - FICC', 1, 0, 'Default Acquirer', None, 1], \
                ['default_trader', 'Default Trader', 'string', None, 'ARENASYS', 1, 0, 'Default Trader', None, 1], \
                ['default_status', 'Default Trade Status', 'string', HTI_Util.getAllStatus(), 'Simulated', 1, 0, 'Default Trade Status', None, 1], \
                ['fo_system', 'FO System', 'string', None, 'Horizon', 1, 0, 'FO System', None, 1]]


def ValidateAndFeedTrade(dict, FeedTrade):    
    ret = True
    
    invalidCptyArray = [[],[]]
    invalidInsArray = [[],[]]
    invalidPfArray = [[],[]]
    invalidTrdCcyArray = [[],[]]
    invalidAcqArray = [[],[]]
    invalidBrokerArray = [[],[]]
    invalidBuySellArray = [[],[]]
    invalidTraderArray = [[],[]]
    new_arr_ins = []
    
    errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
    
    
    tdt = ael.date_today()
    
    asofdate = dict['asofdate']
    DEFAULT_PF = dict['default_pf']
    DEFAULT_BKR = dict['default_bkr']
    DEFAULT_CPTY = dict['default_cpty']
    DEFAULT_ACQ = dict['default_acq']
    DEFAULT_STATUS = dict['default_status']    
    DEFAULT_TRADER = dict['default_trader']
    OWN_ISSUER = dict['own_issuer']
    
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
    feedcodetype = dict['feedcodetype']
        
    try:        
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
            strSql = """
                    select cexec.tradeId, cexec.way, cexec.quantity, cexec.price, cexec.productId, 
                            cexec.exchangeFees, cexec.clearingFees, cexec.brokerageFees, cexec.currencyId as tradeccy, 
                            pp.mic, pp.currencyId as insccy, pp.description, pp.productId as localcode, pp.productType, 
                            '' as underlying, '' as underlying_market, '29991231' as maturity, 1 as pointValue,
                            0 as strike, '' as optionType, '' as exerciseStyle, '' as optionModel, '' as isOtc, '' as deliveryType,
                            '' as wp_ul_mic, '' as wp_ul_insccy, cast('' as NVARCHAR2(255)) as wp_ul_description, '' as wp_ul_localcode,
                            0 as issueSize, '29991231' as issueDate, 0 as barrierLevel, '' as barrierType, '' as ul_type,
                            cexec.brokerExchangeId, cexec.portfolioId, pp.name as insname, '' as ul_insname
                    from EDDMMAPP.CashExecution cexec, EDDMMAPP.PrimaryProduct pp
                    where cexec.productId = pp.productId

                    union

                    select
                            dexec.tradeId, dexec.way, dexec.quantity, dexec.price, dexec.productId,
                            dexec.exchangeFees, dexec.clearingFees, dexec.brokerageFees, dexec.currencyId as tradeccy,
                            fp.mic, fp.currencyId as insccy, fp.description, fp.productId as localcode, 'Future' as productType, 
                            fp.ulId as underlying, fp.marketUlId as underlying_market, to_char(fp.maturity, 'YYYYMONDD') as maturity, fp.pointValue,
                            0 as strike, '' as optionType, '' as exerciseStyle, '' as optionModel, '' as isOtc, '' as deliveryType,
                            '' as wp_ul_mic, '' as wp_ul_insccy, cast('' as NVARCHAR2(255)) as wp_ul_description, '' as wp_ul_localcode,
                            0 as issueSize, '29991231' as issueDate, 0 as barrierLevel, '' as barrierType, pp.productType as ul_type,
                            dexec.brokerExchangeId, dexec.portfolioId, fp.name as insname, pp.name as ul_insname
                    from EDDMMAPP.DerivativeExecution dexec, EDDMMAPP.FutureProduct fp, EDDMMAPP.PrimaryProduct pp
                    where dexec.productId = fp.productId
                    and fp.ulId = pp.productId
                    
                    union

                    select 
                            dexec.tradeId, dexec.way, dexec.quantity, dexec.price, dexec.productId,
                            dexec.exchangeFees, dexec.clearingFees, dexec.brokerageFees, dexec.currencyId as tradeccy,
                            op.mic, op.currencyId as insccy, op.description, op.productId as localcode, 'Option' as productType, 
                            op.ulId as underlying, op.marketUlId as underlying_market, to_char(op.maturity, 'YYYYMONDD') as maturity, op.pointValue, 
                            op.strike, op.optionType, op.exerciseStyle, op.optionModel, '' as isOtc, op.deliveryType,
                            '' as wp_ul_mic, '' as wp_ul_insccy, cast('' as NVARCHAR2(255)) as wp_ul_description, '' as wp_ul_localcode,
                            0 as issueSize, '29991231' as issueDate, 0 as barrierLevel, '' as barrierType, pp.productType as ul_type,
                            dexec.brokerExchangeId, dexec.portfolioId, op.name as insname, pp.name as ul_insname
                    from EDDMMAPP.DerivativeExecution dexec, EDDMMAPP.OptionProduct op, EDDMMAPP.PrimaryProduct pp
                    where dexec.productId = op.productId
                    and op.ulId = pp.productId and op.isOtc = 0
                    
                    union
                    
                    select 
                            dexec.tradeId, dexec.way, dexec.quantity, dexec.price, dexec.productId,
                            dexec.exchangeFees, dexec.clearingFees, dexec.brokerageFees, dexec.currencyId as tradeccy,
                            wp.mic, wp.currencyId as insccy, wp.description, wp.productId as localcode, 
                            case when b.productId is null then 'Warrant' else 'CBBC' end as productType, 
                            wp.ulId as underlying, wp.marketUlId as underlying_market, to_char(wp.maturity, 'YYYYMONDD') as maturity, 1 as pointValue, 
                            wp.strike, wp.optionType, wp.exerciseStyle, wp.optionModel, '' as isOtc, wp.deliveryType,
                            pp.mic as wp_ul_mic, pp.currencyId as wp_ul_insccy, pp.description as wp_ul_description, pp.productId as wp_ul_localcode,
                            ip.issueSize, to_char(ip.issueDate, 'YYYYMONDD') as issueDate, b.barrierLevel, b.barrierType, pp.productType as ul_type,
                            dexec.brokerExchangeId, dexec.portfolioId, wp.name as insname, pp.name as ul_insname
                    from EDDMMAPP.DerivativeExecution dexec
                            inner join EDDMMAPP.WarrantProduct wp on dexec.productId = wp.productId
                            inner join EDDMMAPP.PrimaryProduct pp on wp.ulId = pp.productId
                            left outer join EDDMMAPP.IssueParameters ip on dexec.productId = ip.productId
                            left outer join EDDMMAPP.Barrier b on dexec.productId = b.productId
                    where wp.isOtc = 0
                    """
            
            '''
            strSql = """
                    select *
                    from EDDMMAPP.CashExecution cexec, EDDMMAPP.PrimaryProduct pp
                    where cexec.productId = pp.productId
                    """
            '''
                    
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
                qty = row[COL_QTY].strip()
                price = row[COL_PRICE]
                prodId = row[COL_PROD_ID].strip()
                exchFee = row[COL_EXCH_FEE]
                clearingFee = row[COL_CLEARING_FEE]
                brokFee = row[COL_BROK_FEE]
                trdCcy = row[COL_TRD_CCY].strip()
                insMic = row[COL_INS_MIC].strip()
                insCcy = row[COL_INS_CCY].strip()
                insDesc = row[COL_INS_DESC].strip()
                insLocalCode = row[COL_INS_LOCAL_CODE].strip()
                insProdType = row[COL_INS_PROD_TYPE].strip().upper()
                if row[COL_INS_UNDERLYING] != None:
                    insUnderlying = row[COL_INS_UNDERLYING].strip()
                else:
                    insUnderlying = ''
                if row[COL_INS_UNDERLYING_MKT] != None:
                    insUnderlyingMic = row[COL_INS_UNDERLYING_MKT].strip()
                else:
                    insUnderlyingMic = ''
                insMaturity = row[COL_INS_MATURITY].strip()
                insPointValue = row[COL_INS_POINT_VALUE]
                insStrike = row[COL_INS_STRIKE]
                if row[COL_INS_OPTION_TYPE] != None:
                    insOptionType = row[COL_INS_OPTION_TYPE].strip()
                else:
                    insOptionType = ''
                if row[COL_INS_EXEC_TYPE] != None:
                    insExecType = row[COL_INS_EXEC_TYPE].strip()
                else:
                    insExecType = ''
                if row[COL_INS_OPTION_MODEL] != None:
                    insOptionModel = row[COL_INS_OPTION_MODEL].strip()                
                else:
                    insOptionModel = ''
                insOtc = row[COL_INS_OTC]
                if row[COL_INS_DELIVERY_TYPE] != None:
                    insDeliveryType = row[COL_INS_DELIVERY_TYPE].strip()
                else:
                    insDeliveryType = ''
                if row[COL_INS_UL_MIC] != None:
                    insUlMic = row[COL_INS_UL_MIC].strip()
                else:
                    insUlMic = ''
                if row[COL_INS_UL_INS_CCY] != None:
                    insUlInsCcy = row[COL_INS_UL_INS_CCY].strip()
                else:
                    insUlInsCcy = ''
                if row[COL_INS_UL_DESC] != None:
                    insUlDesc = row[COL_INS_UL_DESC].strip()
                else:
                    insUlDesc = ''
                if row[COL_INS_UL_LOCAL_CODE] != None:
                    insUlLocalCode = row[COL_INS_UL_LOCAL_CODE].strip()
                else:
                    insUlLocalCode = ''                    
                insIssueSize = row[COL_INS_ISSUE_SIZE]
                if row[COL_INS_BARRIER_TYPE] != None:
                    insBarrierType = row[COL_INS_BARRIER_TYPE].strip()
                else:
                    insBarrierType = ''
                if row[COL_TRD_BKR_EXCH_ID] != None:
                    trdBkrExchId = row[COL_TRD_BKR_EXCH_ID].strip()
                else:
                    trdBkrExchId = ''
                trdPfid = row[COL_TRD_PF_ID].strip()
                insName = row[COL_INS_NAME].strip()
                if row[COL_INS_UL_NAME] != None:
                    insUlName = row[COL_INS_UL_NAME].strip()
                else:
                    insUlName = ''
                trdAcquirer = ''
                trdCounterparty = ''
                trdPortfolio = ''
                trd_td = ''
                trd_vd = ''
                
                print 1, trdBkrExchId
                if trdBkrExchId != '':
                    trdCounterparty = HTI_FeedTrade_EDD_Util.mapCounterparty(trdBkrExchId, 'HORIZON_PARTY_ID')
                
                print 2
                if trdPfid != '':
                    trdPortfolio = HTI_FeedTrade_EDD_Util.mapPf(trdPfid, 'MSS_AE_ACES_GRP_CDE')
                
                print 3
                if insProdType == 'CBBC':
                    if insOptionType == 'C' and insBarrierType == 'upAndOut':
                        insBullBear = 'BULL'
                    elif insOptionType == 'P' and insBarrierType == 'downAndOut':
                        insBullBear = 'BEAR'
                else:
                    insBullBear = ''
                       
                print 4
                if row[COL_INS_ISSUE_DATE] != None:
                    insIssueDate = row[COL_INS_ISSUE_DATE].strip()
                else:
                    insIssueDate = ''
                
                if row[COL_INS_UL_TYPE] != None:
                    insUlProdType = row[COL_INS_UL_TYPE].strip()
                else:
                    insUlProdType = ''
                
                trd_mss_acc = ''                                
                
                #25365,S,2000,5.5,8,HKD,XHKG,HKD,PCCW,Stock,,1,,,,,,No,Physical,,,,,,ATP,,,,,01-0241377-00,L98,20151109,20151111,,,
                pos = insLocalCode.find('@')
                print 'pos', pos
                
                if insProdType == 'STOCK':
                    print tradeId + ',' + way + ',' + str(qty) + ',' + str(price) + ',' + insLocalCode[0:pos] + ',' + insMic + ',' + trdCcy + ',' + insDesc + ',' + \
                            insProdType + ',,' + str(insPointValue) + ',,,,,,No,Physical,,,,,,Horizon,,,,,' + trdBkrExchId + ',' + trdPfid + ',' + trd_td + ',' + trd_vd + ',,,'                
                    
                        
                print tradeId, way, qty, price, prodId, exchFee, clearingFee, \
                    brokFee, trdCcy, insMic, insCcy, insDesc, insLocalCode, \
                    insProdType, insUnderlying, insMaturity, insPointValue, \
                    insStrike, insOptionType, insExecType, insOptionModel, \
                    insOtc, insDeliveryType, insUlMic, insUlInsCcy, insUlDesc, \
                    insUlLocalCode, insIssueSize, insBullBear, insIssueDate, \
                    insBarrierType, insUlProdType, trdBkrExchId, trdPfid
                    
                trdnbr = getTrade(tradeId)
                if trdnbr == -1:    #trade already created in FA                    
                    newIns = False
                    trd_insid = ''
                    
                    issuer_ptyid = ''
                    if insProdType in ('CBBC', 'Warrant'):
                        if HTI_FeedTrade_EDD_Util.getIssuerByWarrantName(insName, 'WARRANT_ISSUER_NAME') == OWN_ISSUER:
                            issuer_ptyid = OWN_ISSUER  
                    
                    '''
                    trd_insid, newIns = HTI_FeedTrade_EDD_Util.getInstrument(insProdType, prodId, insMic, insCcy, insDesc, insLocalCode, insUnderlying, 
                                insMaturity, insPointValue, insStrike, insOptionType, insExecType, insOptionModel,
                                insOtc, insDeliveryType, insUlMic, insUlInsCcy, insUlDesc, insUlLocalCode, new_arr_ins, errdict)
                    '''
                    
                    '''
                    trd_insid, newIns = HTI_FeedTrade_EDD_Util.getInstrument(tradeId, way, qty, price, insLocalCode,
                                                    trdCcy, insMic, insCcy, insDesc, insProdType,
                                                    insMaturity, insPointValue, insStrike, insOptionType,
                                                    insExecType, insBullBear, insBarrier, insOtc, insDeliveryType,
                                                    insUlLocalCode, insULProdType, insULMic, insULCcy, insULDesc,
                                                    trdChannel, insIssueSize, insIssueDate, insBarrierType, 
                                                    issuer_ptyid, insName, insULName, new_arr_ins, errdict)
                    '''
                    
                    trd_insid, newIns = HTI_FeedTrade_EDD_Util.getInstrument(tradeId, way, qty, price, insLocalCode,
                                                    trdCcy, insMic, insCcy, insDesc, insProdType,
                                                    insMaturity, insPointValue, insStrike, insOptionType,
                                                    insExecType, insBullBear, insBarrier, insOtc, insDeliveryType,
                                                    insUlLocalCode, insUlProdType, insUlMic, insUlInsCcy, insUlDesc,
                                                    fo_system, insIssueSize, insIssueDate, insBarrierType, issuer_ptyid, 
                                                    insName, insUlName, new_arr_ins, errdict)
                                
                    if newIns and trd_insid == '':
                        print 'Created new instrument %s' % (trd_insid)
                        ins_creation_cnt = ins_creation_cnt + 1
                    
                    trdnbr = -1
                    tradeSituation = ''
                    
                    '''
                    trdnbr, tradeSituation = HTI_FeedTrade_EDD_Util.createTrade(asofdate, trd_insid, tradeId, way, qty, price, trdCcy, DEFAULT_PF, DEFAULT_CPTY,
                                                        DEFAULT_BKR, DEFAULT_ACQ, DEFAULT_STATUS, DEFAULT_TRADER, fo_system, errdict)
                    '''
                    trdnbr, tradeSituation = HTI_FeedTrade_EDD_Util.createTrade(asofdate, trd_insid, tradeId, way, qty, price, trdCcy, DEFAULT_PF, DEFAULT_CPTY,
                                                        DEFAULT_BKR, DEFAULT_ACQ, DEFAULT_STATUS, DEFAULT_TRADER, fo_system, trdAcquirer, trdCounterparty, 
                                                        trdPortfolio, trd_td, trd_vd, trd_mss_acc, errdict)
                                                        
                    if tradeSituation == 'Success' and trdnbr != -1:
                        print 'Created new trade FO:%s, FA:%s' % (tradeId, str(trdnbr))
                        success_trd_cnt = success_trd_cnt + 1
                    #elif tradeSituation == 'Exist' and trdnbr != -1:
                    #    print 'Trade %s is already exist FO:%s, FA:%s' % (tradeId, str(trdnbr))
                    #    already_upload_cnt = already_upload_cnt + 1
                    elif tradeSituation == 'Fail':
                        print 'FO Trade %s is failed to upload' % (tradeId)
                        fail_trd_cnt = fail_trd_cnt + 1
                    else:
                        print 'FO Trade %s is skipped' % (tradeId)
                        skip_trd_cnt = skip_trd_cnt + 1
                else:
                    print 'Trade %s is already exist FO:%s, FA:%s' % (tradeId, str(trdnbr))
                    already_upload_cnt = already_upload_cnt + 1
                                    
            print errdict
            validationErr = LoopValidationErrMsg(errdict)
            errmsg = errmsg + '\n' + validationErr
            
            new_ins_msg = ''
            if len(new_arr_ins) > 0:
                new_ins_msg = 'Auto-created the following Instrument in FA: -'
                new_ins_msg = new_ins_msg + '\n' + 'Instrument Id                '                    
                new_ins_msg = new_ins_msg + '\n' + '--------------------------'
                for new_insid in new_arr_ins:
                    new_ins_msg = new_ins_msg + '\n' + new_insid
            
            msg = 'Date: %s' % tdt.to_string('%Y-%m-%d') + '\n'
            msg = msg + '%s trades from %s' % (str(ttl_trd_cnt), fo_system) + '\n'
            msg = msg + '%s trades Already uploaded in previous batches' % str(already_upload_cnt) + '\n'
            msg = msg + '%s trades were skipped in this batch' % str(skip_trd_cnt) + '\n'
            msg = msg + '%s trades successfully uploaded in this batch' % str(success_trd_cnt) + '\n'
            msg = msg + '%s trades failed to upload in this batch' % str(fail_trd_cnt) + '\n'
            msg = msg + '%s instruments created in this batch' % str(ins_creation_cnt) + '\n'
            
            if errmsg.strip() != '':
                msg = msg + 'Error:' + '\t' + errmsg
                msg = msg + '\n\n' + new_ins_msg
                subject = errSubject
                if send_failureEmail == 'Y':
                    HTI_Email_Util.EmailNotify(subject, msg, RECIPIENTS)
                ret = False
            else:
                msg = msg + '\n' + 'No Error'
                msg = msg + '\n\n' + new_ins_msg
                subject = successSubject
                if send_successEmail == 'Y':
                    HTI_Email_Util.EmailNotify(subject, msg, RECIPIENTS)            
        finally:      
            if rs != None:
                rs.Close()                
                rs = None
                
            return ret
    except IOError:        
        errmsg = 'Date: %s' % tdt.to_string('%Y-%m-%d') + '\n'
        errmsg = errmsg + 'Error:' + '\n\t' + fileName + ' does not exist.'
        if send_failureEmail == 'Y':
            HTI_Email_Util.EmailNotify(errSubject, errmsg, RECIPIENTS)
    except OSError:
        errmsg = 'Date: %s' % tdt.to_string('%Y-%m-%d') + '\n'
        errmsg = errmsg + 'Error:' + '\n\t' + fileName + ' does not exist.'
        if send_failureEmail == 'Y':
            HTI_Email_Util.EmailNotify(errSubject, errmsg, RECIPIENTS)
        

def test_getInstrument():
    invalidCptyArray = [[],[]]
    invalidInsArray = [[],[]]
    invalidPfArray = [[],[]]
    invalidTrdCcyArray = [[],[]]
    invalidAcqArray = [[],[]]
    invalidBrokerArray = [[],[]]
    invalidBuySellArray = [[],[]]
    invalidTraderArray = [[],[]]
    
    errdict = {"invalidIns":invalidInsArray, "invalidParty":invalidCptyArray, "invalidPf":invalidPfArray, \
                            "invalidTrdCcy":invalidTrdCcyArray, "invalidAcquirer":invalidAcqArray, \
                            "invalidBroker":invalidBrokerArray, "invalidBuySell":invalidBuySellArray, \
                            "invalidTrader":invalidTraderArray}
                            
    DEFAULT_PF = 'Trading Book 1'
    DEFAULT_BKR = 'Haitong Intl Securities Company Ltd.'
    DEFAULT_CPTY = 'Access Asia Investment Holdings'
    DEFAULT_ACQ = 'HTIED'
    DEFAULT_STATUS = 'Simulated'
    DEFAULT_TRADER = 'ARENASYS'
    
    fo_system = 'Horizon'    
    tradeId = 'AaHWEB1-1-SEHK-ORION31015'
    way = 'S'
    qty = '400'
    price = '5.8'
    trdCcy = 'HKD' 
    
    ''' Normal Stock
    insProdType = 'Stock'
    prodId = '941@XHKG'
    insMic = 'XHKG'
    insCcy = 'HKD'
    insLocalCode = '941'
    insUnderlying = ''
    insMaturity = ''
    insPointValue = 0
    insStrike = 0
    insOptionType = ''
    insExecType = ''
    insOptionModel = ''
    insOtc = ''
    insDeliveryType = ''
    insUlMic = ''
    insUlInsCcy = ''
    insUlDesc = ''
    insUlLocalCode = ''
    feedcodetype = 'Local Exchange Code'
    insDesc = 'Testing'
    insBullBear = ''
    insBarrier = ''
    insUlProdType = ''
    new_arr_ins = [] 
    '''
    
    ''' Index Future
    insProdType = 'Future'
    prodId = 'IF1508@CCFX'
    insMic = 'CCFX'
    insCcy = 'CNY'
    insLocalCode = 'IF1508'
    insUnderlying = 'CFFEX-I'
    insMaturity = '17/7/2015  15:00:00'
    insPointValue = 300
    insStrike = 0
    insOptionType = ''
    insExecType = ''
    insOptionModel = ''
    insOtc = ''
    insDeliveryType = ''
    insUlMic = 'CCFX'
    insUlInsCcy = 'CNY'
    insUlDesc = 'testing CFFEX-I'
    insUlLocalCode = 'CFFEX-I'
    feedcodetype = 'Local Exchange Code'
    insDesc = 'Testing'
    insBullBear = ''
    insBarrier = ''
    insUlProdType = ''
    new_arr_ins = []
    '''
    
    ''' Stock Future
    insProdType = 'Future'
    prodId = '704_F@XHKG'
    insMic = 'XHKG'
    insCcy = 'HKD'
    insLocalCode = '704_F@XHKG'
    insUnderlying = '704@XHKG'
    insMaturity = '17/11/2015  15:00:00'
    insPointValue = 100
    insStrike = 0
    insOptionType = ''
    insExecType = ''
    insOptionModel = ''
    insOtc = ''
    insDeliveryType = ''
    insUlMic = 'XHKG'
    insUlInsCcy = 'HKD'
    insUlDesc = 'testing 704@XHKG'
    insUlLocalCode = '704@XHKG'
    feedcodetype = 'Local Exchange Code'
    insDesc = 'Testing'
    insBullBear = ''
    insBarrier = ''
    insUlProdType = ''
    new_arr_ins = []
    '''
    
    ''' Index Option
    insProdType = 'Option'
    prodId = 'IO1507-C-4300@CCFX'
    insMic = 'CCFX'
    insCcy = 'CNY'
    insLocalCode = 'IO1507-C-4300@CCFX'
    insUnderlying = 'CFFEX-I@CCFX'
    insMaturity = '17/11/2015  15:00:00'
    insPointValue = 100
    insStrike = 4300
    insOptionType = 'C'
    insExecType = 'E'
    insOptionModel = 'VANILLA'
    insOtc = 'FALSE'
    insDeliveryType = 'CASH'
    insUlMic = 'CCFX'
    insUlInsCcy = 'HKD'
    insUlDesc = 'testing'
    insUlLocalCode = 'CFFEX-I@CCFX'
    feedcodetype = 'Local Exchange Code'
    insDesc = 'Testing'
    new_arr_ins = []
    '''

    ''' Stock Option
    insProdType = 'Option'
    prodId = '1114-P-4@XHKG'
    insMic = 'XHKG'
    insCcy = 'HKD'
    insLocalCode = '1114-C-4@XHKG'
    insUnderlying = '1114@XHKG'
    insMaturity = '17/11/2015  15:00:00'
    insPointValue = 1
    insStrike = 4
    insOptionType = 'P'
    insExecType = 'A'
    insOptionModel = 'VANILLA'
    insOtc = 'FALSE'
    insDeliveryType = 'CASH'
    insUlMic = 'XHKG'
    insUlInsCcy = 'HKD'
    insUlDesc = 'testing'
    insUlLocalCode = '1114@XHKG'
    feedcodetype = 'Local Exchange Code'
    insDesc = 'Testing'
    new_arr_ins = []
    '''
    
    '''
    insProdType = 'Warrant'
    prodId = '17809@XHKG'
    insMic = 'XHKG'
    insCcy = 'HKD'
    insLocalCode = '17808@XHKG'
    insUnderlying = '388@XHKG'
    insMaturity = '17/11/2015  15:00:00'
    insPointValue = 1
    insStrike = 100.68
    insOptionType = 'C'
    insExecType = 'E'
    insOptionModel = ''
    insOtc = 'FALSE'
    insDeliveryType = 'CASH'
    insUlMic = 'XHKG'
    insUlInsCcy = 'HKD'
    insUlDesc = 'testing'
    insUlLocalCode = '388@XHKG'
    feedcodetype = 'Local Exchange Code'
    insDesc = 'Testing'
    new_arr_ins = []
    
    '''
    
    '''
    trd_insid, newIns = HTI_FeedTrade_EDD_Util.getInstrument(tradeId, way, qty, price, insLocalCode,
                                                    trdCcy, insMic, insCcy, insDesc, insProdType,
                                                    insMaturity, insPointValue, insStrike, insOptionType,
                                                    insExecType, insBullBear, insBarrier, insOtc, insDeliveryType,
                                                    insUlLocalCode, insUlProdType, insUlMic, insUlInsCcy, insUlDesc,
                                                    fo_system, new_arr_ins, errdict)
                        
    print trd_insid, newIns, new_arr_ins
    '''
    
    '''
    asofdate = '13/11/2015'
    tradeId = 'AaHWEB1-1-SEHK-ORION31015'
    trd_insid = '704@XHKG'
    way = 'S'
    qty = '400'
    price = '5.8'
    trdCcy = 'HKD'    
    
    trdnbr, tradeSituation = HTI_FeedTrade_EDD_Util.createTrade(asofdate, trd_insid, tradeId, way, qty, price, trdCcy, DEFAULT_PF, DEFAULT_CPTY,
                                                        DEFAULT_BKR, DEFAULT_ACQ, DEFAULT_STATUS, DEFAULT_TRADER, fo_system, errdict)
                                                        
    '''
    

def ael_main(dict): 
    '''
    # test email connection
    subject = "Currency price capture"
    body = "Process is run successfully"
    HTI_Email_Util.EmailNotify(subject, body, 'noreply_testing_fa@htisectesting.com')
    return
    '''
    
    ret = ValidateAndFeedTrade(dict, True)
    #ret = test_getInstrument()
