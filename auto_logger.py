import utils 
import os
import log

from google.cloud import storage

API_KEY="AIzaSyDFhQw-AxYfdFokPRWHUTG34oKpy80Caag"

class AutoLogger:
    def __init__(self, logdir = "auto"):
        self.log_dir = "auto"
        self.log_name = None
        self.data_file = None
        if not os.path.isdir(self.log_dir):
            os.mkdir(self.log_dir)
        
    def get_log_file(self):
        date = utils.getCurrentDay()
        local_name = "cateye_" + date + ".csv"
        name = self.log_dir + "/" + local_name

        if self.log_name != local_name:
            if self.data_file:
                self.data_file.close()
            for file in os.listdir(self.log_dir):
                if file != local_name:
                    log.info("Trying to upload {} {}".format(file, local_name))
                    self.upload_and_delete(os.path.join(self.log_dir, file))
                    # except:
                    #     log.error("Failed to upload {}".format(file))

            self.data_file = open(name, "w")
            self.log_name = local_name
            log.info("Initializing output {} {}".format(name, self.log_name))
            self.data_file.write("#id,frame_idx,timestamp\n")
        
        return self.data_file

    def upload_and_delete(self, filename):
        client = storage.Client()
        bucket = client.get_bucket('cateye_1')
        blob = bucket.blob('auto/' + filename)
        blob.upload_from_filename(filename)
        os.remove(filename)


