# all functions and classes of quote application


"""imports"""


import mysql.connector
import re
from logger import logger
import tkinter as tk
from tkinter import scrolledtext


"""functions and classes"""


# function for creation of dict with errors
def create_dict_with_errors():
    """
    function for creation of dict with errors
    :return: dict with errors
    """
    # create dict with errors
    error_dict = {
        0: "error: 'account with that's name didn't exist'",
        1: "error: 'given account password didn't match with actual'",
        2: "error: 'quote with given quote id didn't exist'",
        3: "error: 'given author name didn't relate to any of existing accounts'",
        4: "error: 'MySQL database isn't connected, use method self.create_database_connection() to create connection'"
    }
    # return dict with errors
    return error_dict


# decorator function for database connection check
def connection_check_decorator(func):
    """
    decorator function for database connection check
    :param func: functon for what been added connection to database check
    :return: function with connection check
    """
    # create wrapped function
    def wrapped(*args, **kwargs):
        # return connection error if connection is None
        if args[0].connection is None:
            logger.error(args[0].error_dict[4])
            return args[0].error_dict[4]
        # return input function if connection is not None
        else:
            return func(*args, **kwargs)

    # return wrapped function
    return wrapped


# class with all application backend functions
class ApplicationBackend:
    # initialization
    def __init__(self):
        """
        class with all application backend functions
        """
        # initialize database connection object without connection
        self.connection = None
        # create error dict
        self.error_dict = create_dict_with_errors()

    # function for creation of server connection to database
    def create_database_connection(self, host_name, port_name, user_name, user_password, database_name):
        """
        function for creation of server connection to database
        :param host_name: db host name
        :param port_name: db port name
        :param user_name: db username
        :param user_password: db user password
        :param database_name: database name
        :return: database connection object
        """
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
            logger.info("MySQL Database connect successfully")
        # rise error if connection unsuccessful
        except mysql.connector.Error as err:
            logger.info(f"Error: '{err}'")
        # return connection object as self
        self.connection = connection

    # function for sql query execution
    @connection_check_decorator
    def execute_sql_query(self, query):
        """
        function for sql query execution
        :param query: sql query
        :return: executed sql query
        """
        # create cursor object for query execution on server
        cursor = self.connection.cursor()
        # try to execute query
        try:
            cursor.execute(query)
            self.connection.commit()
            return "query execute successfully"
        # rise error if execution failed
        except mysql.connector.Error as err:
            return f"Error: '{err}'"

    # function for sql read query
    @connection_check_decorator
    def sql_read_query(self, query):
        """
        function for sql read query
        :param query: sql read query
        :return: executed sql read query
        """
        # create cursor object for query execution on server
        cursor = self.connection.cursor()
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

    # function for taking password of given account name
    @connection_check_decorator
    def take_account_password(self, account_name):
        """
        function for taking password of given account name

        :param account_name: account name from account table
        :return: password from account with target name
        """
        # sql query for target account password take
        sql_password_take = f"""
            SELECT account.account_password FROM account
             WHERE account.account_name = '{account_name}';
        """
        # return account password
        return self.sql_read_query(query=sql_password_take)

    # function for taking account id by its name
    @connection_check_decorator
    def take_account_id(self, account_name):
        """
        function for taking account id by its name

        :param account_name: account name from account table
        :return: id of target account
        """
        # sql query for taking target account id
        sql_id_take = f"""
            SELECT account.account_id FROM account
             WHERE account.account_name = '{account_name}';
        """
        # return account id
        return self.sql_read_query(query=sql_id_take)

    # function for taking account name by account id
    @connection_check_decorator
    def take_account_name_by_id(self, account_id):
        """
        function for taking account name by account id

        :param account_id: account id from account table
        :return: name of target account
        """
        # sql query for taking target account name
        sql_name_take = f"""
            SELECT account.account_name FROM account
             WHERE account.account_id = '{account_id}';
        """
        # return account name
        return self.sql_read_query(query=sql_name_take)

    # function for taking id of the latest quote created by input account
    @connection_check_decorator
    def taking_account_latest_quote_id(self, account_name):
        """
        function for taking id of last quote created by input account

        :param account_name: account name from account table
        :return: id of last created quote
        """
        # take account id by account name
        account_id = self.take_account_id(account_name=account_name)[0][0]
        # sql query for taking all quotes ids created by input account
        sql_id_take = f"""
            SELECT quote.quote_id FROM quote
            WHERE quote.account_id = '{account_id}';
        """
        # take all quotes ids
        quotes_ids = self.sql_read_query(query=sql_id_take)
        # convert quotes_ids to one-dimensional list
        quotes_ids = [i[0] for i in quotes_ids]
        # return quote id with the biggest number
        return max(quotes_ids)

    # function for adding new row to account table
    @connection_check_decorator
    def account_creation(self, account_name, account_password):
        """
        function for adding new row to account table
        :param account_name: unique account name
        :param account_password: account password
        :return: error or success message
        """
        # sql query for insert new account information row
        sql_account_insert = f"""
            INSERT INTO account (`account_name`, `account_password`) VALUES ('{account_name}', '{account_password}');
        """
        # execute query
        output = self.execute_sql_query(query=sql_account_insert)
        # return output
        return output

    # function for editing row from account table
    @connection_check_decorator
    def account_edition(self, p_account_name, p_account_password, new_account_name, new_account_password):
        """
        function for editing row from account table
        :param p_account_name: previous account name
        :param p_account_password: previous account password
        :param new_account_name: new account name
        :param new_account_password: new account password
        :return: error or success message
        """
        # take real account password
        real_password = self.take_account_password(account_name=p_account_name)

        # try compare given and real password, after what either edit target account or return account editing error
        try:
            if real_password[0][0] == p_account_password:
                # sql query for account row update
                sql_account_update = f"""
                    UPDATE account
                    SET account.account_name = '{new_account_name}', account.account_password = '{new_account_password}'
                    WHERE account.account_name = '{p_account_name}';
                """
                # execute query for account edit
                output = self.execute_sql_query(query=sql_account_update)
                # return output
                return output
            else:
                # return error
                return self.error_dict[1]
        except:
            # return error
            return self.error_dict[0]

    # function for deleting row from account table
    @connection_check_decorator
    def account_deletion(self, account_name, account_password):
        """
        function for deleting row from account table
        :param account_name: account name
        :param account_password: account password
        :return: error or success message
        """
        # take real account password
        real_password = self.take_account_password(account_name=account_name)

        # try compare given and real password, after what either delete target account or return account deletion error
        try:
            if real_password[0][0] == account_password:
                # sql query for account row deletion
                sql_account_deletion = f"""
                    DELETE FROM account
                    WHERE account.account_name = '{account_name}';
                """
                # execute query for account deletion
                output = self.execute_sql_query(query=sql_account_deletion)
                # return output
                return output
            else:
                # return error
                return self.error_dict[1]
        except:
            # return error
            return self.error_dict[0]

    # function for adding new row to quote table
    @connection_check_decorator
    def quote_creation(self, account_name, account_password, quote_text):
        """
        function for adding new row to quote table
        :param account_name: author account name
        :param account_password: author account password
        :param quote_text: text of new quote
        :return: error or success message and id of created quote
        """
        # create blank quote_id
        quote_id = None
        # take real account password
        real_password = self.take_account_password(account_name=account_name)
        # take account id
        account_id = self.take_account_id(account_name=account_name)

        # try to compare given and real password
        try:
            # add new quote if account password did match
            if real_password[0][0] == account_password:
                # sql query for adding new row to quote table
                sql_quote_adding = f"""
                    INSERT INTO quote (`account_id`, `quote_text`) VALUES ('{account_id[0][0]}', '{quote_text}');
                """
                # execute query for quote creation
                output = self.execute_sql_query(query=sql_quote_adding)
                # take id of new quote
                quote_id = self.taking_account_latest_quote_id(account_name=account_name)
                # return output and quote_id
                return [output, quote_id]
            # return error if password didn't match
            else:
                return [self.error_dict[1], quote_id]
        # return error if account didn't exist
        except:
            return [self.error_dict[0], quote_id]

    # function for editing text of quote from quote table
    @connection_check_decorator
    def quote_edition(self, account_name, account_password, quote_id, new_quote_text):
        """
        function for edition text of quote from quote table
        :param account_name: author account name
        :param account_password: author account password
        :param quote_id: id of target quote
        :param new_quote_text: new text of quote
        :return: error or success message
        """
        # take real account password
        real_password = self.take_account_password(account_name=account_name)

        # try to compare given and real password
        try:
            # update quote if account password did match
            if real_password[0][0] == account_password:
                # sql query for editing text of existing quote
                sql_quote_text_update = f"""
                    UPDATE quote
                    SET quote.quote_text = '{new_quote_text}'
                    WHERE quote.quote_id = '{quote_id}';
                """
                # execute query for quote update
                output = self.execute_sql_query(query=sql_quote_text_update)
                # return output
                return output
            # return error if password didn't match
            else:
                return self.error_dict[1]
        # return error if account didn't exist
        except:
            return self.error_dict[0]

    # function for deletion of quote
    @connection_check_decorator
    def quote_deletion(self, account_name, account_password, quote_id):
        """
        function for deletion of quote
        :param account_name: author account name
        :param account_password: author account password
        :param quote_id: id of target quote
        :return: error or success message
        """
        # take real account password
        real_password = self.take_account_password(account_name=account_name)

        # try to compare given and real password
        try:
            # delete quote if account password did match
            if real_password[0][0] == account_password:
                # sql query for deletion of quote
                sql_quote_deletion = f"""
                    DELETE FROM quote
                    WHERE quote.quote_id = '{quote_id}';
                """
                # execute query for quote deletion
                output = self.execute_sql_query(query=sql_quote_deletion)
                # return output
                return output
            # return error if password didn't match
            else:
                return self.error_dict[1]
        # return error if account didn't exist
        except:
            return self.error_dict[0]

    # function for taking quote text by quote id
    @connection_check_decorator
    def take_quote_text_by_quote_id(self, quote_id):
        """
        function for taking quote text by quote id

        :param quote_id: id of target quote
        :return: error or quote text with author name
        """
        # try to take quote
        try:
            # sql query for taking quote text with target quote id
            sql_take_quote_text_and_author_name_by_quote_id = f"""
                SELECT quote.quote_text, account.account_name
                FROM quote JOIN account
                ON quote.account_id = account.account_id
                WHERE quote.quote_id = '{quote_id}';
            """
            # read quote text and author name
            output = self.sql_read_query(sql_take_quote_text_and_author_name_by_quote_id)
            # return text and name if output valid
            if len(output[0]) == 2:
                # return output
                return list(output[0])
            # return error if output not valid
            else:
                return self.error_dict[2]
        # return error if quote with this id didn't exist
        except:
            return self.error_dict[2]

    # function for taking all quotes texts by author name
    @connection_check_decorator
    def take_quotes_texts_by_author_name(self, author_name):
        """
        function for taking all quotes texts by author name

        :param author_name: name of author
        :return: error or all quotes texts with ids writen by the target author
        """
        # try to take quotes by author name
        try:
            # take account id of author
            account_id = self.take_account_id(account_name=author_name)
            # sql query for taking quotes texts by author name
            sql_take_quotes_texts__by_account_id = f"""
                SELECT quote.quote_text, quote.quote_id FROM quote
                WHERE quote.account_id = '{account_id[0][0]}';
            """
            # read quotes texts
            output = self.sql_read_query(sql_take_quotes_texts__by_account_id)
            # return quotes texts
            return output
        # return error if author with that's name didn't exist
        except:
            return self.error_dict[3]

    # function for taking all quotes text and authors names where quote text correspond with given text
    @connection_check_decorator
    def take_quotes_texts_by_text(self, target_text):
        """
        function for taking all quotes text and authors names where quote text correspond with given text

        :param target_text: target text by which been returned all corresponding quotes texts
        :return: all quotes texts and authors names correspond with given text.
            output form: [(quote_text, quote_id, account_name),]
        """
        # list with all corresponding quotes texts and authors names
        corresponding_quotes = []

        # take count of rows in quote table
        sql_rows_count = """
            SELECT COUNT(*) FROM quote
        """
        rows_count = self.sql_read_query(sql_rows_count)[0][0]
        # iterate every row and add all text quotes texts with authors names with corresponding to target text

        for count in range(rows_count):
            # taking quote text and author on row number
            sql_take_quote_by_row_count = f"""
                SELECT quote.quote_id, quote.account_id, quote.quote_text FROM quote LIMIT {count},1
            """
            quote = self.sql_read_query(sql_take_quote_by_row_count)[0]
            # search corresponding in quote and target text with
            corresponding = re.search(pattern=target_text, string=quote[2])

            # if corresponding been found, add quote text, quote id, author name and author id to corresponding_quotes
            if corresponding is not None:
                # take author name by id
                author_name = self.take_account_name_by_id(quote[1])[0][0]
                # create tuple with quote text, quote id and account name, then add to corresponding_quotes
                corresponding_quotes.append((quote[2], quote[0], author_name))

        # return list with all corresponding quotes
        return corresponding_quotes


# define child class from ApplicationBackend where been created application GUI and its internal work
class Application(ApplicationBackend):
    # define init
    def __init__(self):
        """
        define child class from ApplicationBackend where been created application GUI and its internal work
        """

        # add init entrails of parent class
        super().__init__()

        # create main GUI window object
        self.gui = self.gui_creation()

    # function for account execution button
    def account_execution(self):
        """
        function for account execution button
        :return: execution of selected mode function
        """
        # get all necessary information
        selected_mode = self.account_selected_mode.get()
        account_name = self.account_name_entry.get()
        account_password = self.account_password_entry.get()
        new_account_name = self.account_new_name_entry.get()
        new_account_password = self.account_new_password_entry.get()

        # choice right operation to use based on selected mode
        # account creation
        if selected_mode == 0:
            # use account creation function with entered information
            result = self.account_creation(account_name, account_password)
        # account edition
        elif selected_mode == 1:
            # use account edition function with entered information
            result = self.account_edition(account_name, account_password, new_account_name, new_account_password)
        # account deletion
        else:
            # use account deletion function with entered information
            result = self.account_deletion(account_name, account_password)

        # clear account output textarea
        self.account_output_textarea.delete(1.0, tk.END)
        # write result of operation to account output textarea
        self.account_output_textarea.insert(index=tk.INSERT, chars=str(result))

    # function for quote execution button
    def quote_execution(self):
        """
        function for quote execution button
        :return: execution of selected mode function
        """
        # get all necessary information
        selected_mode = self.quote_selected_mode.get()
        account_name = self.quote_account_name_entry.get()
        account_password = self.quote_account_password_entry.get()
        quote_text = self.quote_text_entry.get()
        quote_id = self.quote_id_entry.get()

        # choice right operation to use based on selected mode
        # quote creation
        if selected_mode == 0:
            # use quote creation function with entered information
            result = self.quote_creation(account_name, account_password, quote_text)
        # quote edition
        elif selected_mode == 1:
            # use quote text edition function with entered information
            result = self.quote_edition(account_name, account_password, quote_id, quote_text)
        # quote deletion
        else:
            # use quote deletion function with entered information
            result = self.quote_deletion(account_name, account_password, quote_id)

        # clear quote output textarea
        self.quote_output_textarea.delete(1.0, tk.END)

        # if current mode is creation
        if selected_mode == 0:
            # write success message with quote id if quote been creation
            if result[1] is not None:
                # write result of operation to quote output textarea
                self.quote_output_textarea.insert(index=tk.INSERT, chars=f"{result[0]} "
                                                                         f"; id of created quote: {result[1]}")
            # write error if quote hadn't been creation
            else:
                # write result of operation to quote output textarea
                self.quote_output_textarea.insert(index=tk.INSERT, chars=f"{result[0]}")
        # not creation
        else:
            # write result of operation to quote output textarea
            self.quote_output_textarea.insert(index=tk.INSERT, chars=str(result))

    # function for search execution button
    def search_execution(self):
        """
        function for search execution button
        :return: execution of selected mode function
        """
        # get all necessary information
        selected_mode = self.search_selected_mode.get()
        account_name = self.search_by_account_name_entry.get()
        quote_id = self.search_by_quote_id_entry.get()
        target_text = self.search_by_text_entry.get()

        # choice right operation to use based on selected mode
        # search quotes texts by author account name
        if selected_mode == 0:
            # use take_quotes_texts_by_author_name function with entered information
            result = self.take_quotes_texts_by_author_name(account_name)
        # search quote texts by quote id
        elif selected_mode == 1:
            # use take_quote_text_by_quote_id function with entered information
            result = self.take_quote_text_by_quote_id(quote_id)
        # search quote texts by target text pattern
        else:
            # use take_quotes_texts_by_text function with entered information
            result = self.take_quotes_texts_by_text(target_text)

        # clear search output textarea
        self.search_output_textarea.delete(1.0, tk.END)

        # output if search by account name
        if selected_mode == 0:
            # if account didn't have any quotes or return error
            if len(result) == 0 or type(result) == str:
                # write result of operation to search output textarea
                self.search_output_textarea.insert(index=tk.INSERT, chars=str(result))
            # if account have any quotes
            else:
                # create list with output values
                output_text = [f"quote_text: '{quote_text}' ; quote_id: '{quote_id}'"
                               for quote_text, quote_id in result[:]]
                # write result of operation to search output textarea
                self.search_output_textarea.insert(index=tk.INSERT, chars=str(output_text))

        # output if search by quote id
        elif selected_mode == 1:
            # if returned error
            if type(result) == str:
                # write result of operation to search output textarea
                self.search_output_textarea.insert(index=tk.INSERT, chars=str(result))
            # if returned quote
            else:
                # create output text
                output_text = f"quote_text: '{result[0]}' ; author_name: '{result[1]}'"
                # write result of operation to search output textarea
                self.search_output_textarea.insert(index=tk.INSERT, chars=str(output_text))

        # output if search by target text pattern
        else:
            # if returned error
            if type(result) == str:
                # write result of operation to search output textarea
                self.search_output_textarea.insert(index=tk.INSERT, chars=str(result))
            # if returned quote
            else:
                # create list with output values
                output_text = [f"quote_text: '{quote_text}' ; quote_id: '{quote_id}' ; quote_author: '{quote_author}'"
                               for quote_text, quote_id, quote_author in result[:]]
                # write result of operation to search output textarea
                self.search_output_textarea.insert(index=tk.INSERT, chars=str(output_text))

    # function for doing unavailable to use unnecessary entries in current selected account menu mode
    def account_radio_button_mode_selection(self):
        """
        function for doing unavailable to use unnecessary entries in current selected account menu mode
        :return: make unavailable unnecessary entries for current menu mode
        """
        # take current mode
        current_mode = self.account_selected_mode.get()
        # if account creation
        if current_mode == 0:
            # make unavailable new name and new password entries
            self.account_new_name_entry.configure(state="disabled")
            self.account_new_password_entry.configure(state="disabled")
        # if account edition
        if current_mode == 1:
            # make available new name and new password entries
            self.account_new_name_entry.configure(state="normal")
            self.account_new_password_entry.configure(state="normal")
        # if account deletion
        if current_mode == 2:
            # make unavailable new name and new password entries
            self.account_new_name_entry.configure(state="disabled")
            self.account_new_password_entry.configure(state="disabled")

    # function for doing unavailable to use unnecessary entries in current selected quote menu mode
    def quote_radio_button_mode_selection(self):
        """
        function for doing unavailable to use unnecessary entries in current selected quote menu mode
        :return: make unavailable unnecessary entries for current menu mode
        """
        # take current mode
        current_mode = self.quote_selected_mode.get()
        # if quote creation
        if current_mode == 0:
            # make available quote text entry
            self.quote_text_entry.configure(state="normal")
            # make unavailable quote id entry
            self.quote_id_entry.configure(state="disabled")
        # if quote edition
        if current_mode == 1:
            # make available quote text and quote id entry
            self.quote_text_entry.configure(state="normal")
            self.quote_id_entry.configure(state="normal")
        # if quote deletion
        if current_mode == 2:
            # make available quote id entry
            self.quote_id_entry.configure(state="normal")
            # make unavailable quote text entry
            self.quote_text_entry.configure(state="disabled")

    # function for doing unavailable to use unnecessary entries in current selected search menu mode
    def search_radio_button_mode_selection(self):
        """
        function for doing unavailable to use unnecessary entries in current selected search menu mode
        :return: make unavailable unnecessary entries for current menu mode
        """
        # take current mode
        current_mode = self.search_selected_mode.get()
        # if search by account name
        if current_mode == 0:
            # make available account name entry
            self.search_by_account_name_entry.configure(state="normal")
            # make unavailable quote id and quote text entries
            self.search_by_quote_id_entry.configure(state="disabled")
            self.search_by_text_entry.configure(state="disabled")
        # if search by quote id
        if current_mode == 1:
            # make available quote id entry
            self.search_by_quote_id_entry.configure(state="normal")
            # make unavailable account name and quote text entries
            self.search_by_account_name_entry.configure(state="disabled")
            self.search_by_text_entry.configure(state="disabled")
        # if search by quote text
        if current_mode == 2:
            # make available quote text entry
            self.search_by_text_entry.configure(state="normal")
            # make unavailable account name and quote id entries
            self.search_by_account_name_entry.configure(state="disabled")
            self.search_by_quote_id_entry.configure(state="disabled")

    # function for application GUI creation
    def gui_creation(self):
        """
        function for application GUI creation
        :return: main GUI window object and all text entries with text areas and modes variables
        """
        # # create GUI object
        main_window = tk.Tk()
        # add window title
        main_window.title("quote application")
        # change default window size
        # main_window.geometry('1000x800')

        # # variables

        # account select mode buttons column
        account_mode_column = 0
        # account menu entries column
        account_entries_column = 0
        # quote select mode buttons column
        quote_mode_column = 1
        # quote menu entries column
        quote_entries_column = 1
        # quote select mode buttons column
        search_mode_column = 2
        # quote menu entries column
        search_entries_column = 2

        # create variable for account menu mode index
        self.account_selected_mode = tk.IntVar()
        self.account_selected_mode.set(0)
        # create variable for quote menu mode index
        self.quote_selected_mode = tk.IntVar()
        self.quote_selected_mode.set(0)
        # create variable for search menu mode index
        self.search_selected_mode = tk.IntVar()
        self.search_selected_mode.set(0)

        # # labels and entries

        # add label of name menu
        account_label = tk.Label(master=main_window, text="Account management menu", font=("Arial Bold", 20))
        # set label position by grid function
        account_label.grid(column=account_entries_column, row=0)

        # add labels to account entries
        account_name_entry = tk.Label(master=main_window, text="Account Name: ", font=("Arial Bold", 10))
        account_password_entry = tk.Label(master=main_window, text="Account Password: ", font=("Arial Bold", 10))
        account_new_name_entry = tk.Label(master=main_window, text="New Account Name: ", font=("Arial Bold", 10))
        account_new_password_entry = tk.Label(master=main_window, text="New Account Password: ", font=("Arial Bold", 10))
        # set labels positions by grid function
        account_name_entry.grid(column=account_entries_column, row=4)
        account_password_entry.grid(column=account_entries_column, row=6)
        account_new_name_entry.grid(column=account_entries_column, row=8)
        account_new_password_entry.grid(column=account_entries_column, row=10)

        # add name, password and id textbox
        self.account_name_entry = tk.Entry(master=main_window, width=20)
        self.account_password_entry = tk.Entry(master=main_window, width=20)
        self.account_new_name_entry = tk.Entry(master=main_window, width=20, state="disabled")
        self.account_new_password_entry = tk.Entry(master=main_window, width=20, state="disabled")
        # set textbox positions by grid function
        self.account_name_entry.grid(column=account_entries_column, row=5)
        self.account_password_entry.grid(column=account_entries_column, row=7)
        self.account_new_name_entry.grid(column=account_entries_column, row=9)
        self.account_new_password_entry.grid(column=account_entries_column, row=11)

        # add execution label
        account_execute_label = tk.Label(master=main_window, text="Execute: ", font=("Arial Bold", 10))
        # set execution label on grid
        account_execute_label.grid(column=account_entries_column, row=12)

        # add output label
        account_output_label = tk.Label(master=main_window, text="Output: ", font=("Arial Bold", 10))
        # set output label on grid
        account_output_label.grid(column=account_entries_column, row=14)
        # add output textarea widget
        self.account_output_textarea = scrolledtext.ScrolledText(master=main_window, width=30, height=5)
        # set output textarea widget on grid
        self.account_output_textarea.grid(column=account_entries_column, row=15)

        # add label with menu name
        quote_label = tk.Label(master=main_window, text="Quote management menu", font=("Arial Bold", 20))
        # set label position by grid function
        quote_label.grid(column=quote_entries_column, row=0)

        # add labels to quote entries
        quote_account_name_label = tk.Label(master=main_window, text="Account Name: ", font=("Arial Bold", 10))
        quote_account_password_label = tk.Label(master=main_window, text="Account Password: ", font=("Arial Bold", 10))
        quote_text_label = tk.Label(master=main_window, text="Quote Text: ", font=("Arial Bold", 10))
        quote_id_label = tk.Label(master=main_window, text="Quote Id: ", font=("Arial Bold", 10))
        # set labels positions by grid function
        quote_account_name_label.grid(column=quote_entries_column, row=4)
        quote_account_password_label.grid(column=quote_entries_column, row=6)
        quote_text_label.grid(column=quote_entries_column, row=8)
        quote_id_label.grid(column=quote_entries_column, row=10)

        # add account name, account password, quote text and quote id textbox entry
        self.quote_account_name_entry = tk.Entry(master=main_window, width=20)
        self.quote_account_password_entry = tk.Entry(master=main_window, width=20)
        self.quote_text_entry = tk.Entry(master=main_window, width=20)
        self.quote_id_entry = tk.Entry(master=main_window, width=20, state="disabled")
        # set textbox positions by grid function
        self.quote_account_name_entry.grid(column=quote_entries_column, row=5)
        self.quote_account_password_entry.grid(column=quote_entries_column, row=7)
        self.quote_text_entry.grid(column=quote_entries_column, row=9)
        self.quote_id_entry.grid(column=quote_entries_column, row=11)

        # add execution label
        quote_execute_label = tk.Label(master=main_window, text="Execute: ", font=("Arial Bold", 10))
        # set execution label on grid
        quote_execute_label.grid(column=quote_entries_column, row=12)

        # add output label
        quote_output_label = tk.Label(master=main_window, text="Output: ", font=("Arial Bold", 10))
        # set output label on grid
        quote_output_label.grid(column=quote_entries_column, row=14)
        # add output textarea widget
        self.quote_output_textarea = scrolledtext.ScrolledText(master=main_window, width=30, height=5)
        # set output textarea widget on grid
        self.quote_output_textarea.grid(column=quote_entries_column, row=15)

        # add label with menu name
        search_label = tk.Label(master=main_window, text="Search of Quote menu", font=("Arial Bold", 20))
        # set label position by grid function
        search_label.grid(column=search_entries_column, row=0)

        # add labels to search entries
        search_by_account_name_label = tk.Label(master=main_window, text="Account Name: ", font=("Arial Bold", 10))
        search_by_quote_id_label = tk.Label(master=main_window, text="Quote Id: ", font=("Arial Bold", 10))
        search_by_text_label = tk.Label(master=main_window, text="Quote Text: ", font=("Arial Bold", 10))
        # set labels positions by grid function
        search_by_account_name_label.grid(column=search_entries_column, row=4)
        search_by_quote_id_label.grid(column=search_entries_column, row=6)
        search_by_text_label.grid(column=search_entries_column, row=8)

        # add account name, quote id and quote text textbox entry
        self.search_by_account_name_entry = tk.Entry(master=main_window, width=20)
        self.search_by_quote_id_entry = tk.Entry(master=main_window, width=20, state="disabled")
        self.search_by_text_entry = tk.Entry(master=main_window, width=20, state="disabled")
        # set textbox positions by grid function
        self.search_by_account_name_entry.grid(column=search_entries_column, row=5)
        self.search_by_quote_id_entry.grid(column=search_entries_column, row=7)
        self.search_by_text_entry.grid(column=search_entries_column, row=9)

        # add execution label
        search_execute_label = tk.Label(master=main_window, text="Execute: ", font=("Arial Bold", 10))
        # set execution label on grid
        search_execute_label.grid(column=search_entries_column, row=10)

        # add output label
        search_output_label = tk.Label(master=main_window, text="Output: ", font=("Arial Bold", 10))
        # set output label on grid
        search_output_label.grid(column=search_entries_column, row=12)
        # add output textarea widget
        self.search_output_textarea = scrolledtext.ScrolledText(master=main_window, width=30, height=5)
        # set output textarea widget on grid
        self.search_output_textarea.grid(column=search_entries_column, row=13)

        # # buttons

        # add account radio buttons for changing between creating-editing-deleting
        account_menu_mode_crating = tk.Radiobutton(master=main_window, text='Create', value=0,
                                                   variable=self.account_selected_mode,
                                                   command=self.account_radio_button_mode_selection)
        account_menu_mode_editing = tk.Radiobutton(master=main_window, text='Edit', value=1,
                                                   variable=self.account_selected_mode,
                                                   command=self.account_radio_button_mode_selection)
        account_menu_mode_deleting = tk.Radiobutton(master=main_window, text='Delete', value=2,
                                                    variable=self.account_selected_mode,
                                                    command=self.account_radio_button_mode_selection)
        # add radio buttons to grid
        account_menu_mode_crating.grid(column=account_mode_column, row=1)
        account_menu_mode_editing.grid(column=account_mode_column, row=2)
        account_menu_mode_deleting.grid(column=account_mode_column, row=3)

        # add quote radio buttons for changing between creating-editing-deleting
        quote_menu_mode_crating = tk.Radiobutton(master=main_window, text='Create', value=0,
                                                 variable=self.quote_selected_mode,
                                                 command=self.quote_radio_button_mode_selection)
        quote_menu_mode_editing = tk.Radiobutton(master=main_window, text='Edit', value=1,
                                                 variable=self.quote_selected_mode,
                                                 command=self.quote_radio_button_mode_selection)
        quote_menu_mode_deleting = tk.Radiobutton(master=main_window, text='Delete', value=2,
                                                  variable=self.quote_selected_mode,
                                                  command=self.quote_radio_button_mode_selection)
        # add radio buttons to grid
        quote_menu_mode_crating.grid(column=quote_mode_column, row=1)
        quote_menu_mode_editing.grid(column=quote_mode_column, row=2)
        quote_menu_mode_deleting.grid(column=quote_mode_column, row=3)

        # add search radio buttons for changing between creating-editing-deleting
        search_menu_mode_crating = tk.Radiobutton(master=main_window, text='By Account Name', value=0,
                                                  variable=self.search_selected_mode,
                                                  command=self.search_radio_button_mode_selection)
        search_menu_mode_editing = tk.Radiobutton(master=main_window, text='By Quote Id', value=1,
                                                  variable=self.search_selected_mode,
                                                  command=self.search_radio_button_mode_selection)
        search_menu_mode_deleting = tk.Radiobutton(master=main_window, text='By Quote Text', value=2,
                                                   variable=self.search_selected_mode,
                                                   command=self.search_radio_button_mode_selection)
        # add radio buttons to grid
        search_menu_mode_crating.grid(column=search_mode_column, row=1)
        search_menu_mode_editing.grid(column=search_mode_column, row=2)
        search_menu_mode_deleting.grid(column=search_mode_column, row=3)

        # add account execution button
        account_execute_button = tk.Button(master=main_window, text="Execute", command=self.account_execution)
        # set button position by grid
        account_execute_button.grid(column=account_entries_column, row=13)

        # add quote execution button
        quote_execute_button = tk.Button(master=main_window, text="Execute", command=self.quote_execution)
        # set button position by grid
        quote_execute_button.grid(column=quote_entries_column, row=13)

        # add search execution button
        search_execute_button = tk.Button(master=main_window, text="Execute", command=self.search_execution)
        # set button position by grid
        search_execute_button.grid(column=search_entries_column, row=11)

        # return main GUI window object
        return main_window

    # function for application run
    @connection_check_decorator
    def run_application(self, *args, **kwargs):
        """
        function for application run
        :param args: all Tk.mainloop() *args
        :param kwargs: all Tk.mainloop() **kwargs
        :return: run GUI mainloop
        """
        # run application main loop
        self.gui.mainloop(*args, **kwargs)
















