import ael
import acm
import os
import stat
import time
import shutil
import string
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
COL_INS_LOCAL_CODE = 4
COL_TRD_CCY = 5
COL_INS_MIC = 6
COL_INS_CCY = 7
COL_INS_DESC = 8
COL_INS_TYPE = 9
COL_INS_EXP_DAY = 10
COL_INS_POINT_VAL = 11
COL_INS_STRIKE = 12
COL_INS_OPTION_TYPE = 13
COL_INS_EXERCISE_TYPE = 14
COL_INS_BULL_BEAR = 15
COL_INS_BARRIER = 16
COL_INS_OTC = 17
COL_INS_DELIVERY_TYPE = 18
COL_UL_LOCAL_CODE = 19
COL_UL_TYPE = 20
COL_UL_MIC = 21
COL_UL_CCY = 22
COL_UL_NAME = 23
COL_CHANNEL = 24  
COL_INS_ISSUE_SIZE = 25
COL_INS_ISSUE_DATE = 26
COL_INS_BARRIER_TYPE = 27
COL_TRD_ACQUIRER = 28
COL_TRD_MSS_ACC_ID = 29
COL_TRD_AE_ACES_GRP_CDE = 30
COL_TRD_TD = 31
COL_TRD_VD = 32
COL_INS_NAME = 33
COL_INS_UL_NAME = 34
COL_INS_UNDERLYING_MKTID = 35
COL_USER_ID = 36
COL_TIMESTAMP = 37
    
ael_variables = [['asofdate', 'Date', 'string', HTI_Util.get_dates(), "TODAY", 1, 0, 'Date', None, 1], \
                ['fileName', 'File Name', 'string', None, 'C:\\temp\\test001YYYYMMDD.csv', 1, 0, 'File Name', None, 1], \
                ['own_issuer', 'Own Issuer', 'string', HTI_Util.getAllIssuers(), '', 1, 0, 'Mark this issuer to the warrant issued by us', None, 1], \
                ['success_email_subj', 'Success Email Subject', 'string', None, 'FA (PROD) : EDD MSS Trade File Upload - SUCCESS', 1, 0, 'Sucess Email Subject', None, 1], \
                ['success_emaillist', 'Success Email List', 'string', None, 'louis.ck.wong@htisec.com', 1, 0, 'Success Email List', None, 1], \
                ['successEmail', 'Send Success Email', 'string', HTI_Util.get_yesno(), 'N', 0, 0, 'Send Success Email', None, 1], \
                ['failure_email_subj', 'Failure Email Subject', 'string', None, 'FA (PROD) : EDD MSS Trade File Upload - FAILED', 1, 0, 'Failure Email Subject', None, 1], \
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
    if asofdate == 'TODAY':
        asofdate = tdt.to_string('%Y%m%d')
    else:
        asofdate = ael.date(asofdate).to_string('%Y%m%d')
    
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
    
    fileName = dict['fileName']    
    fileName = fileName.replace("YYYYMMDD", tdt.to_string('%Y%m%d'))
    print 'File Name:', fileName
        
    try:        
        fileStats = os.stat(fileName)
        fileInfo = {
        'Size': fileStats[stat.ST_SIZE],
        'LastModified': time.ctime(fileStats[stat.ST_MTIME]),
        'LastAccessed': time.ctime(fileStats[stat.ST_ATIME]),
        'CreationTime': time.ctime(fileStats[stat.ST_CTIME]),
        'Mode': fileStats[stat.ST_MODE]
        }
                
        print 'Reading trade file ' + fileName
        print 'File date: ' + fileInfo['LastModified']
        print 'Process run date: ' + tdt.to_string('%Y-%m-%d')
        
        errmsg = ''
        ins_creation_cnt = 0
        success_trd_cnt = 0
        fail_trd_cnt = 0
        already_upload_cnt = 0
        skip_trd_cnt = 0
        ttl_trd_cnt = 0
        sep = ','
        
        try:     
            # check file corruption
            fi = open(fileName)
            line = fi.readline()
            linecnt = 0
            pcecnt = 0
            hasTrailer = False
            
            while line.strip() <> "":                 
                data = line.split(sep)
                print data, linecnt
                tradeId = data[COL_TRADE_ID].strip()
                way = data[COL_WAY].strip()
                qty = data[COL_QTY].strip()
                price = data[COL_PRICE].strip()
                insLocalCode = data[COL_INS_LOCAL_CODE].strip()
                trdCcy = data[COL_TRD_CCY].strip()
                insMic = data[COL_INS_MIC].strip()
                insCcy = data[COL_INS_CCY].strip()
                insDesc = data[COL_INS_DESC].strip()
                insProdType = data[COL_INS_TYPE].strip()
                insMaturity = data[COL_INS_EXP_DAY].strip()
                if insMaturity != '':
                    insMaturity = insMaturity[6:8] + '/' + insMaturity[4:6] + '/' + insMaturity[0:4]                
                insPointValue = data[COL_INS_POINT_VAL].strip()
                insStrike = data[COL_INS_STRIKE].strip()
                insOptionType = data[COL_INS_OPTION_TYPE].strip()
                insExecType = data[COL_INS_EXERCISE_TYPE].strip()
                insBullBear = data[COL_INS_BULL_BEAR].strip()
                insBarrier = data[COL_INS_BARRIER].strip()
                insOtc = data[COL_INS_OTC].strip()
                insDeliveryType = data[COL_INS_DELIVERY_TYPE].strip()
                insUlLocalCode = data[COL_UL_LOCAL_CODE].strip()
                insULProdType = data[COL_UL_TYPE].strip()
                insULMic = data[COL_UL_MIC].strip()
                insULCcy = data[COL_UL_CCY].strip()
                insULDesc = data[COL_UL_NAME].strip()
                trdChannel = data[COL_CHANNEL].strip()
                insIssueSize = data[COL_INS_ISSUE_SIZE].strip()
                insIssueDate = data[COL_INS_ISSUE_DATE].strip()                
                if insIssueDate != '':
                    insIssueDate = insIssueDate[6:8] + '/' + insIssueDate[4:6] + '/' + insIssueDate[0:4]    
                insBarrierType = data[COL_INS_BARRIER_TYPE].strip()
                trdMssAcquirer = data[COL_TRD_ACQUIRER].strip()
                trd_mss_acc = data[COL_TRD_MSS_ACC_ID].strip()
                trd_ae_aces_grp_cde = data[COL_TRD_AE_ACES_GRP_CDE].strip()
                trd_td = data[COL_TRD_TD].strip()
                trd_vd = data[COL_TRD_VD].strip()                
                insName = data[COL_INS_NAME].strip()
                insULName = data[COL_INS_UL_NAME].strip()
                insUnderlying_mktId = data[COL_INS_UNDERLYING_MKTID].strip()
                fo_userid = data[COL_USER_ID].strip()
                timestamp = data[COL_TIMESTAMP].strip()
                
                print tradeId, way, qty, price, insLocalCode, trdCcy, insMic, insCcy, insDesc, insProdType, insMaturity, insPointValue, insStrike, insOptionType,  \
                    insExecType, insBullBear, insBarrier, insOtc, insDeliveryType, insUlLocalCode, insULProdType, insULMic, insULCcy, insULDesc, trdChannel, \
                    insIssueSize, insIssueDate, insBarrierType, trdMssAcquirer, trd_mss_acc, trd_ae_aces_grp_cde, trd_td, trd_vd, insName, insULName, insUnderlying_mktId, \
                    fo_userid, timestamp
                
                trdAcquirer = ''
                trdCounterparty = ''
                trdPortfolio = ''
                
                if trd_td != '':
                    trd_td = trd_td[6:8] + '/' + trd_td[4:6] + '/' + trd_td[0:4]
                
                if trd_vd != '':
                    trd_vd = trd_vd[6:8] + '/' + trd_vd[4:6] + '/' + trd_vd[0:4]
                                    
                if trd_mss_acc != '':
                    #trdCounterparty = HTI_FeedTrade_EDD_Util.mapCounterpartyByMSSAcc(trd_mss_acc)
                    if trdChannel == 'Horizon':
                        trdCounterparty = ''    # use default counterparty
                    else:
                        trdCounterparty = ''    # use default counterparty
                        #trdCounterparty = HTI_FeedTrade_EDD_Util.mapCounterparty(trd_mss_acc, 'MSS_ACC_CODE')
                
                print 'trdCounterparty', trdCounterparty
                
                '''
                if trd_ae_aces_grp_cde != '':
                    #trdPortfolio = HTI_FeedTrade_EDD_Util.mapPfByAE_ACES_GRP_CODE(trd_ae_aces_grp_cde)
                    if trdChannel == 'Horizon':
                        trdPortfolio = HTI_FeedTrade_EDD_Util.mapPf(trd_ae_aces_grp_cde, 'HORIZON_PORTFOLIO')                    
                    else:
                        #trdPortfolio = HTI_FeedTrade_EDD_Util.mapPf(trd_ae_aces_grp_cde, 'MSS_AE_ACES_GRP_CDE')
                        #trdPortfolio = HTI_FeedTrade_EDD_Util.mapPf(trd_ae_aces_grp_cde, 'PF_MSS_ACC_CODE')
                        trdPortfolio = HTI_FeedTrade_EDD_Util.mapPf(trd_mss_acc, 'PF_MSS_ACC_CODE')
                        
                print 'trdPortfolio', trdPortfolio
                '''
                
                trdnbr = HTI_FeedTrade_EDD_Util.getTrade(tradeId, trdChannel)
                print 'FO Trade No: %s' % (str(trdnbr))
                
                if trdnbr == -1:    #trade already created in FA                    
                    newIns = False
                    trd_insid = ''
                    
                    #print 'C', insName, OWN_ISSUER, insProdType
                    
                    issuer_ptyid = ''
                    if insProdType in ('CBBC', 'Warrant'):
                        if HTI_FeedTrade_EDD_Util.getIssuerByWarrantName(insName, 'WARRANT_ISSUER_NAME') == OWN_ISSUER:
                            issuer_ptyid = OWN_ISSUER  

                    print 'D'
                    
                    trd_insid, newIns = HTI_FeedTrade_EDD_Util.getInstrument(tradeId, way, qty, price, insLocalCode,
                                                    trdCcy, insMic, insCcy, insDesc, insProdType,
                                                    insMaturity, insPointValue, insStrike, insOptionType,
                                                    insExecType, insBullBear, insBarrier, insOtc, insDeliveryType,
                                                    insUlLocalCode, insULProdType, insULMic, insULCcy, insULDesc,
                                                    trdChannel, insIssueSize, insIssueDate, insBarrierType, 
                                                    issuer_ptyid, insName, insULName, insUnderlying_mktId, new_arr_ins, errdict)
                    #if newIns and trd_insid == '':
                    #    print 'Created new instrument %s' % (trd_insid)
                    #    ins_creation_cnt = ins_creation_cnt + 1
                    
                    if trd_ae_aces_grp_cde != '':
                        if trdChannel == 'Horizon':
                            trdPortfolio = HTI_FeedTrade_EDD_Util.mapPf(trd_ae_aces_grp_cde, 'HORIZON_PORTFOLIO')                    
                        else:
                            #trdPortfolio = HTI_FeedTrade_EDD_Util.mapPf(trd_mss_acc, 'PF_MSS_ACC_CODE')
                            trdPortfolio = HTI_FeedTrade_EDD_Util.mapPfByMssAcc(trd_mss_acc, trd_insid)
                        
                    print 'trdPortfolio', trdPortfolio
                    
                    trdnbr = -1
                    tradeSituation = ''
                    
                    print 'H', trd_insid      
                    print trd_td, trd_vd
                    
                    trdnbr, tradeSituation = HTI_FeedTrade_EDD_Util.createTrade(asofdate, trd_insid, tradeId, way, qty, price, trdCcy, DEFAULT_PF, DEFAULT_CPTY,
                                                        DEFAULT_BKR, DEFAULT_ACQ, DEFAULT_STATUS, DEFAULT_TRADER, trdChannel, trdAcquirer, trdCounterparty, 
                                                        trdPortfolio, trd_td, trd_vd, trd_mss_acc, trd_ae_aces_grp_cde, fo_userid, timestamp, errdict)
                    
                    print 'I'
                    if tradeSituation == 'Success' and trdnbr != -1:
                        print 'Created new trade FO:%s (%s), FA:%s' % (tradeId, trdChannel, str(trdnbr))
                        success_trd_cnt = success_trd_cnt + 1
                    #elif tradeSituation == 'Exist' and trdnbr != -1:
                    #    print 'Trade %s is already exist FO:%s, FA:%s' % (tradeId, str(trdnbr))
                    #    already_upload_cnt = already_upload_cnt + 1
                    elif tradeSituation == 'Fail':
                        print 'FO Trade %s (%s) is failed to upload' % (tradeId, trdChannel)
                        fail_trd_cnt = fail_trd_cnt + 1
                    else:
                        print 'FO Trade %s (%s) is skipped' % (tradeId, trdChannel)
                        skip_trd_cnt = skip_trd_cnt + 1
                else:
                    print 'Trade is already exist FO:%s (%s), FA:%s' % (tradeId, trdChannel, str(trdnbr))
                    already_upload_cnt = already_upload_cnt + 1
                
                ttl_trd_cnt = ttl_trd_cnt + 1
                linecnt = linecnt + 1                
                line = fi.readline()                          
                
            fi.close() 
            
            print errdict
            validationErr = HTI_FeedTrade_EDD_Util.LoopValidationErrMsg(errdict)
            errmsg = errmsg + '\n' + validationErr
            
            ins_creation_cnt = len(new_arr_ins)
            
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
                    HTI_Email_Util.EmailNotify(subject, msg, FAILURE_RECIPIENTS)
                else:
                    print subject
                    print str(FAILURE_RECIPIENTS)
                    print msg
                ret = False
            else:
                msg = msg + '\n' + 'No Error'
                msg = msg + '\n\n' + new_ins_msg
                subject = successSubject
                if send_successEmail == 'Y':
                    HTI_Email_Util.EmailNotify(subject, msg, SUCCESS_RECIPIENTS)                    
                else:
                    print subject
                    print str(SUCCESS_RECIPIENTS)
                    print msg
        finally:      
            if fi.closed == False:
                fi.close()                
            else:
                fi.close()      

            return ret
    except IOError:        
        errmsg = 'Date: %s' % tdt.to_string('%Y-%m-%d') + '\n'
        errmsg = errmsg + 'Error:' + '\n\t' + fileName + ' does not exist.'
        if send_failureEmail == 'Y':
            HTI_Email_Util.EmailNotify(errSubject, errmsg, FAILURE_RECIPIENTS)
        else:
            print errSubject
            print errmsg
            print FAILURE_RECIPIENTS
    except OSError:
        errmsg = 'Date: %s' % tdt.to_string('%Y-%m-%d') + '\n'
        errmsg = errmsg + 'Error:' + '\n\t' + fileName + ' does not exist.'
        if send_failureEmail == 'Y':
            HTI_Email_Util.EmailNotify(errSubject, errmsg, FAILURE_RECIPIENTS)
        else:
            print errSubject
            print errmsg
            print FAILURE_RECIPIENTS
        

def ael_main(dict):
    '''
    # test email connection
    subject = "Currency price capture"
    body = "Process is run successfully"
    HTI_Email_Util.EmailNotify(subject, body, 'noreply_testing_fa@htisectesting.com')
    return
    '''
    
    ret = ValidateAndFeedTrade(dict, True)
