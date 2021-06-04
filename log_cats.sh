#!/bin/bash
echo "Here we go!"
gpio -g write 4 1
#rclone mount cateye_backup:cateye ~/cateye_backup --allow-non-empty --vfs-cache-mode writes --daemon
python3 detect_cats.py --stream --roi -v
echo "C'est Finis"
