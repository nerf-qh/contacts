'''
Created on 16 июля 2013 г.

@author: shkalar

Copyright 2013 Aleh Krautsou
Licensed under the Apache License, Version 2.0

'''

import pymysql
import os, sys

def getData(path):
    data = []
    f = open(path, 'r')
    f.readline() # Заголовок
    line = f.readline().strip()
    while line:
        if line[0] != '#' and len(line) > 4:
            data.append(tuple(line.replace('\n', '').replace('\r', '').split(';')))
        line = f.readline()
                  
    return data
    
class db(object):
    '''
    Работа с базой
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.host = '127.0.0.1'
        #port = '3306'
        self.user = 'root'
        self.passwd = '123'
        self.db = 'my_db'        
    
    def connect(self):
        '''
        Подключение к БД
        '''
        self.conn = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db, charset='utf8')
        self.cur = self.conn.cursor()
    
    def close(self):
        self.conn.close()
    
    def update(self, fio, data, name_row):
        '''
        Обновление данных сотрудников
        '''
        fio = fio.replace(' ', ' ').strip().lower().split(' ')
        str_query = r"SELECT j.`id` FROM j3m5_contact_details j WHERE j.`name` like '%" + fio[0] + r"%' and j.`name` like '%" + fio[1] + r"%'"
        self.cur.execute(str_query)
        if self.cur.rowcount == 0:
            print('Not found: %s %s %s' % (fio[0],fio[1], fio[2]))
        elif self.cur.rowcount > 1:
            print('Many found: %s %s %s' % (fio[0],fio[1], fio[2]))
        else: 
            id_row = self.cur.fetchone()
            str_query = r"UPDATE j3m5_contact_details set %s='%s' WHERE id = %s" % (name_row, data, id_row[0])
            self.cur.execute(str_query)
            self.conn.commit()
            print('+ %s,  %s %s %s   -> %s' % (id_row[0], fio[0],fio[1], fio[2], data))
        
        
def main():
    files_dir = os.path.dirname(sys.argv[0]) + '/'
    file_data = 'dr.csv';
    data = getData(files_dir + file_data)
    my_db = db()
    my_db.connect()
    for i in data:
        my_db.update(i[0], i[1], 'created' )
    my_db.close()

if __name__ == '__main__':
    main()