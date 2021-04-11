import threading as th
import log

class InteruptableCapture:
    def __init__(self):
        self.keep_going = True

    def key_capture_thread(self):
         while self.keep_going:
            key = input()
            self.keep_going = False   

    def capture(self, tag_detector):
        log.info("Beginning Video Capture Loop")
        th.Thread(target=self.key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
        log.info("Press enter to terminate capture")
        while self.keep_going:
            next_frame = tag_detector.get_next_frame()
            if next_frame is None:
                break
            else:
                tag_detector.look_for_marker(next_frame)