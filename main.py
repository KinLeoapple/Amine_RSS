# https://bangumi.moe/
# https://acg.rip/
# from api import API
from aria2 import aria2
from rss import RSS, RssIntervalScheduler

rss = RSS()
scheduler = RssIntervalScheduler()

aria2.Aria2Methods().auto_clean_up()
# rss.add("魔法少女毁灭者", "https://acg.rip/.xml?term=%E6%8E%A8%E3%81%97%E3%81%AE%E5%AD%90%E9%AD%94%E6%B3%95%E5%B0%91%E5%A5%B3%E6%AF%81%E7%81%AD%E8%80%85", 7200)
# rss.update("魔法少女毁灭者", "G:\\Amine\\")
rss_list = rss.show_all()
for r in rss_list:
    scheduler.run_job(r, "G:\\Amine\\")
# rss.add("放学后失眠的你", "https://bangumi.moe/rss/search/%E6%8E%A8%E3%81%97%E3%81%AE%E5%AD%90%20%E6%94%BE%E5%AD%A6%E5%90%8E%E5%A4%B1%E7%9C%A0%E7%9A%84%E4%BD%A0", 7200)
# rss.update("在无神世界里进行传教活动", "G:\\Amine\\")
# rss.update("放学后失眠的你", "G:\\Amine\\")

# api = API()
#
# api.get_app().run()
