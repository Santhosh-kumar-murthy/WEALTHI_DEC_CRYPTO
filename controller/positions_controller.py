import winsound
from contextlib import closing

import pymysql
from pymysql.cursors import DictCursor
from config import db_config

import pandas as pd


class PositionsController:
    def __init__(self):
        self.conn = pymysql.connect(**db_config, cursorclass=DictCursor)
        self.create_positions_table()

    def create_positions_table(self):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS positions (
                                position_id INT AUTO_INCREMENT PRIMARY KEY,
                                instrument_name VARCHAR(255),
                                direction INT,
                                position_entry_time DATETIME,
                                position_entry_price FLOAT,
                                position_exit_time DATETIME,
                                position_exit_price FLOAT,
                                profit FLOAT
                            )
                        ''')
            self.conn.commit()

    def enter_new_position(self, instrument_name, buy_price, direction):
        with self.conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO positions (instrument_name, direction,position_entry_time,position_entry_price) '
                'VALUES (%s,%s,NOW(),%s)',
                (instrument_name, direction, buy_price))
        self.conn.commit()
        freq = 500
        dur = 100
        winsound.Beep(freq, dur)

    def exit_position(self, position, exit_price):
        profit = float(exit_price) - float(position['position_entry_price']) if position['direction'] == 1 else float(
            position['position_entry_price']) - float(exit_price)
        with self.conn.cursor() as cursor:
            cursor.execute(
                'UPDATE positions SET position_exit_price = %s,position_exit_time = NOW(),'
                'profit = %s WHERE position_id = %s',
                (exit_price, profit, position['position_id']))
        self.conn.commit()
        freq = 500
        dur = 100
        winsound.Beep(freq, dur)

    def get_active_position(self, index_name):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(
                'SELECT * FROM positions WHERE instrument_name = %s AND position_exit_time IS NULL', index_name)
            active_trade = cursor.fetchone()
        return active_trade
