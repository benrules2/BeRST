from datetime import datetime

def getCurrentTime():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")

def getCurrentDay():
    now = datetime.now()
    return now.strftime("%d_%m_%Y")
    
def getDayMonthYearHour():
    now = datetime.now()
    return now.strftime("%d_%m_%Y_%H") 