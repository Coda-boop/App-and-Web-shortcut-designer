from shelve import open
from logging import getLogger

logger = getLogger("SessionTracker")

class ConfigSettings:
    def __init__(self, identifier, appPaths=None, URLS=None, webApp="") -> None:
        self.id = identifier

        if appPaths is None: self.appPaths = {}
        else: self.appPaths = appPaths.copy()

        if URLS is None: self.URLS = {}
        else: self.URLS = URLS.copy()

        self.webApp = webApp
    
    def __repr__(self) -> str:
        return "ConfigSettings{}".format(str(tuple(self.appPaths.keys())))

    def __str__(self) -> str:
        formatted = "Configuration identifier: " + self.id
        for (app, path) in zip(self.appPaths.keys(), self.appPaths.values()):
            formatted += f"\n    {app}: {path}"
            
            if app == self.webApp:
                for (webpage, link) in zip(self.URLS.keys(), self.URLS.values()):
                    formatted += f"\n        {webpage}: {link}"
        return formatted


    def add_app(self, name, path) -> None:
        assert path.endswith(".exe")
        self.appPaths[name] = path
    
    def add_url(self, name, path) -> None:
        self.appPaths[name] = path
    
    def remove_app(self, name) -> None:
        self.appPaths.pop(name)
    
    def remove_url(self, name):
        self.URLS.pop(name)
    
def save_config(config):
    with open(configPath) as db:
        db[config.id] = config

def open_config(id):
    assert id in get_config_ids()
    with open(configPath) as db:
        return db[id]

def get_config_ids():
    with open(configPath) as db:
        return list(db.keys())

def get_configs():
    with open(configPath) as db:
        return dict(zip(db.keys(), db.values()))

def delete_config(id):
    assert id in get_config_ids()
    with open(configPath) as db:
        db.pop(id)

configPath = r"Source\ConfigSettings\Config"

def main():
    appPaths = {
            "Chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "Obsidian": r"C:\Users\Aarni\AppData\Local\Obsidian\Obsidian.exe",
            }
    chromeURLS = {
        "script": r"https://docs.google.com/document/d/1RtES8Z8pvNoZrZoO-hSuiLyu36CEPMhuqT5p7xYSbDs/edit",
        "slides": r"https://docs.google.com/presentation/u/0/",
        "docs": r"https://docs.google.com/document/u/0/",
        "plan": r"https://docs.google.com/document/d/1u8TLwlRFtRz2CajuCusf8AAwMHtLh721LaSC9-JXBnY/edit#heading=h.ch4bstwr9nt1 "
            }
    con = ConfigSettings("kurslar", appPaths=appPaths, URLS=chromeURLS, webApp="Chrome")
    save_config(con)
    #open_config("kurslar")

if __name__ == "__main__":
    main()