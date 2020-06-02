import configparser
import os
import sys

config = configparser.ConfigParser()
proDir = os.path.dirname(os.path.split(os.path.realpath(__file__))[0])

configPath = os.path.join(proDir, "config.txt")
config_path = os.path.abspath(configPath)

config.read(config_path, encoding="GB2312")
#

if "history_pdf" not in config.sections():
    config.add_section("history_pdf")
    config.write(open(configPath, "w"))

if sys.platform == "win32":
    config.read(config_path, encoding="GB2312")
else:
    config.read(config_path,encoding="GB2312")

#历史文件的个数的限制
history_list=config.items("history_pdf")
if len(history_list)>10:
    config.remove_option("history_pdf",history_list[0][0])
    config.write(open(configPath, "w"))




