import voyager

class User(object):
    def __init__(self, uid, email, display_name, company, creation_date, _is_admin=False):
        # uid & email are never empty
        self.uid = uid
        self.email = email
        self.display_name = display_name
        self.company = company
        self.creation_date = creation_date
        self._is_admin = _is_admin

    def __str__(self):
        if self.display_name and self.company and self.creation_date:
            return "Voyager User " + self.display_name + " (" + self.email + ")"
        return "Voyager User " + self.email

    def _delete(self):
        ''' internal use only '''
        raise NotImplementedError()

    def remove(self):
        ''' Removes user from the repository's (read-) permission list '''
        # ISSUE: add/remove repo are inconsistent
        voyager.client._send_request(
            "DELETE", 
            "/user/" + voyager.client._http_client.uid + "/source_access",
            data={"target_uid" : self.uid})

    @classmethod
    def create(cls, email):
        ''' creates a new user on the server, and adds it to 
        requester's repository (read-) permissions list
        returns a User object, as it is represented on the server;
        if it's a registered user, returns all fields (name, company etc.)
        otherwise (ie. invitation to the repo), returns a basic user 
        object with only the email & uid fields '''
        resp = voyager.client._send_request(
            "POST", 
            "/user/" + voyager.client._http_client.uid + "/source_access",
            data={"target_email" : email})
        # only uid and email are guaranteed to be non-null
        return User._load_from_dict(resp)

    @classmethod
    def _load(cls, uid):
        ''' loads user from uid or email, if authenticated user has sufficient permission,
        returns a User object, as it is represented on the server;
        if it's a registered user, returns all fields (name, company etc.)
        otherwise, returns a basic user object with only the email field '''
        resp = voyager.client._send_request("GET", "/user/" + uid)
        return User._load_from_dict(resp)

    @classmethod
    def _load_from_dict(cls, user_dict):
        return User(user_dict["uid"], user_dict["email"], user_dict["display_name"],
                    user_dict["company"], user_dict["creation_date"])
