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
'''
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
'''

ael_variables = [['asofdate', 'Date', 'string', [str(ael.date_today()), 'Today'], 'Today', 1, 0, 'Date', None, 1], \
                ['fileName', 'File Name', 'string', None, 'c:\\temp\\HorizonTrade_YYYYMMDD.csv', 1, 0, 'File Name', None, 1], \
                ['acquirers', 'Acquirer(s)', 'string', HTI_Util.getAllAcquirers(), None, 1, 1, 'Acquirer(s)', None, 1], \
                ['success_email_subj', 'Success Email Subject', 'string', None, 'FA (PROD) : FICC Bond Trade File Upload - SUCCESS', 1, 0, 'Sucess Email Subject', None, 1], \
                ['success_emaillist', 'Success Email List', 'string', None, 'louis.ck.wong@htisec.com', 1, 0, 'Success Email List', None, 1], \
                ['successEmail', 'Send Success Email', 'string', HTI_Util.get_yesno(), 'N', 0, 0, 'Send Success Email', None, 1], \
                ['failure_email_subj', 'Failure Email Subject', 'string', None, 'FA (PROD) : FICC Bond Trade File Upload - FAILED', 1, 0, 'Failure Email Subject', None, 1], \
                ['failure_emaillist', 'Failure Email List', 'string', None, 'louis.ck.wong@htisec.com', 1, 0, 'Failure Email List', None, 1], \
                ['failureEmail', 'Send Failure Email', 'string', HTI_Util.get_yesno(), 'N', 0, 0, 'Send Failure Email', None, 1], \
                ['fo_system', 'FO System(s)', 'string', HTI_Util.getAllFOSystems(), 'Horizon', 1, 1, 'FO System(s)', None, 1], \
                ['target_system', 'Target System', 'string', None, 'MSSE', 0, 0, 'MSSE / MSSD / [BLANK]', None, 1], \
                ['tradeinfoonly', 'Trade Info Only', 'string', HTI_Util.get_yesno(), 'N', 0, 0, 'Generate file for Trade Info Only', None, 1]]

def genTradeFile(dict, FeedTrade):    
    ret = True
    
    #tdt = ael.date_today()
    
    asofdate = dict['asofdate']
    if asofdate == 'Today':
        asofdate = ael.date_today()
    else:
        asofdate = ael.date(asofdate)
    
    # Acquirers
    acq_array_list = dict['acquirers']
    
    acq_list = ''
    for acq in acq_array_list:
        if acq_list == '':
            acq_list = "'" + acq + "'"
        else:
            acq_list = acq_list + ",'" + acq + "'"
    
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
    
    tradeinfoonly = dict['tradeinfoonly']
    
    fo_system_list = dict['fo_system']
    fosys_list = ''
    for fosys in fo_system_list:
        if fosys_list == '':
            fosys_list = "'" + fosys + "'"
        else:
            fosys_list = fosys_list + ",'" + fosys+ "'"
    
    fileName = dict['fileName']
    fileName = fileName.replace("YYYYMMDD", asofdate.to_string("%Y%m%d"))
    
    target_system = dict['target_system']
    
    f = open(fileName, "w")
        
    errmsg = ''
    
    asofdate_tmr = asofdate.add_days(1)
    
    rs = None
    try:            
        strSql = """
                select t.trdnbr, as.value
                from trade t, instrument i, portfolio pf, additionalinfo as, additionalinfospec ais, party acq
                where t.creat_time >= '%s' and t.creat_time < '%s'
                and t.insaddr = i.insaddr
                and t.status not in ('Void')
                and t.prfnbr = pf.prfnbr
                and i.otc = 'No'
                and t.acquirer_ptynbr = acq.ptynbr
                and acq.ptyid in (@accquirer_list)
                and t.trdnbr = as.recaddr and as.addinf_specnbr = ais.specnbr and ais.field_name = 'Trade Source'
                and as.value in (@fosys_list)
                and t.trdnbr >= 39227
                order by as.value
                """ % (asofdate.to_string('%Y-%m-%d'), asofdate_tmr.to_string('%Y-%m-%d'))
        
        strSql = strSql.replace('@accquirer_list', acq_list)
        strSql = strSql.replace('@fosys_list', fosys_list)        
        
        print strSql
        rs = ael.asql(strSql)    
        columns, buf = rs
        for table in buf:                        
            for row in table:     
                #print row
                trdnbr = row[0]
                #print 'trdnbrA', trdnbr
                acm_trd = acm.FTrade[trdnbr]
                if acm_trd != None:
                    acm_ins = acm_trd.Instrument()
                    insType = acm_ins.InsType()
                    
                    tradeSource = ''
                    if acm_trd.AdditionalInfo().Trade_Source() != None:            
                        if acm_trd.AdditionalInfo().Trade_Source().strip() != '':
                            tradeSource = acm_trd.AdditionalInfo().Trade_Source().strip()
                    
                    if tradeSource == '':       # skip those without trade source
                        continue
                        
                    #print tradeSource, target_system
                    if tradeSource != target_system:
                        if not HTI_Util.MatchTradeAgainstSystem(target_system, acm_ins):
                            continue
                    
                    #print 'trdnbrB', trdnbr
                    trade_source = ''
                    if acm_trd.AdditionalInfo().Trade_Source() != None:            
                        if acm_trd.AdditionalInfo().Trade_Source().strip() != '':
                            trade_source = acm_trd.AdditionalInfo().Trade_Source().strip()
                    
                    tradeId = ''                    
                    if acm_trd.AdditionalInfo().FO_Trade_Id_1() != None: 
                        if acm_trd.AdditionalInfo().FO_Trade_Id_1().strip() != '':
                            tradeId = acm_trd.AdditionalInfo().FO_Trade_Id_1().strip()
                            if acm_trd.AdditionalInfo().FO_Trade_Id_2() != None:
                                if acm_trd.AdditionalInfo().FO_Trade_Id_2().strip() != '':
                                    tradeId = tradeId + acm_trd.AdditionalInfo().FO_Trade_Id_2().strip()
                                    if acm_trd.AdditionalInfo().FO_Trade_Id_3() != None:
                                        if acm_trd.AdditionalInfo().FO_Trade_Id_3().strip() != '':
                                            tradeId = tradeId + acm_trd.AdditionalInfo().FO_Trade_Id_3().strip()
                                        
                    print trdnbr, acm_ins.Name(), tradeId, insType
                            
                    #tradeId = tradeId.replace(trade_source + '-', '') #remove the trade source appended
                    tradeId = tradeId[0:len(tradeId)-9] # remove the date appended
                    
                    qty = acm_trd.Quantity()        
                    if qty >= 0:
                        way = 'B'
                    else:
                        way = 'S'
                        
                    qty = abs(qty)
                    
                        
                    price = acm_trd.Price()
                    
                    localcode = ''                    
                    if acm_ins.AdditionalInfo().Local_Exchange_Code() != None:       
                        if acm_ins.AdditionalInfo().Local_Exchange_Code().strip() != '':
                            localcode = acm_ins.AdditionalInfo().Local_Exchange_Code().strip()
                            
                    trdCcy = acm_trd.Currency().Name()
                    
                    insMic = ''                    
                    
                    if acm_ins.AdditionalInfo().MIC() != None:          
                        if acm_ins.AdditionalInfo().MIC().strip() != '':
                            insMic = acm_ins.AdditionalInfo().MIC().strip()
                    
                    insCcy = acm_trd.Instrument().Currency().Name()                   
                    
                    insDesc = ''                    
                    if acm_ins.AdditionalInfo().Ins_Description() != None:          
                        if acm_ins.AdditionalInfo().Ins_Description().strip() != '':
                            insDesc = acm_ins.AdditionalInfo().Ins_Description().strip()
                                    
                    trdBkrExchId = ''
                    if target_system != 'Horizon':
                        if acm_trd.AdditionalInfo().MSS_Account() != None:          
                            if acm_trd.AdditionalInfo().MSS_Account().strip() != '':
                                trdBkrExchId = acm_trd.AdditionalInfo().MSS_Account().strip()
                                    
                    trdPfid = ''
                    horizon_user_id = ''
                    timestamp = ''
                    
                    '''
                    if target_system == 'Horizon':
                        if acm_trd.AdditionalInfo().Horizon_Portfolio() != None:            
                            if acm_trd.AdditionalInfo().Horizon_Portfolio().strip() != '':
                                trdPfid = acm_trd.AdditionalInfo().Horizon_Portfolio().strip()
                    else:
                        if acm_trd.AdditionalInfo().AE_Aces_Code() != None:            
                            if acm_trd.AdditionalInfo().AE_Aces_Code().strip() != '':
                                trdPfid = acm_trd.AdditionalInfo().AE_Aces_Code().strip()
                    '''
                    
                    insPointValue = acm_trd.Instrument().ContractSize()
                    
                    #print acm_trd
                    #print acm_trd.TradeTime()[0:10].replace('-', '')
                    if target_system == 'Horizon':
                        trd_td = ''
                        trd_vd = ''
                        if acm_trd.AdditionalInfo().Horizon_Portfolio() != None:            
                            if acm_trd.AdditionalInfo().Horizon_Portfolio().strip() != '':
                                trdPfid = acm_trd.AdditionalInfo().Horizon_Portfolio().strip()
                        
                        if acm_trd.AdditionalInfo().Horizon_User_Id() != None:   
                            if acm_trd.AdditionalInfo().Horizon_User_Id().strip() != '':
                                horizon_user_id = acm_trd.AdditionalInfo().Horizon_User_Id().strip()
                        timestamp = acm_trd.TradeTime().replace('-', '').replace(':', '')
                    else:
                        trd_td = acm_trd.TradeTime()[0:10].replace('-', '')
                        trd_vd = acm_trd.ValueDay()[0:10].replace('-', '')
                        if acm_trd.AdditionalInfo().AE_Aces_Code() != None:            
                            if acm_trd.AdditionalInfo().AE_Aces_Code().strip() != '':
                                trdPfid = acm_trd.AdditionalInfo().AE_Aces_Code().strip()
                    
                    if acm_ins.SettlementType() == 'Physical Delivery':
                        insDeliveryType = 'Physical'
                    else:
                        if insType in ('Stock'):
                            insDeliveryType = 'Physical'
                        else:
                            insDeliveryType = 'Cash'
                    
                    print insType
                    if insType in ('Stock', 'EquityIndex'):
                        insProdType = 'STOCK'
                    elif insType == 'Future/Forward':
                        insProdType = 'FUTURE'
                    elif insType == 'Option':
                        insProdType = 'OPTION'
                    elif insType == 'Warrant':
                        #print 'A', acm_ins.Instrument().Name(), acm_ins.ExoticType()=='None'
                        if acm_ins.ExoticType() == 'None':
                            insProdType = 'WARRANT'
                        else:
                            insProdType = 'CBBC'
                            
                    print 'tradeSource', tradeSource, trdPfid
                    
                    if insType in ('Future/Forward','Option','Warrant'):
                        insMaturity = acm_ins.ExpiryDate()[0:10].replace('-', '')
                        acm_ins_und = acm_ins.Underlying()
                        
                        insUlMic = ''
                        if acm_ins_und.AdditionalInfo().MIC() != None:          
                            if acm_ins_und.AdditionalInfo().MIC().strip() != '':
                                insUlMic = acm_ins_und.AdditionalInfo().MIC().strip()
                        
                        insUlInsCcy = acm_ins_und.Currency().Name()
                        
                        insUlDesc = ''
                        if acm_ins_und.AdditionalInfo().Ins_Description() != None:          
                            if acm_ins_und.AdditionalInfo().Ins_Description().strip() != '':
                                insUlDesc = acm_ins_und.AdditionalInfo().Ins_Description().strip()
                        
                        insUlLocalCode = ''
                        if acm_ins.InsType() != 'Warrant':
                            if acm_ins_und.InsType() == 'EquityIndex':
                                if acm_ins.AdditionalInfo().Commodity_Code() != None:          
                                    if acm_ins.AdditionalInfo().Commodity_Code().strip() != '':
                                        insUlLocalCode = acm_ins.AdditionalInfo().Commodity_Code().strip()
                                        insUlLocalCode = HTI_FeedTrade_EDD_Util.getFullIndexLocalCodeByMapping(insUlLocalCode, insUlMic)
                                        #insUlLocalCode = acm_ins.AdditionalInfo().Commodity_Code().strip()
                            else:
                                if acm_ins_und.AdditionalInfo().Local_Exchange_Code() != None:          
                                    if acm_ins_und.AdditionalInfo().Local_Exchange_Code().strip() != '':
                                        insUlLocalCode = acm_ins_und.AdditionalInfo().Local_Exchange_Code().strip()
                        else:
                            if acm_ins_und.AdditionalInfo().Local_Exchange_Code() != None:          
                                if acm_ins_und.AdditionalInfo().Local_Exchange_Code().strip() != '':
                                    insUlLocalCode = acm_ins_und.AdditionalInfo().Local_Exchange_Code().strip()
                                    
                            if insUlLocalCode != '':
                                if acm_ins_und.InsType() == 'EquityIndex': # because EquityIndex has two commodity codes for normal and mini contracts
                                    sep = ','                                    
                                    comdty_code_array = insUlLocalCode.split(sep)
                                    insUlLocalCode = comdty_code_array[0]                                    
                                
                        if acm_ins_und.InsType() in ('Stock'):
                            insUlProdType = 'STOCK'
                            if acm_ins.InsType() != 'Warrant':
                                insDeliveryType = 'Physical'
                            '''
                            if target_system == 'Horizon':
                                insUlProdType = 'STOCK'
                            else:
                                if acm_ins_und.InsType() == 'Stock':
                                    insUlProdType = 'STOCK'
                                else:
                                    insUlProdType = 'INDEX'
                            '''
                        elif acm_ins_und.InsType() == 'EquityIndex':
                            insUlProdType = 'INDEX'
                        elif acm_ins_und.InsType() == 'Future/Forward':
                            insUlProdType = 'FUTURE'
                        else:
                            insUlProdType = ''
                            
                        insUlName = ''
                        if acm_ins_und.AdditionalInfo().Ins_Short_Name() != None:          
                            if acm_ins_und.AdditionalInfo().Ins_Short_Name().strip() != '':
                                insUlName = acm_ins_und.AdditionalInfo().Ins_Short_Name().strip()
                    else:
                        insMaturity = ''
                        insUlMic = ''
                        insUlInsCcy = ''
                        insUlDesc = ''
                        insUlLocalCode = ''
                        insUlProdType = ''
                        insUlName = ''
                    
                    if insType in ('Option','Warrant'):
                        insStrike = str(acm_ins.StrikePrice())
                        if acm_ins.IsCallOption():
                            if target_system == 'Horizon':
                                insOptionType = 'C'
                            else:
                                insOptionType = 'Call'
                        else:
                            if target_system == 'Horizon':
                                insOptionType = 'P'
                            else:
                                insOptionType = 'Put'
                        if acm_ins.ExerciseType() == 'European':    
                            if target_system == 'Horizon':
                                insExecType = 'E'
                            else:
                                insExecType = 'European'
                        else:
                            if target_system == 'Horizon':
                                insExecType = 'A'
                            else:
                                insExecType = 'American'
                    else:
                        insStrike = ''
                        insOptionType = ''
                        insExecType = ''
                        
                    if insType in ('Warrant'):
                        insIssueSize = str(acm_ins.TotalIssued())
                        insIssueDate = acm_ins.IssueDay()[0:10].replace('-', '')
                    else:
                        insIssueSize = ''
                        insIssueDate = ''
                        
                    if insProdType in ('CBBC'):
                        for exotic in acm_ins.Exotics():
                            if exotic.BarrierOptionType() == 'Up & Out':
                                insBarrierType = 'UPANDOUT'
                            elif exotic.BarrierOptionType() == 'Down & Out':
                                insBarrierType = 'DOWNANDOUT'
                            elif exotic.BarrierOptionType() == 'Down & In':
                                insBarrierType = 'DOWNANDIN'
                            else:
                                insBarrierType = 'UPANDIN'
                            break
                        if insOptionType.upper() in ('CALL', 'C') and insBarrierType == 'UPANDOUT':
                            insBullBear = 'BULL'
                        elif insOptionType.upper() in ('PUT', 'P') and insBarrierType == 'DOWNANDOUT':
                            insBullBear = 'BEAR'
                        else:
                            insBullBear = 'BULL'                        
                        insBarrierLevel = str(acm_ins.Barrier())                        
                    else:
                        insBarrierType = ''
                        insBullBear = ''
                        insBarrierLevel = ''
                    
                    insName = ''
                    if acm_ins.AdditionalInfo().Ins_Short_Name() != None:          
                            if acm_ins.AdditionalInfo().Ins_Short_Name().strip() != '':
                                insName = acm_ins.AdditionalInfo().Ins_Short_Name().strip()
                                
                    if insType in ('Option', 'Future/Forward'):
                        insUnderlying_mktId = acm_ins.AdditionalInfo().Commodity_Code().strip()
                    else:
                        insUnderlying_mktId = ''
                        
                    otc = 'No'
                                   
                    if tradeinfoonly == 'Y':
                        insDesc = ''
                        insProdType = ''
                        insPointValue = ''
                        insStrike = ''
                        insOptionType = ''
                        insExecType = ''
                        insDeliveryType = ''
                        insUlLocalCode = ''
                        insUlProdType = ''
                        insUlMic = ''
                        insUlInsCcy = ''
                        insIssueSize = ''
                        insIssueDate = ''
                        insBarrierType = ''
                        #trdBkrExchId = ''
                        #trdPfid = ''
                        insName = ''
                        insUlName = ''
                        insUnderlying_mktId = ''
                        horizon_user_id = ''
                        timestamp = ''
                        otc = ''
                        insMaturity = ''
                        insUlDesc = ''
                        
                        # the following columns are for MSSD
                        '''
                        COL_MSSD_UNDERLYING = 38
                        COL_MSSD_CALLPUT = 39
                        COL_MSSD_EXP_MONTH = 40
                        COL_MSSD_STRIKE = 41
                        COL_MSSD_POINTVAL = 42
                        '''
                    
                    mssd_underlying = ''
                    mssd_callput = ''
                    mssd_exp_month = ''
                    mssd_strike = ''
                    mssd_pointval = ''
                    
                    if target_system == 'MSSD':
                        # show individual attributes of instrument rather than local code of instrument
                        localcode = ''
                        if acm_ins.Underlying().AdditionalInfo().Local_Exchange_Code() != None:       
                            if acm_ins.Underlying().AdditionalInfo().Local_Exchange_Code().strip() != '':
                                    mssd_underlyings = acm_ins.Underlying().AdditionalInfo().Local_Exchange_Code().strip()
                                    mssd_underlying_list = mssd_underlyings.split(',')                                    
                                    mssd_underlying = mssd_underlying_list[0]
                        
                        if acm_ins.InsType() == 'Option':
                            if acm_ins.IsCallOption():                                
                                mssd_callput = 'CALL'
                            else:
                                mssd_callput = 'PUT'
                            mssd_strike = str(acm_ins.StrikePrice())
                        else:
                            mssd_strike = '0'
                        
                        if acm_ins.ExpiryDate() != None:
                            mssd_exp_month = ael.date(acm_ins.ExpiryDate()[0:10]).to_string("%Y%m")
                                                
                        if acm_ins.ContractSize() != None:
                            mssd_pointval = str(acm_ins.ContractSize())                        
                    
                    if insType in ('Warrant'):
                        if acm_ins.ContractSize() != 0:
                            warrantParity = str(int(1.0 / float(acm_ins.ContractSize())))
                    else:
                        warrantParity = '0'
                    
                    if insType == 'Stock':
                        #25365,S,2000,5.5,8,HKD,XHKG,HKD,PCCW,Stock,,1,,,,,,No,Physical,,,,,,ATP,,,,,01-0241377-00,L98,20151109,20151111,,,
                        detailLine = tradeId + ',' + way + ',' + str(qty) + ',' + str(price) + ',' + localcode + ',' + trdCcy + ',' + insMic + ',' + insCcy + ',' + insDesc + ',' + \
                            insProdType + ',,' + str(insPointValue) + ',,,,,,' + otc + ',' + insDeliveryType + ',,,,,,' + trade_source + ',,,,,' + trdBkrExchId + ',' + trdPfid + ',' + trd_td + ',' + trd_vd + \
                            ',' + insName + ',' + insUlName + ',' + insUnderlying_mktId + ',' + horizon_user_id + ',' + timestamp + ',' + warrantParity
                    elif insType == 'Future/Forward':
                        ulpos = insUlLocalCode.find('@')
                        if ulpos < 0:
                            ulpos= len(insUlLocalCode) - 1                    
                            #25366,B,1,9077,HHIZ5,HKD,XHKF,HKD,FUT Dec15 on HSCEI,Future,20151230,50,,,,,,No,Cash,HHI,Index,XHKG,HKD,HANG SENG CHINA ENTERPRISES IDX.,ATP,,,,,01-0241377-00,L98,20151109,20151111,,,
                            detailLine = tradeId + ',' + way + ',' + str(qty) + ',' + str(price) + ',' + localcode + ',' + trdCcy + ',' + insMic + ',' + insCcy + ',' + insDesc + ',' + \
                                insProdType + ',' + insMaturity + ',' + str(insPointValue) + ',,,,,,' + otc + ',' + insDeliveryType + ',' + insUlLocalCode + ',' + insUlProdType + ',' + \
                                insUlMic + ',' + insUlInsCcy + ',' + insUlDesc + ',' + trade_source + ',,,,,' + trdBkrExchId + ',' + trdPfid + ',' + trd_td + ',' + trd_vd + ',' + \
                                insName + ',' + insUlName + ',' + insUnderlying_mktId + ',' + horizon_user_id + ',' + timestamp +  ',' + warrantParity
                    elif insType == 'Option':
                        #25368,B,2,90,HSI10000L5,HKD,XHKF,HKD,PUT Dec15 on HSI @ 10000,Option,20151230,50,10000,Put,European,,,No,Cash,HSI,Index,XHKG,HKD,HANG SENG INDEX,ATP,,,,,01-0241377-00,L98,20151109,20151111,,,
                        detailLine = tradeId + ',' + way + ',' + str(qty) + ',' + str(price) + ',' + localcode + ',' + trdCcy + ',' + insMic + ',' + insCcy + ',' + insDesc + ',' + \
                            insProdType + ',' + insMaturity + ',' + str(insPointValue) + ',' + insStrike + ',' + insOptionType + ',' + insExecType + ',,,' + otc + ',' + insDeliveryType + ',' + \
                            insUlLocalCode + ',' + insUlProdType + ',' + insUlMic + ',' + insUlInsCcy + ',' + insUlDesc + ',' + trade_source + ',,,,,' + trdBkrExchId + ',' + trdPfid + ',' + \
                            trd_td + ',' + trd_vd + ',' + insName + ',' + insUlName + ',' + insUnderlying_mktId + ',' + horizon_user_id + ',' + timestamp +  ',' + warrantParity
                    elif insType == 'Warrant':
                        insPointValue = 1
                        if insProdType == 'WARRANT':
                            #25371,B,100000,0.035,22698,HKD,XHKG,HKD,CSGEELY@EC1512B,Warrant,20151214,1,4.5,Call,European,,,No,Cash,176,Stock,XHKG,HKD,Geely Autombile Holdings Limited,MSS,1234546.56,20151010,,,01-0241377-00,L98,20151109,20151111,NM-L&F @EC1606A,,
                            detailLine = tradeId + ',' + way + ',' + str(qty) + ',' + str(price) + ',' + localcode + ',' + trdCcy + ',' + insMic + ',' + insCcy + ',' + insDesc + ',' + \
                                insProdType + ',' + insMaturity + ',' + str(insPointValue) + ',' + insStrike + ',' + insOptionType + ',' + insExecType + ',,,' + otc + ',' + insDeliveryType + ',' + \
                                insUlLocalCode + ',' + insUlProdType + ',' + insUlMic + ',' + insUlInsCcy + ',' + insUlDesc + ',' + trade_source + ',' + insIssueSize + ',' + insIssueDate + ',,,' + \
                                trdBkrExchId + ',' + trdPfid + ',' + trd_td + ',' + trd_vd + ',' + insName + ',' + insUlName + ',' + insUnderlying_mktId + ',' + horizon_user_id + ',' + timestamp +  ',' + warrantParity
                        elif insProdType == 'CBBC':
                            #25372,B,1,0.07,69080,HKD,XHKG,HKD,JP#HSI RC1611Z (HSI Bull),CBBC,20151119,1,21750,Call,European,Bull,21950,No,Cash,HSI,Index,XHKG,HKD,HANG SENG INDEX,ATP,999999.15,20150102,upAndOut,,01-0241377-00,L98,20151109,20151111,NM-L&F @EC1606A,,
                            detailLine = tradeId + ',' + way + ',' + str(qty) + ',' + str(price) + ',' + localcode + ',' + trdCcy + ',' + insMic + ',' + insCcy + ',' + insDesc + ',' + \
                                insProdType + ',' + insMaturity + ',' + str(insPointValue) + ',' + insStrike + ',' + insOptionType + ',' + insExecType + ',' + insBullBear + ',' + str(insBarrierLevel) + ',' + otc + ',' + insDeliveryType + ',' + \
                                insUlLocalCode + ',' + insUlProdType + ',' + insUlMic + ',' + insUlInsCcy + ',' + insUlDesc + ',' + trade_source + ',' + insIssueSize + ',' + insIssueDate + ',' + insBarrierType + ',,' + \
                                trdBkrExchId + ',' + trdPfid + ',' + trd_td + ',' + trd_vd + ',' + insName + ',' + insUlName + ',' + insUnderlying_mktId + ',' + horizon_user_id + ',' + timestamp +  ',' + warrantParity
                
                    if target_system == 'MSSD':
                        detailLine = detailLine + ',' + mssd_underlying + ',' + mssd_callput + ',' + mssd_exp_month + ',' + mssd_strike + ',' + mssd_pointval + '\n'
                    else:
                        detailLine = detailLine + '\n'
                    print detailLine
                    f.write(detailLine)
        f.close()
        
        email_content = 'Date: %s' % asofdate.to_string('%Y-%m-%d') + '\n'
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
        email_content = 'Date: %s' % asofdate.to_string('%Y-%m-%d') + '\n'
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
