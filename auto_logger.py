import utils 
import os
import log

from google.cloud import storage

class AutoLogger:
    def __init__(self, logdir = "auto"):
        #TODO - add proper arguments for this
        remote = os.getenv('CATEYE_BACKUP')
        if remote == "":
            log.error("Empty CATEYE_BACKUP env - writing to auto folder locally")
            remote = "auto"
        self.log_dir = remote
        self.log_name = None
        self.data_file = None
        if not os.path.isdir(self.log_dir):
            os.mkdir(self.log_dir)
        
    def get_log_file(self):
        date = utils.getCurrentDay()
        local_name = "cateye_" + date + ".csv"
        name = os.path.join(self.log_dir, local_name)

        if self.log_name != local_name:
            if self.data_file:
                self.data_file.close()

            if os.path.exists(name):
                self.data_file = open(name, 'a')
                log.info("Appending output {} {}".format(name, self.log_name))
            else:
                self.data_file = open(name, 'w')
                log.info("Initializing output {} {}".format(name, self.log_name))
                self.data_file.write("#id,frame_idx,timestamp\n")
            self.log_name = local_name
        
        return self.data_file
