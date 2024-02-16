import Config

ConfigSettings = Config.ConfigSettings

class ConfigInput:
    """Configuration input session:
        Enter the following commands to view or edit Session Configurations.
    """

    def __init__(self) -> None:
        self.killStr = ""
        self.killStrMandatory = False   # Convert the kill string to become necessary
        self.basePrompt = "Enter valid command, or \"help\":"
        self.comms = {"help": Help, "view": View, "edit": Edit, "add": AddConfig}
        self.handleCommand = self.commandCall
    
    def commandCall(self, comm):
        self.comms[comm]().runTime()

    def runTime(self):
        run = True
        while run:
            comm = input(self.basePrompt).rstrip()
            if (comm == self.killStr and not self.killStrMandatory) or \
                    (comm != self.killStr and self.killStrMandatory):
                break
            if comm not in self.comms and self.comms:
                continue
            self.handleCommand(comm)

class Help(ConfigInput):
    def __init__(self) -> None:
        super().__init__()
        self.basePrompt = "Press Enter to see help texts: "
        self.killStrMandatory = True
        self.comms = {}

    def runTime(self):
        print("Displaying help for various commands:")
        print(ConfigInput.__doc__)
        print(View.__doc__)
        print(Edit.__doc__)
        print(AddConfig.__doc__)

        #input()

class Edit(ConfigInput):
    """\"edit\"
        Edit a specific configuration.
        >Configuration ID
        >App or URL identifier
        >Edit, add or delete a file path or URL
    """
    def __init__(self):
        super().__init__()
        self.basePrompt = "Enter valid configuration ID to edit: "
        self.comms = Config.get_configs()
        self.handleCommand = self.editConfig
    
    def editConfig(self, comm):
        if comm not in Config.get_config_ids(): return
        EditConfig(comm).runTime()

class EditConfig(Edit):
    def __init__(self, configID):
        super().__init__()
        self.config = Config.open_config(configID)
        self.basePrompt = "Enter valid App identifier to edit, or NEW to add a setting: "
        self.handleCommand = self.editApp
        self.comms = list(self.config.URLS.keys()) + list(self.config.appPaths.keys()) + ["NEW", "DELETE"]

    def editApp(self, comm):
        if comm == "NEW":
            AddPath(self.config.id).runTime()
            return
        if comm == "DELETE":
            Config.delete_config(self.configID)
        if comm in self.config.URLS.keys(): 
            EditURL(comm, self.config.id).runTime()
        else:
            EditApp(comm, self.config.id).runTime()

class AddPath(EditConfig):
    def __init__(self, configID):
        super().__init__(configID)
        self.basePrompt = "Enter the setting type (APP / URL / WEB) followed by name of new setting: "
        self.handleCommand = self.newApp
        self.comms = []
    
    def newApp(self, name):
        try:
            if name[:3] == "APP" or name[:3] == "WEB":
                EditApp(name[4:], self.config.id).runTime()
                if name[:3] == "WEB":
                    self.config.webApp = name[4:]
            elif name[:3] == "URL":
                EditURL(name[4:], self.config.id).runTime()
            #print(name][])
        except IndexError:
            return

class EditApp(EditConfig):
    def __init__(self, appID, configID):
        super().__init__(configID)
        self.appID = appID
        self.handleCommand = self.handle
        self.basePrompt = f"DEL or EDIT the settings for {self.appID} : "
        self.comms = ["DEL", "EDIT"]
    
    def handle(self, comm):
        if comm == "DELETE" and self.appID in self.config.appPaths:
            self.config.appPaths.pop(self.appID)
        elif comm == "EDIT":
            run = True
            while run:
                newPath = input(f"Enter new filepath for {self.appID}, or store as the web app with WEB: ").rstrip().replace("\"", "")
                if newPath == "WEB":
                    self.config.webApp = self.appID
                if newPath.endswith(".exe"):
                    self.config.appPaths[self.appID] = newPath
                    run = False
                if newPath == self.killStr:
                    break
        
        Config.save_config(self.config)

class EditURL(EditConfig):
    def __init__(self, URL_ID, configID):
        super().__init__(configID)
        self.URL_ID = URL_ID
        self.comms = ["DEL", "EDIT"]
        self.handleCommand = self.handle
        self.basePrompt = f"DEL or EDIT the URL for {self.URL_ID}"
    
    def handle(self, comm):
        if comm == "DELETE":
            self.config.URLS.pop(self.URL_ID)
        elif comm == "EDIT":
            newPath = input(f"Enter new filepath for {self.URL_ID}: ").rstrip()
            if newPath != self.killStr:
                self.config.URLS[self.URL_ID] = newPath
        
        Config.save_config(self.config)

class AddConfig(ConfigInput):
    """\"add\"
        Add a new configuration setting.
        >Config name
        >Edit Config settings
    """
    def __init__(self) -> None:
        super().__init__()
        self.basePrompt = "Enter new name for Configuration: "
        self.handleCommand = self.addApp
        self.comms = []
    
    def addApp(self, name):
        con = ConfigSettings(name)
        Config.save_config(con)
        EditConfig(name).runTime()

class View(ConfigInput):
    """\"view\"
        View either a specific configuration, or view a list of all saved configurations.
    """
    def __init__(self) -> None:
        super().__init__()
        self.basePrompt = "Enter configuration ID to view, or \"ids\" to view all identifiers: "
        self.comms = Config.get_configs()
        self.comms["ids"] = self.give_ids
        self.handleCommand = self.viewConfig
    
    def viewConfig(self, key):
        if key == "ids":
            self.give_ids()
            return
        print(Config.open_config(key))

    def give_ids(self):
        #print(self.comms)
        for comm in self.comms:
            if comm == "ids": continue
            print(f"    ID: {comm}")
        input()


def main():
    x = ConfigInput()
    x.runTime()

if __name__ == "__main__":
    main()
