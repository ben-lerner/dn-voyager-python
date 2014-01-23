import base64
import sys
from http_client import VoyagerError
import voyager

class Table(object):
    def __init__(self, tid, name, description):
        self.tid = tid
        self.name = name
        self.description = description

    def __str__(self):
        return self.name

    # potentially tid/name/description as attributes with http requests?
    # or just a single update function for everything?

    def get_value(self, y, x):
        val = None
        try:
            resp = voyager.client._send_request("GET", 
                                                "/table/" + self.tid + "/" + str(y) + "/" + str(x))
            val = resp["val"]
        except VoyagerError as ex:
            if ex.error_code == 404:
                val = None
            else:
                raise ex
        return val

    def put_value(self, y, x, value):
        resp = voyager.client._send_request("POST", 
                                            "/table/" + self.tid + "/" + str(y) + "/" + str(x),
                                            data={"val" : value})

    def download_sample(self):
        ''' Returns table's sample data (a list of lists of top-left 10x10 cells) '''
        resp = voyager.client._send_request("GET", "/table/" + self.tid + "/sample")
        sample = [ [None] * 10 for y in range(10) ]
        for point in resp["sample"]:
            # print "point = " + str(point)
            sample[point["y"]][point["x"]] = point["val"]
        return sample

    def download_data(self):
        ''' Returns table's entire data set (2D: list of lists) '''
        resp = voyager.client._send_request("GET", "/table/" + self.tid)
        if len(resp["data"]) == 0:
            #sys.stderr.write("\n1\n")
            return [[]]
        max_y = 1
        max_x = 1
        for point in resp["data"]:
            max_y = max(max_y, point["y"])
            max_x = max(max_x, point["x"])
        data = [ [None] * (max_x + 1) for y in range(max_y + 1)]
        # sys.stderr.write("got resp = " + str(resp["data"]))
        for point in resp["data"]:
            data[point["y"]][point["x"]] = point["val"]
        # sys.stderr.write("\nreturning data = " + str(data) + "\n")
        return data

    def upload_data(self, data):
        ''' Uploads data set to the table. Data should be a (2D) list of lists of value '''
        list_dict = []
        for y, row in enumerate(data):
            for x, cell in enumerate(row):
                list_dict.append({"y" : y,
                                  "x" : x,
                                  "val" : cell})
        voyager.client._send_request("POST", "/table/" + self.tid,
                                     data={"data" : list_dict,
                                           "data_type" : "list"})

    def upload_data_csv(self, csv_data):
        ''' Uploads data set to the table. Data should be a comma separated string '''
        data = base64.b64encode(csv_data)
        voyager.client._send_request("POST", "/table/" + self.tid,
                                     data={"data" : data,
                                           "data_type" : "csv"})

    def erase_data(self):
        ''' Erases all data from the table '''
        self.upload_data([[]])

    def drop(self):
        ''' Deletes the entire table, its data set and the user access list '''
        voyager.client._send_request("DELETE", "/table/" + self.tid)

    def get_users(self):
        ''' Returns the list of users with read-access to this table '''
        response = voyager.client._send_request("GET", "/table/" + self.tid + "/users")
        return [voyager.User._load_from_dict(user_dict) for user_dict in response["users"]]

    def add_user(self, user):
        ''' Adds user the read-only access list '''
        voyager.client._send_request("POST", "/table/" + self.tid + "/users/" + user.uid)

    def remove_user(self, user):
        ''' Removes user from the read-only access list '''
        voyager.client._send_request("DELETE", "/table/" + self.tid + "/users/" + user.uid)

    def has_access(self, user):
        ''' Returns a boolean indicating user has read-access to this table '''
        response = voyager.client._send_request("GET", "/table/" + self.tid + "/users/" + user.uid)
        return response["access"]

    def save(self):
        ''' Save the changes to table's name & description back to the Voyager server '''
        response = voyager.client._send_request("POST", "/table/" + self.tid,
                                                data={"name" : self.name,
                                                      "description" : self.description})
        return None

    @classmethod
    def create(cls, name, description):
        ''' Creates a new empty table '''
        resp = voyager.client._send_request("POST", "/table/", 
                                            data={"name" : name,
                                                  "description" : description})
        return Table(resp["tid"], name, description)

    @classmethod
    def _load(cls, tid):
        ''' Loads a table tid (only metadata) '''
        resp = voyager.client._send_request("GET", "/table/" + tid)
        return Table._load_from_dict(resp)
        
    @classmethod
    def _load_from_dict(cls, table_dict):
        return Table(table_dict["tid"], table_dict["name"], table_dict["description"])

    

        
