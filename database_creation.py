# firstly, we need to create database with all necessary tables


"""imports"""


import mysql.connector
from logger import logger


"""database creation"""


# function for creation of server connection
def create_server_connection(host_name, port_name, user_name, user_password):
    # try to connect to MySQL server
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            port=port_name,
            user=user_name,
            passwd=user_password
        )
        logger.info("MySQL Database connection successful")
    # rise error if connection unsuccessful
    except mysql.connector.Error as err:
        logger.info(f"Error: '{err}'")
    # return connection object
    return connection


# function for creation of server connection to database
def create_database_connection(host_name, port_name, user_name, user_password, database_name):
    # try to connect to MySQL server database
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            port=port_name,
            user=user_name,
            passwd=user_password,
            database=database_name
        )
        logger.info("MySQL Database connection successful")
    # rise error if connection unsuccessful
    except mysql.connector.Error as err:
        logger.info(f"Error: '{err}'")
    # return connection object
    return connection


# function for sql query execution
def execute_sql_query(connection, query):
    # create cursor object for query execution on server
    cursor = connection.cursor()
    # try to execute query
    try:
        cursor.execute(query)
        connection.commit()
        return "query execute successfully"
    # rise error if execution failed
    except mysql.connector.Error as err:
        return f"Error: '{err}'"


# function for sql read query
def sql_read_query(connection, query):
    # create cursor object for query execution on server
    cursor = connection.cursor()
    # try to execute query
    try:
        cursor.execute(query)
        # read and return data from execution output
        result = cursor.fetchall()
        # logger.info("read successfully")
        return result
    # rise error if execution failed
    except mysql.connector.Error as err:
        return f"Error: '{err}'"


# function for many sql query execution
def executemany_sql_query(connection, sql, val):
    # create cursor object for query execution on server
    cursor = connection.cursor()
    # try to execute query
    try:
        cursor.executemany(sql, val)
        connection.commit()
        logger.info("query execute successfully")
    # rise error if execution failed
    except mysql.connector.Error as err:
        logger.info(f"Error: '{err}'")


# connect to MySQL server
connection = create_server_connection(host_name="127.0.0.1", port_name="3306", user_name="root",
                                      user_password="1234567890")
# create new database
database_creation_query = "CREATE DATABASE quote_application"
execute_sql_query(connection=connection, query=database_creation_query)


"""database tables creation"""


# connect to MySQL database
connection = create_database_connection(host_name="127.0.0.1", port_name="3306", user_name="root",
                                        user_password="1234567890", database_name="quote_application")
# print database name
print(connection.database)

# create account table
create_account_table = """
CREATE TABLE account (
    account_id INT NOT NULL AUTO_INCREMENT,
    account_name VARCHAR(100) NOT NULL,
    account_password VARCHAR(100) NOT NULL,
    PRIMARY KEY (account_id)
);
 """
execute_sql_query(connection, create_account_table)

# create quote table
create_quote_table = """
CREATE TABLE quote (
    quote_id INT NOT NULL AUTO_INCREMENT,
    account_id INT,
    quote_text VARCHAR(1000) NOT NULL,
    PRIMARY KEY (quote_id),
    FOREIGN KEY(account_id) REFERENCES account(account_id) ON DELETE CASCADE
);
 """
execute_sql_query(connection, create_quote_table)















