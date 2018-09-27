# -*- coding:utf-8 -*-

# author : zhangning
# requirement : oracle 12c

import cx_Oracle
import traceback

class Oracle(object):
    def __init__(self, host, port, user, password, sid, logger):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.sid = sid
        self.logger = logger
        self._conn = None
        self._cursor = None
        self._connectDB()

    def _connectDB(self):
        try:
            self._conn = cx_Oracle.connect(self.user, self.password, "%s:%s/%s" % (self.host, self.port, self.sid))
            self._cursor = self._conn.cursor()
            return True
        except Exception as e:
            logger_info = 'connect Oracle failed\n %s' % (traceback.format_exc())
            self.logger.error(logger_info)
            return False

    def makedict(self, cursor):
        cols_name = [c[0] for c in cursor.description]
        def gendict(*args):
            return dict(zip(cols_name, args))
        return gendict

    def _connPing(self):
        try:
            self._conn.ping()
            return True
        except:
            return False

    def _check_db_conn(self):
        if self._connPing() == False:
            while True:
                self.logger.info('cannot connect to Oracle,try to reconnect Oracle!')
                self._connectDB()
                if self._connPing() == True:
                    self.logger.info('reconnect Oracle succeeded!')
                    break
                else:
                    self.logger.info('reconnect Oracle failed!')
        else:
            pass

    def _getALL(self, sql):
        self._check_db_conn()
        self._cursor.execute(sql)
        self._cursor.rowfactory = self.makedict(self._cursor)
        res = self._cursor.fetchall()
        # self._commit()
        return res

    def _getOne(self, sql):
        self._check_db_conn()
        # print self._cursor
        self._cursor.execute(sql)
        self._cursor.rowfactory = self.makedict(self._cursor)
        res = self._cursor.fetchone()
        # self._commit()
        return res

    #获取Select的SQL语句
    def _getSelectSQL(self, table_name, column_name, max_id, row_num):
        sql = 'select * from %s where %s > %s order by %s fetch first %s rows only' % (table_name, column_name, max_id, column_name, row_num)
        return sql

    # 获取insert的SQL语句
    def _getInsertSQL(self, table_name, value_dict):
    # The Type of value_dict is dictionary
    # Example: insert into table_name(col1,col2,..,coln) values(:col1,:col2,..,coln)
        fields = ','.join(value_dict.keys())
        val_fields = ','.join(map(lambda x: ':%s' % x, value_dict.keys()))
        sql = 'insert into %s(%s) values(%s)' % (table_name, fields, val_fields)
        return sql

    # 插入一条记录
    def _insertOne(self, sql, value):
    # value : list/tuple/dict
    # value_dict = {'ins_col1': val1, 'ins_col2': val2,..., 'ins_coln': valn}
    # Example: cursor.execute('insert into table_name(col1,col2,..,coln) values(:ins_col1,:ins_col2,..,ins_coln)', value_dict)
        self._check_db_conn()
        self._cursor.execute(sql, value)

    # 插入多条记录
    def _insertMany(self):
    # value_dict = [{'ins_col1': val_11, 'ins_col2': val_21,..., 'ins_coln': val_n1},{'ins_col_12': val1, 'ins_col2': val_22,..., 'ins_coln': val_n2}]
    # Example: cursor.execute('insert into table_name(col1,col2,..,coln) values(:ins_col1,:ins_col2,..,ins_coln)', value_dict)
        self._check_db_conn()
        self._cursor.executemany(sql, value)

    # 更新操作
    def _update(self, table_name, set_dict, where_dict):
        pass

    # 删除操作
    def _delete(self):
        pass

    # 提交操作
    def _commit(self):
        self._conn.commit()

    # 关闭数据库连接
    def _close(self):
        self._cursor.close()
        self._conn.close()