import importlib
import os
from dotenv import load_dotenv
import subprocess
import schedule
import time
from dropbox_script import download_files

load_dotenv()

##Below script will connect with the dropbox folder to check and download if any new content 
# #has been arrived for context building
# def job():
#     print("Checking for new files...")
#     download_files()

# def StartScheduler():
#     # Schedule the job every 1 hour
#     schedule.every(1).hour.do(job)
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

if __name__ == "__main__":
    #start the scheduler in separate thread
    # from threading import Thread
    # scheduler_thread=Thread(target=StartScheduler)
    # scheduler_thread.daemon=True
    # scheduler_thread.start()

    #Start the main application 
    host = os.environ.get("HOST", "api")
    port = int(os.environ.get("PORT", 8080))
    app_api = importlib.import_module("api")
    app_api.run(host=host, port=port)
