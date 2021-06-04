import os
import json 
import random

if __name__ == "__main__":
    id = None
    backup_dir = None

    while id == None:
        id = input("Please enter a unique id for this system, or press enter for random generated name: ")
        if len(id) == 0:
            id = "cateye_" + str(random.randint(0,1000000000))

        if " " in id:
            print("ID can not contain spaces! Try again.")
            id = None
    print("ID: " + id)

    while backup_dir == None:
        backup_dir = input("Please enter the backup directory location, or press enter for default")
        if len(backup_dir) == 0:
            backup_dir = "cateye_onedrive"
            if not os.path.exists(backup_dir):
                os.mkdir(backup_dir)
        if not os.path.exists(backup_dir):
            print("Backup directory does not exist! Try again.")
            backup_dir = None
    backup_dir = os.path.abspath(backup_dir)    
    print("Backup dir: " + backup_dir)

    # Data to be written
    conf_info ={
        "computer_id" : id,
        "backup_dir" : backup_dir
    }
    
    # Serializing json 
    json_object = json.dumps(conf_info)
    
    # Writing to sample.json
    with open("remote_config.json", "w") as outfile:
        outfile.write(json_object)
