"""run application"""


# import defs
import defs


# function for app starting
def application_run():
    # create application object
    application = defs.Application()
    # create connection to database
    application.create_database_connection(host_name="127.0.0.1", port_name="3306", user_name="root",
                                           user_password="1234567890", database_name="quote_application")
    # run application GUI
    application.run_application()


# run application
if __name__ == "__main__":
    application_run()
















