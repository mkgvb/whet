#!/bin/python3

import sqlite3
import datetime
import random
import time

db_file='whet.db'


class DataBase():

    
    def __init__(self, table, unit='value'):
        self.conn = sqlite3.connect(db_file)
        self.table = table

        try:
            cursor = self.conn.cursor()
            cursor.execute('CREATE TABLE {tn} (date integer, {unit} integer)'.format(tn=table,unit=unit))
            self.conn.commit()
        except sqlite3.OperationalError as sqlErr:
            print(sqlErr)

        cursor.close()

    def open(self):
        self.c = self.conn.cursor()

    def close(self):
        self.conn.commit()
        self.c.close()

    def destroy(self):
        self.conn.close()

    def writeNow(self, value):
        self.open()
        t = [(int(time.time()), value)]
        self.c.executemany("INSERT INTO " + self.table + " VALUES (?,?)", t)
        self.close()

    def readAll(self, before=int(time.time()), after=0):
        self.open()
        g = (self.table, before, after)
        for row in self.c.execute('''
        SELECT * FROM {tn}
        WHERE date <= {b} AND date >= {a} 
        ORDER BY date'''.format(tn=self.table, b=before, a=after)):
            print(time.strftime('%Y-%m-%d %H:%M:%S',
                                time.localtime(row[0])), str(row[1]) + 'c   ' + str(row))
        self.close()


if __name__ == '__main__':
    print('------------temperature-------------------')
    dw = DataBase('temperature-test')
    dw.writeNow(random.randint(1, 100))
    dw.readAll(before=time.time()-300)
    print('^^^---------before - 300---------------^^^')
    dw.readAll()
    print('^^^------------all------------^^^')
    dw.destroy()
    print('------------------------------------------\n\n')
    

    print('------------power-------------------')
    dw = DataBase('power-test','watts')
    dw.writeNow(random.randint(1, 100))
    dw.readAll(before=time.time()-300)
    print('^^^---------before - 300---------------^^^')
    dw.readAll()
    print('^^^------------all------------^^^')
    dw.destroy()
    print('------------------------------------------\n\n')
    
    dw.destroy()
