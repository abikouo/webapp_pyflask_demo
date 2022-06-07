import psycopg2


class DBClient(object):

    def __init__(self, host, user, db, password):
        dbuser = user
        if host.endswith("postgres.database.azure.com"):
            # specific case for azure db
            dbuser = f"{user}@{host}"
        conn_string = f"host={host} user={dbuser} dbname={db} password={password} sslmode='require'"
        self.conn = psycopg2.connect(conn_string)
    
    def close(self):
        self.conn.close()

    def write(self, sql_query):
        error = None
        try:
            cursor = self.conn.cursor()
            if isinstance(sql_query, list):
                for qry in sql_query:
                    cursor.execute(qry)
            else:
                cursor.execute(sql_query)
            cursor.close()
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as e:
            error = e
        return error

    def read(self, sql_query, all=False):
        error = None
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_query)
            if cursor.rowcount == 0:
                cursor.close()
                return None, error
            else:
                data = cursor.fetchone() if not all else cursor.fetchall()
                cursor.close()
                return data, None
        except (Exception, psycopg2.DatabaseError) as e:
            if cursor:
                cursor.close()
            return None, e