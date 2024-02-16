from subprocess import Popen
import webbrowser
from os import system
from psutil import process_iter, boot_time
from datetime import datetime, time as datetime_time, timedelta
from sys import argv, executable
from logging import getLogger, basicConfig

import Config
import ConfigSession

logger = getLogger("SessionShortcut")
ConfigSettings = Config.ConfigSettings  
logPath = r"ConfigSettings\Log.txt"

autoOpenTime = [6, 30, 0]
autoOpenThreshold = 30

class Session:
    """A session object for opening and tracking work done on a given project."""
    def __init__(self, config, autoExe=False):
        """Initialize object"""
        self.config = config

        print("Welcome, Aarnold.")
        self.exeType = "Auto  " if autoExe else "Manual"

        self.open_processes = {}
        self.opened_pids = []

        self.startTime = None
        self.endTime = None
        self.sessionLen = None

    def startup(self):
        """Open a Kurslar work session and all related apps"""

        if self.config.appPaths:
            for app, path in zip(self.config.appPaths.keys(), self.config.appPaths.values()):
                if app == self.config.webApp and path.split("\\")[-1] in (i.name() for i in process_iter()): continue
                self.open_processes[app] = Popen(path, shell=False)
                self.opened_pids.append(self.open_processes[app].pid)

        # Open relevant tabs in the specified web application
        if "chrome.exe" in (i.name() for i in process_iter()) and self.config.URLS:
            webbrowser.register("Chrome_", None, webbrowser.BackgroundBrowser(self.config.appPaths[self.config.webApp]))
            for url in self.config.URLS.values():
                webbrowser.get("Chrome_").open_new_tab(url)
        self.startTime = datetime.now()

        logger.info("Session started: {}".format(self.startTime))

    def writeLog(self):
        """Save session information"""

        with open(logPath, "a") as logFile:
            logTxt = "\n" + str(self.startTime) + " | " + str(self.endTime) + " | " + str(self.sessionLen) + " | " + \
                self.exeType
            logFile.write(logTxt)
        logger.info(" Session info logged to \"{}\"".format(self.logPath))

    def time_diff(self, start, end):
        """Calculate difference between datetime A and datetime B"""

        if isinstance(start, datetime_time):  # convert to datetime
            assert isinstance(end, datetime_time)
            start, end = [datetime.combine(datetime.min, t) for t in [start, end]]
        if start <= end:  # e.g., 10:33:26-11:15:49
            return end - start
        else:  # end < start e.g., 23:55:00-00:25:00
            end += timedelta(1)  # +day
            assert end > start
            return end - start

    def terminate(self, logTime=True, kill=False):
        """Terminate a work session"""

        if logTime:
            self.endTime = datetime.now()
            self.sessionLen = self.time_diff(self.startTime, self.endTime)

            self.writeLog()

        logger.info("Session Length: {}".format(self.sessionLen))
        logger.warning("Closing processes: {}".format(", ".join(self.open_processes.keys())))
        for process in self.open_processes.values():
            if process.pid not in self.opened_pids: continue
            system("Taskkill /PID %d /F" % process.pid)
        print("Have a nice day, Aarnold.")
        input()

def open_session(id, exeType):
    config = Config.open_config(id)
    session = Session(config, exeType)

    try:
        session.startup()
        input("Exit session\n")
        session.terminate()
    except Exception as error:
        logger.error(f"Exception found: {error}")
        session.terminate(logTime=False)

def main():
    basicConfig(level="INFO")  # Logging config
    logger.info(f"Program interpreter: {executable}")

    boot = datetime.fromtimestamp(boot_time())
    boot_distance = datetime.now() - boot

    exeType = boot_distance.total_seconds() < autoOpenThreshold or "--auto" in argv

    config_options = Config.get_config_ids()
    sessionID = ""

    while True:
        sessionID = input("Enter session or exit: ")
        if sessionID == "config":
            ConfigSession.main()
            config_options = Config.get_config_ids()
            continue
        if sessionID == "exit":
            break
        if sessionID not in config_options: 
            print("Select a valid session ID: ")
            continue

        open_session(sessionID, exeType)

if __name__ == '__main__':
    main()
