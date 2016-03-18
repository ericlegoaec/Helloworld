from xlrd import open_workbook, cellname, xldate_as_tuple
from datetime import date, datetime
from xlutils.copy import copy

# Open Accounts
book_acc = open_workbook('Accounts Position Auto version.xls', formatting_info=True)
book_acc_w = copy(book_acc)

# Open Securities
book_sec = open_workbook('Securities AC Portfolio 20140701.xls')
sheet_sec = book_sec.sheet_by_index(0)
# Avail Balance TN (Local CCY) : 7
# Market Value TN (Local CCY) : 9
for r in range(1, sheet_sec.nrows):
    date_value = xldate_as_tuple(sheet_sec.cell(r,0).value, book_sec.datemode)
    t = datetime(*date_value)
    currency = sheet_sec.cell(r, 3).value.strip()
    # print currency
    s = sheet_sec.cell(r, 2).value
    ab = sheet_sec.cell(r, 7).value
    mv = sheet_sec.cell(r, 9).value
    # print t, s, currency

    names_sheet = book_acc.sheet_names()
    sheet_rel = book_acc.sheet_by_name(s)
    sheet_rel_w = book_acc_w.get_sheet(names_sheet.index(s))

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
            sheet_rel_w.write(row, col_ab, ab)
            print s, row, col_ab
    
#print sheet_sec.cell(0, 9)
book_acc_w.save('test.xls')

#print sheet0.row(13)
#print cellname(0,0)
#print sheet.cell(1,0).value


##sheet = book.sheet_by_name('02-0241377-22')
##date_value = xldate_as_tuple(sheet.cell(20,0).value, book.datemode)
##print datetime(*date_value)
