from http_client import VoyagerHttp, VoyagerError
import voyager_version
import user
import table

class Client(object):
    def __init__(self):
        self._http_client = None

    def _send_request(self, method, endpoint, headers=None, data=None):
        ''' for internal use only;
        sends a request to the api server '''
        return self._http_client.send_request(method, endpoint, headers, data)

    def _check_auth(self):
        if not self._http_client:
            raise VoyagerError(error_code=None, 
                               error_message="Please authorize Voyager client first")

    def initialize(self, access_token=None, email=None, pwd=None, timeout=5.0):
        ''' Authorizes the client and initializes internal structures; Authorize
        using your own access_ token (available at console.datanitro.com), 
        or with your email and password combination. Default timeout is 5 sec. '''
        new_http_client = VoyagerHttp(timeout)
        new_http_client.authorize(access_token, email, pwd)
        self._http_client = new_http_client

    def get_all_tables(self):
        ''' Returns the list of all (public and private) tables accessible
        by the authorized user '''
        resp = self._send_request("GET", "/user/" + self._http_client.uid + "/tables_accessible")
        return [ table.Table._load_from_dict(t) for t in resp["tables"]]

    def get_all_tables_sources(self):
        ''' Returns the list of users that share tables with me '''
        self._check_auth()
        resp = self._send_request("GET", 
                                  "/user/" + self._http_client.uid + "/target_access")
        return [user.User._load_from_dict(user_dict) for user_dict in resp["users"]]

    def get_my_tables(self):
        ''' Returns user's repository (list of private tables) '''
        resp = self._send_request("GET", "/user/" + self._http_client.uid + "/tables_owned")
        return [ table.Table._load_from_dict(t) for t in resp["tables"]]

    def get_my_users(self):
        ''' Returns the list of users with general (read-)access to my repository '''
        self._check_auth()
        resp = self._send_request("GET", 
                                  "/user/" + self._http_client.uid + "/source_access")
        return [user.User._load_from_dict(user_dict) for user_dict in resp["users"]]

    @classmethod
    def version(cls):
        return voyager_version.VERSION

