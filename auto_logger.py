import utils 
import os
import log
import json

class AutoLogger:
    def __init__(self, custom_data_file = None):
        #TODO - add proper cli parser arguments for this instead of environment variable)
        
        if os.path.exists("remote_config.json"):
            conf = open("remote_config.json", 'r')
            config = json.load(conf)
            remote = os.path.join(config['backup_dir'], config['computer_id'])
            log.info("Attemping to mounting OneDrive:cateye to {}".format(remote))
            os.system("rclone mount cateye:cateye {} --allow-non-empty --vfs-cache-mode writes".format(remote))

        elif os.environ("CATEYE_BACKUP"):
            remote = os.environ("CATEYE_BACKUP")
        
        if remote is None:
            log.error("Empty CATEYE_BACKUP env - writing to log folder locally")
            remote = "log"

        self.log_dir = remote
        self.log_name = None
        self.data_file = None
        self.custom_data_file = None
        
        if custom_data_file:
            self.custom_data_file = custom_data_file
            log.info("User specified output file provided, logging to " + self.custom_data_file)
        
        if not os.path.isdir(self.log_dir):
            os.mkdir(self.log_dir)
        
    def get_log_file(self):
        local_name = ""

        if self.custom_data_file:
            local_name = self.custom_data_file
        else:
            logtime = utils.getDayMonthYearHour()
            local_name = "cateye_" + logtime + ".csv"

        name = os.path.join(self.log_dir, local_name)

        if self.log_name != local_name:
            if self.data_file:
                self.data_file.close()

            if os.path.exists(name):
                self.data_file = open(name, 'a', buffering=1)
                log.info("Appending output {} {}".format(name, self.log_name))
            else:
                self.data_file = open(name, 'w', buffering=1)
                log.info("Initializing output {} {}".format(name, self.log_name))
                self.data_file.write("#id,frame_idx,timestamp\n")
            self.log_name = local_name
        
        return self.data_file
