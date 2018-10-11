import json
import requests
from urllib import parse
import mcsettings as URL


class Cloud():
    """main class with mail.ru cloud APIs"""

    def __init__(self, email="", password=""):
        self.__password__ = password
        self.email = email
        self.response = None
        self.authorized = False
        self.token = ""
        self.cookies = {}
        self.loader = ""

    def __auth__(self):
        values = {"Login": self.email, "Password": self.__password__}
        self.response = requests.get(URL.AUTH, params=values)
        if self.response.status_code == requests.codes.ok:
            self.authorized = True
            self.cookies = dict(self.response.cookies)
        else:
            self.authorized = False

    def __get_token__(self):
        """update token"""
        values = {"email": self.email}
        self.response = requests.get(
            URL.TOKEN, params=values, cookies=self.cookies)
        self.token = json.loads(self.response.text)["body"]["token"].strip()
        return self.token

    def login(self):
        """login cloud to start work """
        self.__auth__()
        self.__get_token__()

    def logout(self):
        self.response = requests.post(URL.LOGOUT, cookies=self.cookies)
        if self.response.status_code == requests.codes.ok:
            self.authorized = False
            self.cookies = {}
            self.token = ""
        else:
            self.authorized = True

    def __get_loader__(self):
        """get the load server """
        self.response = requests.get(URL.DISPATCHER)
        self.loader = self.response.text.split(" ")[0]

    def __load_file__(self, filepath=""):
        """load file to cloclo, and return dict with params"""
        path = [i for i in filepath.split('/') if i]
        filename = path.pop()
        with open(filepath, 'rb') as f:
            fd = {'file': f}
            values = {"Content_Type": "multipart/form-data",
                      "Content": {"file": filename}}
            self.response = requests.post(
                self.loader, params=values, files=fd, cookies=self.cookies)

        ls = self.response.text.split(";")

        if self.response.status_code == requests.codes. and ls:
            return {"name": ls[1].strip(),
                    "hash": ls[0].strip(),
                    "size": ls[2].strip()
                    }
        else:
            return None

    def __link_file__(self, file_params, cloud_path):
        """Finaly add link of loaded file into cloud """
        if self.add_folder(cloud_path):
            body = parse.urlencode({
                "folder": cloud_path,
                "files": json.dumps([{
                    "name": file_params["name"],
                    "size":file_params["size"],
                    "hash":file_params["hash"],
                }]),
                "api": 1,
                "email": self.email,
                "storage": "home",
                "token": self.token,
            })
            self.response = requests.post(
                URL.ADDFILE, data=body, cookies=self.cookies)
            return self.response.status_code == requests.codes.ok
        else:
            return False

    def add_folder(self, full_folder_name=""):
        """Generate full path to file every time, even if exist """
        ls = full_folder_name.split('/')
        cls = [item for item in ls if item]
        parpath = ""
        for foldername, parent in self.__gen_parents__(cls):
            parpath += "/"+parent
            body = parse.urlencode({
                "add": json.dumps([{
                    "folder": parpath,
                    "name": foldername,
                }]),
                "api": 1,
                "email": self.email,
                "storage": "home",
                "token": self.token,
            })
            self.response = requests.post(
                URL.ADDFOLDER, data=body, cookies=self.cookies)
        return self.response.status_code == requests.codes.ok

    def __gen_parents__(self, ls):
        f = []
        par = "/"
        for i in ls:
            if par == "/":
                f.append((i, par))
                par = i
            else:
                f.append((i, par))
                par = i
        return f

    def add_file(self, local_path, cloud_path):
        """Load file into cloud 
        -- local_path = path on the local machine
        -- cloud_path = path you want to load in cloud , if not exists will be created
         """
        self.__get_loader__()
        params = self.__load_file__(local_path)
        self.__link_file__(params, cloud_path)

    def share(self, filename_with_path=""):
        """share the file from cloud """
        body = parse.urlencode({
            "ids": json.dumps([filename_with_path]),
            "api": 1,
            "email": self.email,
            "storage": "home",
            "token": self.token,
        })
        self.response = requests.post(
            URL.SHARE, data=body, cookies=self.cookies)
        if self.response.status_code == requests.codes.ok:
            return self.response.json()["body"][0]["url"]["get"]
        else:
            return None

    def unshare(self, filename_with_path=""):
        """unshare the file """
        body = parse.urlencode({
            "ids": json.dumps([filename_with_path]),
            "api": 1,
            "email": self.email,
            "storage": "home",
            "token": self.token,
        })
        self.response = requests.post(
            URL.UNSHARE, data=body, cookies=self.cookies)
        return self.response.status_code == requests.codes.ok

    def remove(self, full_path=""):
        """Remove files, folders all of them, use CAREFULL """
        body = parse.urlencode({
            "ids": json.dumps([full_path]),
            "api": 1,
            "email": self.email,
            "storage": "home",
            "token": self.token,
        })
        self.response = requests.post(
            URL.REMOVE, data=body, cookies=self.cookies)
        return self.response.status_code == requests.codes.ok

    def move(self, current_path="", target_path=""):
        """Move file or folder in cloud """
        body = parse.urlencode({
            "folder": target_path,
            "ids": json.dumps([current_path]),
            "api": 1,
            "email": self.email,
            "storage": "home",
            "token": self.token,
        })
        self.response = requests.post(
            URL.MOVE, data=body, cookies=self.cookies)
        return self.response.status_code == requests.codes.ok

    def rename(self, current_name="", target_name=""):
        """Rename file or folder in cloud 
        -- current_name = full path + name 
        -- target_name = only name of file
        """
        body = parse.urlencode({
            "rename": json.dumps([{
                "id": current_name,
                "name": target_name,
            }]),
            "api": 1,
            "email": self.email,
            "storage": "home",
            "token": self.token,
        })
        self.response = requests.post(
            URL.RENAME, data=body, cookies=self.cookies)
        return self.response.status_code == requests.codes.ok
