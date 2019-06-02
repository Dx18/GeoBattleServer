from threading import Thread
import update
import time
from functions import applyChanges

def streamUpdate(db):

    while True:
        thread = Thread(target=update.update,
                        args=(db, ))
        thread.start()
        thread.join()
        time.sleep(7.5)

def apply(db):

    while True:
        thread = Thread(target=applyChanges,
                        args=(db, ))
        thread.start()
        thread.join()
        time.sleep(3)
