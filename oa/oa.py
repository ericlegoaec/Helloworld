#!/usr/bin/env python  
# -*- coding: utf-8 -*-  
import win32com.client
import os
from xlrd import open_workbook, xldate_as_tuple
from datetime import datetime
import shutil
 
#---------------------------------------------------------------------------
class easyExcel:
    '''
    Some convenience methods for Excel documents accessed
    through COM.
    '''
    def __init__(self, filename=None):
        '''
        Create a new application
        if filename is None, create a new file
        else, open an exsiting one
        '''
        self.xlApp = win32com.client.gencache.EnsureDispatch('Excel.Application')
        self.xlApp.Visible = False
        if filename:
            self.filename = filename  
            self.xlBook = self.xlApp.Workbooks.Open(filename)  
        else:  
            self.xlBook = self.xlApp.Workbooks.Add()  
            self.filename = ''    
    def visible(self,visible = True):
        '''
        if Visible is true, the applicaion is visible
        '''
        self.Visible = visible
    def save(self, newfilename=None):
        '''
        if filename is None, save the openning file
        else save as another file used the given name
        '''
        if newfilename:
            self.filename = newfilename  
            self.xlBook.SaveAs(newfilename)  
        else:  
            self.xlBook.Save()      
    def close(self):
        '''
        Close the application
        '''
        self.xlBook.Close(SaveChanges=0)  
        del self.xlApp  
    def getCell(self, sheet, row, col):  
        '''
        Get value of one cell
        '''
        sht = self.xlBook.Worksheets(sheet)  
        return sht.Cells(row, col).Value  
    def setCell(self, sheet, row, col, value):  
        '''
        Set value of one cell
        '''
        sht = self.xlBook.Worksheets(sheet)  
        sht.Cells(row, col).Value = value 
    def getRange(self,sheet,row1,col1,row2,col2):
        '''
        Return a 2d array (i.e. tuple of tuples)
        '''
        sht = self.xlBook.Worksheets(sheet)
        return sht.Range(sht.Cells(row1,col1),sht.Cells(row2,col2)).Value
    def setRange(self,sheet,leftCol,topRow,data):
        '''
        Insert a 2d array starting at given location.
        i.e. [['a','b','c'],['a','b','c'],['a','b','c']]
        Works out the size needed for itself
        '''
        bottomRow = topRow + len(data) - 1
        rightCol = leftCol + len(data[0]) - 1
        sht = self.xlBook.Worksheets(sheet)
        sht.Range(sht.Cells(topRow, leftCol), sht.Cells(bottomRow, rightCol)).Value = data   


outname = "Accounts Position Auto version.xlsx"
outname = os.getcwd() + "\\" + outname
# backup Accounts file
shutil.copy(outname, outname.split(".")[0]+"_bak.xlsx")

sec_name = "Securities AC Portfolio 20140701.xls"
sec_name = os.getcwd() + "\\" + sec_name 

fea_name = "Futures AC Portfolio 20140701.xls"
fea_name = os.getcwd() + "\\" + fea_name

book_acc = open_workbook(outname)
book_sec = open_workbook(sec_name)
book_fea = open_workbook(fea_name)

sheet_sec = book_sec.sheet_by_index(0)
sheet_fea = book_fea.sheet_by_index(0)

        
if __name__ == "__main__":
    wlist = []

    for r in range(1, sheet_sec.nrows):
        date_value = xldate_as_tuple(sheet_sec.cell(r,0).value, book_sec.datemode)
        t = datetime(*date_value)
        currency = sheet_sec.cell(r, 3).value.strip()
        # print currency
        s = sheet_sec.cell(r, 2).value
        ab = sheet_sec.cell(r, 7).value
        mv = sheet_sec.cell(r, 9).value
        # print t, s, currency

        #! Decide s in or not in the ACC exceil file
        snames = book_acc.sheet_names()
        if s not in snames:
            continue
        sheet_rel = book_acc.sheet_by_name(s)

        if currency == 'HKD':
            col_ab = 1
            col_mv = 4
        if currency == 'SGD' or currency == 'CNY':
            col_ab = 2
            col_mv = 5
        if currency == 'USD':
            col_ab = 3
            col_mv = 5

        for row in range(10, sheet_rel.nrows):
            date_value = xldate_as_tuple(sheet_rel.cell(row,0).value, book_acc.datemode)
            tt = datetime(*date_value)
            if tt == t:
                wlist.append([s, row+1, col_ab+1, ab])
                wlist.append([s, row+1, col_mv+1, mv])
                # print s, type(s), row+1, col_ab+1, ab, type(ab)

    for r in range(1, sheet_fea.nrows):
        date_value = xldate_as_tuple(sheet_fea.cell(r,0).value, book_sec.datemode)
        t = datetime(*date_value)
        currency = sheet_fea.cell(r, 3).value.strip()
        # print currency

        s = sheet_fea.cell(r, 2).value
        ab = sheet_fea.cell(r, 7).value
        mv = sheet_fea.cell(r, 9).value
        # print t, s, currency

        #! Decide s in or not in the ACC exceil file
        snames = book_acc.sheet_names()
        if s not in snames:
            continue
        sheet_rel = book_acc.sheet_by_name(s)

        if currency == 'HKD':
            col_ab = 1
            col_mv = 3
        if currency == 'USD':
            col_ab = 2
            col_mv = 4

        for row in range(10, sheet_rel.nrows):
            date_value = xldate_as_tuple(sheet_rel.cell(row,0).value, book_acc.datemode)
            tt = datetime(*date_value)
            if tt == t:
                wlist.append([s, row+1, col_ab+1, ab])
                wlist.append([s, row+1, col_mv+1, abs(mv)])
                # print s, type(s), row+1, col_ab+1, ab, type(ab)

    accProxy = easyExcel(outname)
    for l in wlist:
        accProxy.setCell(l[0], l[1], l[2], l[3])
        print 'write:', l
    accProxy.save()
    accProxy.close()
    print 'Done!'


#     # excelProxy = easyExcel(r'I:\newly\excel\oa\Accounts Position Auto version.xlsx')
#     excelProxy = easyExcel(outname)

#     # print excelProxy.getRows('Sheet 1')

#     content = excelProxy.getCell("Sheet 1", 5, 1)#, 'Qiubao') 
#     print content, type(content)

#     # excelProxy.setCell('02-0241377-22', 153, 2, -299022428.92)

# #    excelProxy.setRange("sheet1",2,1, ['a','b','c']) 
# #    excelProxy.save()
#     excelProxy.save()
#     excelProxy.close()
#     print "Done!"