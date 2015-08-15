#!/usr/bin/python3.3
# -*- coding: utf-8 -*-

'''
Created on 24 июня 2013 г.

@author: shkalar

Copyright 2013 Aleh Krautsou
Licensed under the Apache License, Version 2.0

'''

import sys
import os
import logging
import configparser
import base64
from urllib.request import urlretrieve
import glob
import pymysql
from convert_image import resize


class connector():
    """
        Connector to site db 
    """
    def __init__(self, config):
        """
        Set db 
        """
        self.host = config.get('db', 'host')
        self.port = config.get('db', 'port', fallback='3306')
        self.user = config.get('db', 'user')
        self.passwd = config.get('db', 'passwd')
        self.db = config.get('db', 'name')
        self.charset = config.get('db', 'charset', fallback='utf8')
    
    def getContacts(self):
        """
        Get contacts from db
        """
        conn = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db, charset=self.charset)
        cur = conn.cursor()
        cur.execute("""
        SELECT `alias`, `id`, `name`, `con_position`, `suburb`, `telephone`, `fax`, `misc`, `image`, `email_to`, `mobile`, `created` FROM j3m5_contact_details  where published=1 ORDER BY name 
        """)
        data = []
        for r in cur:
            data.append(r)
        cur.close()
        conn.close() 
        return data

def create_vCard(files_dir, serv, data):
    logging.info('Create ' + data[2])
    tmp_img = files_dir + 'tmp.jpg'
    
    file_name = files_dir + data[0] + ".vcf"   
    f = open(file_name, 'w')
    f.write('BEGIN:VCARD\nVERSION:3.0\n')
    fio = data[2].replace(' ', ' ').strip().split(' ')
    f.write('FN:' + fio[0] + ' ' + fio[1] + '\n')
    f.write('N:' + fio[0] + ';' + fio[1] + ';;;\n')
    if data[9]:
        f.write('EMAIL;TYPE=INTERNET;TYPE=WORK:' + data[9] + '\n')
    
    f.write('TEL;TYPE=CELL:' + data[10] + '\n')
    f.write('BDAY:' + str(data[11]).replace(' 00:00:00','') + '\n')
    tel = data[5].split(',')
    for nom in tel:
        f.write('TEL;TYPE=WORK:' + nom.strip() + '\n')
    f.write('TITLE:' + data[3] + '\n')
    note = data[7].replace('\r\n', '\\r\\n').replace('\n', '\\n').replace('<p>','').replace('</p>','')
    f.write('NOTE:' + data[6] + '\\n' + note + '\n')
    if len(data[4]) > 0:
        f.write('ADR;TYPE=HOME:;;;' + data[4] + ';;;\n')
    
    if len(data[8]) > 0:
        try:
            urlretrieve(serv + data[8], tmp_img)
        except:
            logging.warn('err. not found file:' + serv + data[8])
        else:
            resize(tmp_img)
            f.write('PHOTO;ENCODING=b;TYPE=JPEG:' + str(base64.b64encode(open(tmp_img, 'rb').read()))[2:-1] + '\n')

    f.write('ORG:ЕКТ\n END:VCARD\n')
    f.close()
    
def write_to_file(fpath, what):
    try:
        handle = open(fpath,"a")
    except:
        logging.critical("error: can not write to file (%s)" % fpath)
        sys.exit(0)
    handle.write(what)
    handle.close()

def del_old_files(files_dir):
    filelist = glob.glob(files_dir + "*.*")
    for f in filelist:
        os.remove(f)
    filelist = glob.glob(files_dir + "all/*.vcf")
    for f in filelist:
        os.remove(f)


def create_vCards(db_conn, files_dir, serv):
    data = db_conn.getData()
    for r in data:
        create_vCard(files_dir, serv, r)


def merge_files(files_dir):
    if not os.path.exists(files_dir + 'all/'):
        try:
            os.makedirs(files_dir + 'all/')
        except OSError:
            logging.critical(OSError)
            sys.exit(0)
 
    nom_file = 0
    for line in glob.glob(files_dir + '*.vcf'):
        tmp_path = files_dir + 'all/all_' + str(nom_file).zfill(2) + '.vcf'
        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 8000000:
            nom_file += 1
            tmp_path = files_dir + 'all/all_' + str(nom_file).zfill(2) + '.vcf'
            
        f = open(tmp_path, 'a')
        for content in open(line, "r"):
            f.write(content)
        f.close()    

def main():
    dir_path = os.path.dirname(sys.argv[0])
    
    logging.basicConfig(filename = dir_path + 'contacts.log',
                        filemode = 'a',
                        level = logging.DEBUG,
                        format = '%(asctime)s %(levelname)s: %(message)s',
                        datefmt = '%Y-%m-%d %H:%M:%S')

    logging.debug('Start creat contacts')
    
    configPath = dir_path + 'config.ini'
    config = configparser.ConfigParser()

    if os.path.exists(configPath):
        logging.debug('Config path: %s' % configPath)
        config.read(configPath)
    else:
        print('Config not exists:%s' % configPath)
        logging.critical('Config not exists:%s' % configPath)
        return
    
    db_conn = connector(config)
    files_dir = config.get('files', 'dir', fallback='./vcf/')
    serv = config.get('site', 'adr', fallback='')
   
    del_old_files(files_dir)
    create_vCards(db_conn, files_dir, serv)
    merge_files(files_dir)
    
    logging.info('End generation vCard')

if __name__ == '__main__':
    main()
