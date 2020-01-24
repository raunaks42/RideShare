from sqlalchemy import (Column, DateTime, ForeignKey, Integer, MetaData,
                        String, Table, create_engine)

class DataBase:

	def __init__(self, dbname=''):
		self.db_engine = create_engine(f'sqlite:///{dbname}')

	def create_db_tables(self):
		metadata = MetaData()

		users = Table('users', metadata,
			Column('username', String, primary_key=True),
			Column('password', String, nullable=False)
		)

		rides = Table('rides', metadata,
			Column('rideId', Integer, primary_key=True),
			Column('created_by', None, ForeignKey('users.username')),
			Column('timestamp', String, nullable=False),
			Column('source', Integer, nullable=False),
			Column('destination', Integer, nullable=False)
		)

		riders = Table('riders', metadata,
			Column('rideId', None, ForeignKey('rides.rideId'), primary_key=True),
			Column('user', None, ForeignKey('users.username'), primary_key=True)
		)

		try:
			metadata.create_all(self.db_engine)
		except Exception as e:
			print(e)
			return False

	def execute(self, query, params=()):
		with self.db_engine.connect() as conn:
			try: conn.execute(query, params)
			except Exception as e:
				print(e)
				return False
		return True

	def fetchall(self, query, params=()):
		with self.db_engine.connect() as connection:
			try: res = connection.execute(query, params).fetchall()
			except Exception as e:
				print(e)
				return False
		return list(map(list, res)) if res else False

	def fetchone(self, query, params=()):
		with self.db_engine.connect() as connection:
			try: res = connection.execute(query, params).fetchone()
			except Exception as e:
				print(e)
				return False
		return list(res) if res else False

db = DataBase('rideshare.db')
execute = db.execute
fetchall = db.fetchall
fetchone = db.fetchone

if __name__ == "__main__":
	db.create_db_tables()
	pass
