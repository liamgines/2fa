from flask import session

class Session:
    count = 0
    drivers = []

    @property
    def id(self):
        return session["id"]

    @id.setter
    def id(self, value):
        session["id"] = value

    @property
    def driver(self):
        return self.drivers[session["id"]]

    @property
    def name(self):
        return session["name"]

    @name.setter
    def name(self, value):
        session["name"] = value

    @property
    def password(self):
        return session["password"]

    @password.setter
    def password(self, value):
        session["password"] = value

    @property
    def password_changed(self):
        return session["password_changed"]

    @password_changed.setter
    def password_changed(self, value):
        session["password_changed"] = value
