'''
Created on 16 сент. 2013 г.

@author: shkalar

Copyright 2013 Aleh Krautsou
Licensed under the Apache License, Version 2.0
'''
import os, sys, glob

def main():
    files_dir = os.path.dirname(sys.argv[0]) + '/vcf/'
    
    nom_file = 0
    if not os.path.exists(files_dir + 'all/'):
        try:
            os.makedirs(files_dir + 'all/')
        except OSError:
            sys.exit(0)
            print(OSError)
        
    for line in glob.glob(files_dir + '*.vcf'):
        tmp_path = files_dir + 'all/all_' + str(nom_file) + '.txt'
        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 1000000:
            nom_file += 1
            tmp_path = files_dir + 'all/all_' + str(nom_file) + '.txt'
        f = open(tmp_path, 'a')
        for content in open(line, "r"):
            f.write(content)
        f.close()    


if __name__ == '__main__':
    main()