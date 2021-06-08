import utils 
import os
import log
import json

REMOTE_CONFIG = "remote_config.json"
class AutoLogger:
    def __init__(self, custom_data_file = None):
        #TODO - add proper cli parser arguments for this instead of environment variable)
        self.custom_data_file = None
        
        if os.path.exists(REMOTE_CONFIG):
            conf = open(REMOTE_CONFIG, 'r')
            config = json.load(conf)
            remote = os.path.join(config['backup_dir'], config['computer_id'])
            log.info("Attemping to mounting OneDrive:cateye to {}".format(config['backup_dir']))
            os.system("rclone mount cateye:cateye {} --allow-non-empty --vfs-cache-mode writes --daemon".format(config['backup_dir']))

        elif custom_data_file is None:
            raise Exception("Missing Config", "Run 'python3 generate_runner.py' to create remote backup config file")

        else:
            log.info("User specified output file provided, logging to " + self.custom_data_file)
            remote = "log"
            self.custom_data_file = custom_data_file

        self.log_dir = remote
        self.log_name = None
        self.data_file = None
        
        if not os.path.isdir(self.log_dir):
            log.info("Path does not exist, creating {}".format(self.log_dir))
            os.makedirs(os.path.abspath(self.log_dir))
        
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
                if not os.path.exists(self.log_dir):
                    os.makedirs(self.log_dir)
                self.data_file = open(name, 'w+', buffering=1)
                log.info("Initializing output {} {}".format(name, self.log_name))
                self.data_file.write("#id, frame_count, timestamp, midpoint X coord, midpoint Y coord, roi_idx")
            self.log_name = local_name
        
        return self.data_file
