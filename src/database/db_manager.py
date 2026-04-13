import sqlite3

"""
DB Manager
负责数据库的初始化、连接、关闭等操作
"""

class DBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """打开 Excel 文件"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def commit(self):
        """点击 保存 按钮"""
        if self.conn:
            self.conn.commit()

    def close(self):
        """关掉 Excel 文件"""
        if self.conn:
            self.conn.close()

    def execute_script(self, script: str):
        """
        一次性运行一整串 SQL 命令（比如把蓝图全跑一遍）
        """
        if self.cursor:
            self.cursor.executescript(script)
            self.commit()

    def execute(self, query: str, params: tuple = None):
        """
        执行一条具体的命令（带参数防注入）
        """
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def execute_and_commit(self, query: str, params: tuple = None):
        """
        执行命令并直接保存
        """
        results = self.execute(query, params)
        self.commit()
        return results