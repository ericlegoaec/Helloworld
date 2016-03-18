import fl_util
import datetime
import os
import zipfile
from BeautifulSoup import BeautifulSoup
import lxml

def locate_table(table, row_pos, col_pos, st):
	cell = table.Cell(row_pos, col_pos)
	if cell and st in cell.Range.Text:
		return True
	
	return False

def write_to_termsheet(cur, header, template, outfile):
	document = zipfile.ZipFile(template)
	xml_content = document.read('word/document.xml')
	#print xml_content
	soup = BeautifulSoup(xml_content, "xml")

	print soup.pStyle
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