import fl_util
import csv
import datetime
import os
import win32com.client as win32

def locate_table(table, row_pos, col_pos, st):
	cell = table.Cell(row_pos, col_pos)
	if cell and st in cell.Range.Text:
		return True
	
	return False

def write_to_termsheet(cur, header, template, outfile):
	word = win32.gencache.EnsureDispatch("Word.Application")
	word.Visible = 0
	doc = word.Documents.Add(template)
	word.Selection.Find.Execute("[TODAY_DATE]", False, False, False, False, False, True, 1, False, datetime.date.today().strftime("%d. %B %Y"), 2)
	try:
		for table in doc.Tables:
			if locate_table(table, 2, 1, "Liquidity Provider broker ID"):

				cur.execute("select * from termsheet")
				term_rows = cur.fetchall()
				term_row_cnt = len(term_rows)

				for i in range(1, term_row_cnt):
					for j in range(0, table.Columns.Count):
						print table.Cell(i+1, j).Range.Text
						table.Cell(i+1, j).Range.Text = table.Cell(1, j).Range.Text
				

	finally:
		doc.SaveAs(outfile)
		doc.Close()

	return

def merge_xlsx_db(cur, term_sheet_file, comp_info_file):
	header_term, arr_term = fl_util.xlsx_to_arr(term_sheet_file)
	header_info, arr_info = fl_util.xlsx_to_arr(comp_info_file)

	fl_util.create_tbl(cur, "term", header_term, arr_term)
	fl_util.create_tbl(cur, "info", header_info, arr_info)

	header_termsheet = fl_util.remove_dup(header_term, header_info)
	header_termsheet = '"'+'","'.join(header_term.split(','))+'"'

	cur.execute("create table termsheet (" + header_termsheet + ")")
	cur.execute("insert into termsheet ("+header_termsheet+") SELECT "+header_termsheet+" from term left join info on term.guarantor = info.equity where issuer <> '' ")

	cur.execute("drop table term")
	cur.execute("drop table info")

	info_rows = cur.execute("select * from termsheet")
	return header_termsheet

comp_info_file = "D:\\Projects\\HTI\\docx_automation\\Company Information.xlsx"
term_sheet_file = "D:\\Projects\\HTI\\docx_automation\\ClearedTermSheet_20160308_095932.csv.xlsx"
sld_eng_template = "D:\\Projects\\HTI\\docx_automation\\SLD Template (English).docx"
sld_eng_output = "D:\\Projects\\HTI\\docx_automation\\SLD (English).docx"

conn, cur = fl_util.db_cur()
header_termsheet = merge_xlsx_db(cur, term_sheet_file, comp_info_file)

write_to_termsheet(cur, header_termsheet, sld_eng_template, sld_eng_output)