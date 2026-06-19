import pymysql
import itertools

from utils.env import DBUSER, DBPASS, DATABASE


# sql class
class sql:
	
	# connection
	@staticmethod
	def connect():
		db = pymysql.connect(host="dl-center-bot-db", user=DBUSER, password=DBPASS, database=DATABASE, autocommit=False)
		db_cursor = db.cursor()
		return db, db_cursor
	
	# run query
	@staticmethod
	def run(query, arg=None):
		try:
			db, db_cursor = sql.connect()
			
			db_cursor.execute(query, arg if arg != None else None)
			
			db.commit()
		except Exception as e:
			raise e
		finally:
			db.close()
	
	# transaction
	@staticmethod
	def transaction(queries):
		try:
			db, db_cursor = sql.connect()
			
			for item in queries:
				db_cursor.execute(item[0], item[1] if len(item) == 2 else None)
			
			db.commit()
		except Exception as e:
			db.rollback()
			raise e
		finally:
			db.close()
	
	# get a single result
	@staticmethod
	def get(query, arg=None):
		try:
			db, db_cursor = sql.connect()
			
			if arg != None:
				db_cursor.execute(query, arg)
			else:
				db_cursor.execute(query)
			try:
				res = db_cursor.fetchone()[0]
			except TypeError:
				res = None
			
			return res
		except Exception as e:
			raise e
		finally:
			db.close()
	
	# chain the result
	@staticmethod
	def chain(query, arg=None):
		try:
			db, db_cursor = sql.connect()
			
			if arg != None:
				db_cursor.execute(query, arg)
			else:
				db_cursor.execute(query)
			res = list(itertools.chain(*db_cursor.fetchall()))
			
			return res
		except Exception as e:
			raise e
		finally:
			db.close()
