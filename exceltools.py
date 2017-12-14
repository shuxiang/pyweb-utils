#coding=utf8
from StringIO import StringIO
import csv

def list2csv(name, title, table):
    f = file(name, 'w')
    f.write('\xEF\xBB\xBF')
    writer = csv.writer(f)
    writer.writerow([t.encode('utf8') if type(t) is unicode else str(t) for t in title])
    for l in table:
        try:
            writer.writerow([c.encode('utf8') if type(c) is unicode else (str(c) if c!=None else '') for c in l])
        except:
            pass
    f.close()

import xlwt

def list2xlsx(name, title, table, sheetname='sheet1'):
    f = xlwt.Workbook() #创建工作簿

    '''
    创建第一个sheet:
    sheet1
    '''
    sheet1 = f.add_sheet(sheetname, cell_overwrite_ok=True) #创建sheet

    # write title
    for i, t in enumerate(title):
        sheet1.write(0, i, t)

    # write content
    for j, row in enumerate(table):
        for k, c in enumerate(row):
            sheet1.write(j+1, k, c)


    f.save(name) #保存文件


def list2xlsx_v2(name, titles, tables, sheetnames=[]):
    f = xlwt.Workbook() #创建工作簿

    '''
    创建第一个sheet:
    sheet1
    '''
    for m, title in enumerate(titles):
        sheet1 = f.add_sheet(sheetnames[m], cell_overwrite_ok=True) #创建sheet

        # write title
        for i, t in enumerate(title):
            sheet1.write(0, i, t)

        # write content
        for j, row in enumerate(tables[m]):
            for k, c in enumerate(row):
                sheet1.write(j+1, k, c)


    f.save(name) #保存文件

if __name__ == '__main__':
    #list2xlsx('/home/sx/epan/testtest.xlsx', ['w1', u'创建sheet'], [[1, 'dddddddddddddddddfsfisjlfjdsjfdsjlfjdslfj, dljslfdskl '], [2222222222222222222222, u'疑问又来了，合并单元格可能出现空值，但是表格本身的普通单元格也可能是空值，要怎么获取单元格所谓的"第一个行或列的索引"呢？'], ["'2222222222222222222222", '22222222222222222222']])
    pass