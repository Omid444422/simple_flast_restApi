import mysql.connector

class Database:
    def __init__(self) -> None:
        self.connection = mysql.connector.connect( 
        host="localhost",
        user="root",
        password="",
        database="blog_application")
        self.cursor = self.connection.cursor(buffered=True)

    def querySingle(self,sql, args):
    # args id=%s [1]
        self.__init__()
        try:
            result = list()
            if args:
              self.cursor.execute(sql, args)
            else:
              self.cursor.execute(sql)

            for row in self.cursor:
                result.append(dict((column[0],row[index]) for index, column in enumerate(self.cursor.description)))
            return result
        finally:
            self.connection.commit()
            self.cursor.close()