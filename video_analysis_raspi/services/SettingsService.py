import getopt
import logging
import sys

import requests

from video_analysis_raspi.model.Settings import Settings


class SettingsService:
    settings: Settings

    def __init__(self, cmd_argv):
        self.settings = Settings()
        try:
            opts, args = getopt.getopt(cmd_argv, "hs:u:p:", ["server=", "username=", "password="])
        except getopt.GetoptError:
            print('app.py -s <server_address> -u <username_server> -p <password_server>')
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print('app.py -s <server_address> -u <username_server> -p <password_server>')
                sys.exit()
            elif opt in ("-s", "--server"):
                self.settings.server_url_base = arg
            elif opt in ("-u", "--username"):
                self.settings.server_user = arg
            elif opt in ("-p", "--password"):
                self.settings.server_pwd = arg

        self.log_in_to_server()

    def get_settings(self):
        pass

    def get_setting(self, setting_name):
        pass

    def change_setting(self, setting_name):
        pass

    def log_in_to_server(self):
        url_login = self.settings.server_url_base + self.settings.server_url_login
        login_data = {
            'username': self.settings.server_user,
            'password': self.settings.server_pwd
        }
        response = requests.post(url_login, json=login_data)
        if response.ok:
            logging.info("Log-in to server was successful")
        else:
            logging.warning("Could not connect to server --> log in failed")
        self.settings.server_jwt = response.json()['jwt']
        self.settings.server_auth_header = {'Authorization': 'Bearer {}'.format(self.settings.server_jwt)}
