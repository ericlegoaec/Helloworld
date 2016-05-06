import ael
import acm
import HTI_ExcelReport2
import HTI_FeedTrade_EDD_Util
import HTI_Util
import os

COL_INS_DESC = 0
COL_LOCAL_EXCH_CODE = 1
COL_BUY_POS = 2
COL_BUY_AVG_PRICE = 3
COL_SELL_POS = 4
COL_SELL_AVG_PRICE = 5
COL_OUTSTANDING_IN_MARKET = 6
COL_TTL_ISSUED = 7
COL_PERCENT_IN_MARKET = 8
COL_INS_CCY = 9
COL_MEET_ACTIVE_QUOTE = 10

RPT_DAILY_TRADING_SUMMARY = "Daily Trading Summary of Derivative Warrants"
RPT_PRELIST_TRADING_SUMMARY = "Pre Listing Trading Summary of Derivative Warrants"

def getAllReports():
    rpts = []
    rpts.append(RPT_DAILY_TRADING_SUMMARY)
    rpts.append(RPT_PRELIST_TRADING_SUMMARY)
    rpts.sort()
    return rpts
    

ael_variables = [['posdate', 'Date', 'string', [str(ael.date_today()), 'Today'], 'Today', 1, 0, 'Position Date', None, 1], \
                ['acquirers', 'Acquirers', 'string', HTI_Util.getAllAcquirers(), 'HTISEC - FICC', 1, 1, 'Acquirers', None, 1], \
                ['counterparties', 'Counterparties', 'string', HTI_Util.getAllParties(), None, 0, 1, 'Counterparties', None, 1], \
                ['pf', 'Portfolios', 'FPhysicalPortfolio', HTI_Util.getAllPortfolios(), '', 0, 1, 'Choose the portfolios to report', None, 1], \
                ['issuer', 'Issuer', 'string', HTI_Util.getAllIssuers(), 'Haitong Intl Financial Product - Issuer', 0, 0, 'Issuer', None, 1], \
                ['calendar', 'Calendar', 'string', HTI_Util.getAllCalendar(), 'Target', 1, 0, 'Calendar to get the banking day', None, 1], \
                ['rptname', 'Report Name', 'string', getAllReports(), RPT_DAILY_TRADING_SUMMARY, 1, 0, 'Report Name', None, 1], \
                ['revised', 'Revised (Y/N)', 'string', HTI_Util.get_yesno(), 'N', 0, 0, 'Revised (Y/N)', None, 1], \
                ['exporttofile', 'ExportToFile', 'string', None, '', 0, 0, 'Export To File', None, 1]]

def get_addInfo(entity, addinfo_name):
    try:
        return entity.add_info(addinfo_name)
    except:
        return ""
    
def get_insInfo(posdate, acq_list, pty_list, pf_list, issuer, rptname):
    all_warrant_info_dict = {}
    
    acq_str = ''
    pty_str = ''
    pf_str = ''
    issuer_str = ''
    
    if acq_list != '':
        acq_str = 'and acq.ptyid in (%s)' % (acq_list)
    
    if pty_list != '':
        pty_str = 'and cpty.ptyid in (%s)' % (pty_list)
    
    if pf_list != '':
        pf_str = 'and pf.prfid in (%s)' % (pf_list)
        
    if issuer != '':
        issuer_str = 'and issuer.ptyid = \'%s\'' % (issuer)

    
    if rptname == RPT_DAILY_TRADING_SUMMARY:
        strSql = """
                select i.insid
                from instrument i, trade t, party cpty, party acq, portfolio pf, party issuer
                where i.insaddr = t.insaddr
                and i.instype = 'Warrant'
                and i.exp_day > '%s'
                and t.status not in ('Void', 'Simulated')
                and t.counterparty_ptynbr = cpty.ptynbr
                and t.acquirer_ptynbr = acq.ptynbr
                and t.prfnbr = pf.prfnbr
                and i.issuer_ptynbr *= issuer.ptynbr
                %s
                %s
                %s
                %s
                group by i.insid""" % (posdate.to_string('%Y-%m-%d'), acq_str, pty_str, pf_str, issuer_str)
    elif rptname == RPT_PRELIST_TRADING_SUMMARY:
        strSql = """
            select i.insid
            from instrument i
            where i.instype = 'Warrant'  
            and i.issue_day = '%s'
            and i.exp_day > '%s'""" % (posdate.to_string('%Y-%m-%d'), posdate.to_string('%Y-%m-%d'))
            
    print strSql
    rs = ael.asql(strSql)
    columns, buf = rs
    for table in buf: 
        for row in table:
            insid = row[0].strip()
            ael_ins = ael.Instrument[insid]
            total_issued = ael_ins.total_issued
            ins_desc = get_addInfo(ael_ins, 'Ins Description')
            meetActiveQuote = get_addInfo(ael_ins, 'Meet Active Quote')
            if meetActiveQuote != 'Yes':
                meetActiveQuote = ''
                
            localExchCode = get_addInfo(ael_ins, 'Local Exchange Code')
            curr_insid = ael_ins.curr.insid.strip()
            warrant_info_array = [ins_desc, localExchCode, '0', '0.00', '0', '0.00', 0, str(total_issued), '0.00%', curr_insid, meetActiveQuote]
            all_warrant_info_dict[insid] = warrant_info_array
    
    print all_warrant_info_dict
    return all_warrant_info_dict
    
def get_ins_qty_and_avgprice(tf_id, all_warrant_info_dict, asofdate):
    context = acm.GetDefaultContext()
    sheet_type = 'FPortfolioSheet'
    
    if asofdate == 'Today':
        posdate = ael.date_today()
    else:
        posdate = ael.date[asofdate]
    
    asofdate_minus1 = posdate.add_days(-1)

    #create CalculationSpace (Virtual Trading Manager)
    calc_space = acm.Calculations().CreateCalculationSpace(context, sheet_type)
    
    try:
        #simulate sheet settings
        calc_space.SimulateGlobalValue( 'Portfolio Profit Loss Start Date', 'Inception' )
        #calc_space.SimulateGlobalValue( 'Portfolio Profit Loss Start Date', 'Custom Date' )
        #calc_space.SimulateGlobalValue( 'Portfolio Profit Loss Start Date Custom', asofdate_minus1 )
        calc_space.SimulateGlobalValue( 'Portfolio Profit Loss End Date', 'Custom Date' )    
        calc_space.SimulateGlobalValue( 'Portfolio Profit Loss End Date Custom', asofdate )
        calc_space.SimulateGlobalValue( 'Valuation Date', asofdate )
        
        tf = ael.TradeFilter[tf_id]
        
        #add item to portfolio sheet
        nacmTf = acm.FTradeSelection[tf.fltid]
        top_node = calc_space.InsertItem(nacmTf)
        calc_space.Refresh()
                
        tf_iter = calc_space.RowTreeIterator().FirstChild()
        ins_iter = tf_iter.FirstChild()
        
        while ins_iter:
            row = ins_iter.Tree().Item()   
            pos = float(calc_space.CalculateValue(row, 'Portfolio Position'))
            avg_price = float(calc_space.CalculateValue(row, 'Portfolio Average Price'))
            insid = str(row).replace("'", "")            
            ins_array = all_warrant_info_dict[insid]

            if tf_id == 'TF_BUY_WARRANT':
                '''
                if pos >= 0:
                    ins_array[COL_BUY_POS] = str(pos)
                else:
                    ins_array[COL_BUY_POS] = '(' + str(abs(pos)) + ')'
                '''
                ins_array[COL_BUY_POS] = str(pos)
                ins_array[COL_BUY_AVG_PRICE] = str(avg_price)
            elif tf_id == 'TF_SELL_WARRANT':
                '''
                if pos >= 0:
                    ins_array[COL_SELL_POS] = str(pos)
                else:
                    ins_array[COL_SELL_POS] = '(' + str(abs(pos)) + ')'
                '''
                ins_array[COL_SELL_POS] = str(pos)
                ins_array[COL_SELL_AVG_PRICE] = str(avg_price)
            elif tf_id == 'TF_EDD_WARRANT':
                ttl_issue = float(ins_array[COL_TTL_ISSUED])
                #ins_array[COL_OUTSTANDING_IN_MARKET] = str(ttl_issue-pos)       
                ins_array[COL_OUTSTANDING_IN_MARKET] = str(-pos)
                ins_array[COL_PERCENT_IN_MARKET]= str(float(ins_array[COL_OUTSTANDING_IN_MARKET]) / float(ins_array[COL_TTL_ISSUED]) * 100) + '%'
            
            all_warrant_info_dict[insid] = ins_array
            ins_iter = ins_iter.NextSibling()
            
        '''
        for i in all_warrant_info_dict:
            insid = i
            print insid
        return all_warrant_info_dict
        '''
        return all_warrant_info_dict
    except:
        print 'Fail'
        return all_warrant_info_dict
        
class ReportLayout(HTI_ExcelReport2.CommonLayoutReport):
    title = ''
    posdate = None
    issuer_name = ''
    revised = 'N'
    calendar = ''
    
    RPT_DAILY_TRADING_SUMMARY = "Daily Trading Summary of Derivative Warrants"
    RPT_PRELIST_TRADING_SUMMARY = "Pre Listing Trading Summary of Derivative Warrants"

    def __init__(self, title, posdate, issuer_name, revised, calendar):
        self.title = title
        self.posdate = posdate
        self.issuer_name = issuer_name
        self.revised = revised
        self.calendar = calendar
        HTI_ExcelReport2.CommonLayoutReport.__init__(self)
                    
    def reportHeader(self, currentRow, reportIndex, excelApp):
        # Write title        
        excelApp.Cells(currentRow[self.ROW], 1).Value = self.title
        excelApp.Cells(currentRow[self.ROW], 1).Font.Bold = True
        
        currentRow[self.ROW] = currentRow[self.ROW] + 1
        HTI_ExcelReport2.CommonLayoutReport.reportHeader(self, currentRow, reportIndex, excelApp)    
        
        #excelApp.Columns(9).NumberFormat = "#,##0.00"

    def reportEnd(self, excelApp):        
        HTI_ExcelReport2.CommonLayoutReport.reportEnd(self, excelApp)
        
        excelApp.Columns("A:K").Select()
        excelApp.Selection.HorizontalAlignment = HTI_ExcelReport2.ExcelConstant.xlLeft
        
        excelApp.Rows("1").Select()     # Remove the report name
        excelApp.Selection.Delete()
        
        i=1
        while i <= 9:        
            excelApp.Range("A1").EntireRow.Insert()
            i=i+1
            
        excelApp.Range("A11").EntireRow.Insert()
        excelApp.Range("A11").Value = "--------------------------------------------------------------"
        excelApp.Range("B11").Value = "------------------------"
        excelApp.Range("C11").Value = "--------------------------------------------------------------"
        excelApp.Range("D11").Value = "--------------------------------------------------------------"
        excelApp.Range("E11").Value = "--------------------------------------------------------------"
        excelApp.Range("F11").Value = "--------------------------------------------------------------"
        excelApp.Range("G11").Value = "--------------------------------------------------------------"
        excelApp.Range("H11").Value = "--------------------------------------------------------------"
        excelApp.Range("I11").Value = "--------------------------------------------------------------"
        excelApp.Range("J11").Value = "--------------------------------------------------------------"
        excelApp.Range("K11").Value = "-------------------------"
                
        excelApp.Range("A1").Value = self.issuer_name
        excelApp.Range("A2").Value = self.title
        excelApp.Range("A4:K4").Merge()
        
        if self.title == self.RPT_DAILY_TRADING_SUMMARY:
            excelApp.Range("A4").Value = "The Issuer is committed to providing active quotes for only those warrants that satisfy the criteria as set out in paragraph 4.8 of the Industry Principles based on a real time basis.\nYou may access the Industry Principles at http://www.hkex.com.hk/eng/prod/secprod/dwrc/Documents/principle.pdf.\n\nNote:  Column K shows historic information based on market data as of close of trading on the Trade Date specified in this Daily Trading Summary and is for investors’ general information only.\nInvestors should not rely on this list as an indication that a product marked with “Yes” actually meets the active quote criteria at any other time.  If you want to know whether a particular warrant is\neligible for active quotes at any particular time on a trading day, you should contact the Issuer at its enquiry hotline to ask if such warrant meets the active quote criteria."
            excelApp.Range("A6").Value = "The Stock Exchange of Hong Kong Limited received notifications regarding the daily trading summary of Derivative Warrants as follows:-"
        elif self.title == self.RPT_PRELIST_TRADING_SUMMARY:
            excelApp.Range("A4").Value = "The Issuer is committed to providing active quotes for only those warrants that satisfy the criteria as set out in paragraph 4.8 of the Industry Principles based on a real time basis.\nYou may access the Industry Principles at http://www.hkex.com.hk/eng/prod/secprod/dwrc/Documents/principle.pdf.\n\nNote:  Column K only shows historic information based on market data as of close of trading on the Trade Date immediately preceding the Listing Date specified in this Pre Listing Daily Trading\nSummary and is for investors’ general information only. Investors should not rely on this list as an indication that a product marked with “Yes” actually meets the active quote criteria at any other time.\nIf you want to know whether a particular warrant is eligible for active quotes at any particular time on a trading day, you should contact the Issuer at its enquiry hotline to ask if such warrant meets the active quote criteria."
            excelApp.Range("A6").Value = "The Stock Exchange of Hong Kong Limited received notifications regarding the pre listing trading summary of Derivative Warrants as follows:-"
            
        excelApp.Range("A4").EntireRow.RowHeight = 120
        if self.title == self.RPT_DAILY_TRADING_SUMMARY:
            excelApp.Range("A8").Value = "Trade Date:-"
            print self.posdate
            #excelApp.Range("B8").Value = str(self.posdate)
        elif self.title == self.RPT_PRELIST_TRADING_SUMMARY:
            excelApp.Range("A8").Value = "Derivative Warrants Listing Date:-"
            
            print self.calendar
            ael_cal = ael.Calendar[self.calendar]
            print self.posdate.add_banking_day(ael_cal, 1)
            self.posdate = self.posdate.add_banking_day(ael_cal, 1)
            
        pos_date_ymd = self.posdate.to_ymd()
        yy = str(pos_date_ymd[0])
        mm = pos_date_ymd[1]
        if mm < 10:
            mm = '0' + str(mm)
        else:
            mm = str(mm)
        dd = pos_date_ymd[2]
        if dd < 10:
            dd = '0' + str(dd)
        else:
            dd = str(dd)
        
        print yy, mm, dd, dd+mm+yy
        excelApp.Range("B8").Value = dd+mm+yy       
        #excelApp.Range("B8").NumberFormat = "mmddyyyy"            
        if self.revised == 'Y':
            excelApp.Range("C8").Value = "(Revised)"
        
        excelApp.Range("A1").EntireColumn.ColumnWidth = 40
        
        excelApp.Columns("C").NumberFormat = "#,##0_);(#,##0)"        
        excelApp.Columns("E").NumberFormat = "#,##0_);(#,##0)"
        excelApp.Columns("G").NumberFormat = "#,##0_);(#,##0)"
        excelApp.Columns("H").NumberFormat = "#,##0_);(#,##0)"
        
        excelApp.Cells(1, 1).Select()       

def ael_main(dict):
    asofdate = dict['posdate']
    if asofdate == 'Today':
        posdate = ael.date_today()
    else:
        posdate = ael.date[asofdate]
        
    # Acquirers
    acq_array_list = dict['acquirers']
    
    acq_list = ''
    for acq in acq_array_list:
        if acq_list == '':
            acq_list = "'" + acq + "'"
        else:
            acq_list = acq_list + ",'" + acq + "'"
    
    pty_array_list = dict['counterparties']
    
    pty_list = ''
    for pty in pty_array_list:
        if pty_list == '':
            pty_list = "'" + pty + "'"
        else:
            pty_list = pty_list + ",'" + pty + "'"
            
    exporttofilepath = dict['exporttofile']
    exporttofilepath = exporttofilepath.replace("YYYYMMDD", posdate.to_string("%Y%m%d"))
    
    # Portfolios
    portfolios = dict['pf'] 
    
    portfolioList2 = []
    pf_list = ''
    portfolioList2.extend(portfolios)
    for port in portfolioList2:
        prfid = str(port.Name())
        pfarr = []
        pPf = ael.Portfolio[prfid]
        HTI_FeedTrade_EDD_Util.getChildPortfolio(pPf, pfarr)  
        if len(pfarr) > 0:
            for pf in pfarr:                
                if len(pf_list) != 0:          
                    pf_list = pf_list + ','                
                pf_list = pf_list + "'" + pf + "'"
        else:
            if len(pf_list) != 0:  
                pf_list = pf_list + ','                
            pf_list = pf_list + "'" + prfid + "'"
            
    # Issuers
    issuer = dict['issuer']
    
    # Report Name
    rptname = dict['rptname']
    
    # Revised
    revised = dict['revised']
    
    # Calendar
    calendar = dict['calendar']
    
    all_warrant_info_dict = get_insInfo(posdate, acq_list, pty_list, pf_list, issuer, rptname)
    #print all_warrant_info_dict
    
    if acq_list != '':
        acq_str = 'and acq.ptyid in (%s)' % (acq_list)
    else:
        acq_str = ''
    
    if pty_list != '':
        pty_str = 'and cpty.ptyid in (%s)' % (pty_list)
    else:
        pty_str = ''
    
    if pf_list != '':
        pf_str = 'and pf.prfid in (%s)' % (pf_list)
    else:
        pf_str = ''
        
    issuer_str = ''
    
    if issuer != '':
        issuer_str = 'and issuer.ptyid = \'%s\'' % (issuer)
        
    strSql = """
            select t.trdnbr
            from instrument i, trade t, party acq, portfolio pf, party pty, party issuer
            where i.insaddr = t.insaddr
            and i.instype = 'Warrant'
            and i.exp_day > '@exp_dt'
            and t.status not in ('Void', 'Simulated')
            and t.acquirer_ptynbr = acq.ptynbr
            and t.counterparty_ptynbr = pty.ptynbr
            and i.issuer_ptynbr *= issuer.ptynbr
            and t.prfnbr = pf.prfnbr
            and t.quantity @compare_sign 0
            @pty_str
            @acq_str
            @pf_str
            @issuer_str
            @trade_time_str
            """
            
    dt = posdate.to_string('%Y-%m-%d')
    dt_plus1 = posdate.add_days(1).to_string('%Y-%m-%d')
    strBuySql = strSql.replace('@accquirer_list', acq_list)
    strBuySql = strBuySql.replace('@compare_sign', '>=')
    strBuySql = strBuySql.replace('@exp_dt', dt)
    strBuySql = strBuySql.replace('@pty_str', pty_str)
    strBuySql = strBuySql.replace('@acq_str', acq_str)
    strBuySql = strBuySql.replace('@pf_str', pf_str)
    strBuySql = strBuySql.replace('@issuer_str', issuer_str)
    strBuySql = strBuySql.replace('@trade_time_str', "and t.time >= '@dt' and t.time < '@d_plus1'")    
    #strBuySql = strBuySql.replace('@trade_time_str', "and t.time < '@d_plus1'")    
    strBuySql = strBuySql.replace('@dt', dt)
    strBuySql = strBuySql.replace('@d_plus1', dt_plus1)
    
    print 'strBuySql', strBuySql
    
    tobject = ael.TextObject.read('type="SQL Query" and name="%s"' % ('tf_buy_warrant_qry'))
    tobject_c = tobject.clone()    
    tobject_c.set_text(strBuySql)
    tobject_c.commit()
    ael.poll()
    
    
    strSellSql = strSql.replace('@accquirer_list', acq_list)
    strSellSql = strSellSql.replace('@compare_sign', '<')
    strSellSql = strSellSql.replace('@exp_dt', posdate.to_string('%Y-%m-%d'))
    strSellSql = strSellSql.replace('@pty_str', pty_str)
    strSellSql = strSellSql.replace('@acq_str', acq_str)
    strSellSql = strSellSql.replace('@pf_str', pf_str)
    strSellSql = strSellSql.replace('@issuer_str', issuer_str)
    strSellSql = strSellSql.replace('@trade_time_str', "and t.time >= '@dt' and t.time < '@d_plus1'")    
    #strSellSql = strSellSql.replace('@trade_time_str', "and t.time < '@d_plus1'")
    strSellSql = strSellSql.replace('@dt', dt)
    strSellSql = strSellSql.replace('@d_plus1', dt_plus1)
    
    print 'strSellSql', strSellSql
    
    tobject = ael.TextObject.read('type="SQL Query" and name="%s"' % ('tf_sell_warrant_qry'))
    tobject_c = tobject.clone()    
    tobject_c.set_text(strSellSql)
    tobject_c.commit()
    ael.poll()
    
    all_warrant_info_dict = get_ins_qty_and_avgprice('TF_BUY_WARRANT', all_warrant_info_dict, asofdate)
    all_warrant_info_dict = get_ins_qty_and_avgprice('TF_SELL_WARRANT', all_warrant_info_dict, asofdate)
    
    strTtlSql = strSql.replace('@accquirer_list', acq_list)
    strTtlSql = strTtlSql.replace('@compare_sign', '~=')
    strTtlSql = strTtlSql.replace('@exp_dt', posdate.to_string('%Y-%m-%d'))
    strTtlSql = strTtlSql.replace('@pty_str', pty_str)
    strTtlSql = strTtlSql.replace('@acq_str', acq_str)
    strTtlSql = strTtlSql.replace('@pf_str', pf_str)
    strTtlSql = strTtlSql.replace('@issuer_str', issuer_str)
    #strTtlSql = strTtlSql.replace('@trade_time_str', ' ')
    strTtlSql = strTtlSql.replace('@trade_time_str', "and t.time < '@d_plus1'")
    strTtlSql = strTtlSql.replace('@dt', dt)
    strTtlSql = strTtlSql.replace('@d_plus1', dt_plus1)
    
    print 'strTtlSql', strTtlSql
    
    tobject = ael.TextObject.read('type="SQL Query" and name="%s"' % ('tf_edd_warrant_qry'))
    tobject_c = tobject.clone()    
    tobject_c.set_text(strTtlSql)
    tobject_c.commit()
    ael.poll()
        
    all_warrant_info_dict = get_ins_qty_and_avgprice('TF_EDD_WARRANT', all_warrant_info_dict, asofdate)
    
    print all_warrant_info_dict
    
    rptContent = []
    for warrant_info in all_warrant_info_dict:
        row = all_warrant_info_dict[warrant_info]
        rptContent.append(row)
    
    font = HTI_ExcelReport2.Font()
    font.bold = True    
    reportData = HTI_ExcelReport2.ReportData()
    reportData.newSheet = True
    
    reportData.headerText = ['Stock Short Name', 'Stock Code', 'Number of Derivative Warrants Bought', \
            'Average Price per Derivative Warrant Bought', 'Number of Derivative Warrants (Sold)', 'Average Price per Derivative Warrant (Sold)', \
            'Number of Derivative Warrants Still out in Market', 'Total Issue Size', 'Percent of Issue Still out in Market', 'Trading Currency', \
            'Meet Active Quote']
        
    #title = 'Daily Trading Summary Report asof ' + posdate.to_string('%d/%m/%Y')
    title = rptname
        
    if issuer.strip() != '':
        ael_issuer = ael.Party[issuer]
        issuer_name = ael_issuer.fullname
    else:
        issuer_name = ''
    
    report = ReportLayout(title, posdate, issuer_name, revised, calendar)
    rptContent.sort(CompareByTradeNo)
    reportData.rows = rptContent
    report.addReportData(reportData, {'SUM': [], 'COL_TEXT': [], 'CUSTOM_TEXT': {'COL': [], 'TEXT': []}})
    if exporttofilepath.strip() == '':
        report.show()
    else:
        try:
            os.remove(exporttofilepath)
        except:
            pass 
        report.save(exporttofilepath)

def CompareByTradeNo(x, y):
    # currency    
    if int(x[COL_LOCAL_EXCH_CODE]) > int(y[COL_LOCAL_EXCH_CODE]):
        return 1
    elif int(x[COL_LOCAL_EXCH_CODE]) < int(y[COL_LOCAL_EXCH_CODE]):
        return -1    
    else:
        return 0
