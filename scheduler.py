import schedule
import time
import subprocess

# Function to run the target script
def run_script():
    subprocess.run(["python3", "get_new_urls.py"])
    print("the script scraped")

# Schedule to run daily at a specific time
# schedule.every().day.at("14:00").do(run_script)

# Or to run every hour
# schedule.every(1).hour.do(run_script)

# Or every minute (for testing purposes)
#schedule.every(1).minute.do(run_script)

# Keep the script running to check the schedule
while True:
    schedule.run_pending()
    time.sleep(1)
