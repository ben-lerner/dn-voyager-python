import requests
import json

_VOYAGER_API = "http://api.datanitro.com/v1"
#_VOYAGER_API = "http://localhost:8000/v1"

class VoyagerError(Exception):
    def __init__(self, error_code, error_message):
        ''' Error_code represents a non-200 HTTP error code;
        errro_code = None if the error is cought locally in python client '''
        super(VoyagerError, self).__init__(error_message)
        self.error_message = error_message
        self.error_code = error_code

    def __str__(self):
        out = ""
        if self.error_code:
            out += str(self.error_code) + ": "
        if self.error_message:
            out += self.error_message
        else:
            out += "Error"
        return out

class VoyagerHttp(object):
    def __init__(self, timeout=5.0):
        self.access_token = None
        self.uid = None
        self.timeout = timeout

    def authorize(self, access_token, email, pwd):
        ''' Authorizes user either through access_token or 
        through email and pwd, but not both;
        raises VoyagerError on failure '''
        if not access_token and not email:
            raise VoyagerError(None, "Please specify access_token or email/pwd")
        if access_token and (email or pwd):
            raise VoyagerError(None, "Authorize through access_token or email/pwd, but not both")
        
        data = None
        if access_token:
            data = {"access_token" : access_token}
        else:
            data = {"email" : email,
                    "pwd" : pwd}

        response = None
        try:
            response = requests.post(_VOYAGER_API + "/auth", 
                                     headers=None, 
                                     data=json.dumps(data),
                                     timeout=self.timeout)
            response.raise_for_status()
            response_json = response.json()
            self.access_token = response_json["token"]
            self.uid = response_json["uid"]
        except requests.exceptions.HTTPError as ex:
            msg = None
            try:
                # try to extract error message from the server, is possible
                js = response.json()
                msg = js["message"]
            except Exception:
                msg = str(ex)
            raise VoyagerError(response.status_code, msg)
        # success, we're done
        

    def send_request(self, method, endpoint, headers=None, data=None):
        ''' Sends a request to Voyager's server and returns a json (dict) response,
        raises VoyagerError on failure '''
        if not self.access_token:
            raise VoyagerError(401, 'Unauthorized')
        req_methods = { "get" : requests.get,
                        "post" : requests.post,
                        "put" : requests.put,
                        "delete" : requests.delete }
        method = method.lower()
        if not method in req_methods:
            raise KeyError()
        
        all_headers = {}
        if headers:
            all_headers = headers
        all_headers["token"] = self.access_token

        # print "data = " + str(data)
        # print "sending data = " + str(json.dumps(data))
        response = None
        try:
            response = req_methods[method](_VOYAGER_API + endpoint,
                                           headers=all_headers,
                                           data=json.dumps(data), 
                                           timeout = self.timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            msg = None
            try:
                # try to extract error message from the server, is possible
                js = response.json()
                msg = js["message"]
            except Exception:
                msg = str(ex)
            raise VoyagerError(response.status_code, msg)

        # possible data conversion (datetime) issue
        return response.json()
                                                   




