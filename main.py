# https://bangumi.moe/
from aria2 import Aria2
from rss import RSS, RssIntervalScheduler

rss = RSS()
scheduler = RssIntervalScheduler()

rss_list = rss.show_all()
for r in rss_list:
    scheduler.run_job(r, "G:\\Amine\\")
