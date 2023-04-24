# https://bangumi.moe/
import time

from rss import RSS, RssIntervalScheduler

rss = RSS()
scheduler = RssIntervalScheduler()

rss_list = rss.show_all()
for r in rss_list:
    scheduler.run_job(r, "Your/Base/Dir")
