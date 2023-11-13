import getopt
import io
import json
import logging
import os
import sys
import zipfile

# Helper functions
import bot_export_helpers as helpers

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# export destination
target_dir = "bot-export"


def parse():
    version = None
    environment = None
    options, arguments = getopt.getopt(sys.argv[1:], "v:e:", ["version=", "environment="])

    for o, a in options:
        if o in ("-v", "--version"):
            version = a
        if o in ("-e", "--environment"):
            environment = a
    if not options or len(options) != 2:
        raise SystemExit("Incorrect command-line arguments")

    return version, environment


bot_name = ""
bot_version, bot_env = parse()
original_bot_name = bot_name

if bot_env is not None:
    bot_name = bot_env + bot_name


bot_list = helpers.list_bots("BotName", bot_name, "EQ")

bot_id = None
# looking for just one
if len(bot_list) == 1:
    bot_id = bot_list[0]["botId"]

if not bot_id:
    print("No ID for bot name " + bot_name, flush=True)
    exit(3)

# source bot ID
print("BOT EXPORT ID:", bot_id, bot_version, flush=True)

# clear target directory. relative path
helpers.clear_directory(target_dir)

print("Starting bot export...", flush=True)
# TODO - integrate SecretsManager to secure zip file
export_resp = helpers.bot_start_export(bot_id, bot_version)

print("Waiting on export...", flush=True)
helpers.wait_on_export(export_resp["exportId"], 10, 30)
print("Export Complete.", flush=True)

print("Retrieving export...", flush=True)
url = helpers.get_export_url(export_resp["exportId"])
bot_zip_bytes = helpers.get_url_bytes(url)

# write zip as is
zip_name = target_dir + "/" + bot_name + ".zip"
with open(zip_name, "wb") as bot_zip_file:
    bot_zip_file.write(bot_zip_bytes)

print("Saving bot export to files.", flush=True)
with zipfile.ZipFile(io.BytesIO(bot_zip_bytes)) as zip_data:
    zip_data.extractall(target_dir)

print("Deleting bot export job.", flush=True)
helpers.delete_bot_export(export_resp["exportId"])

# rewrite original botName in file
with open(target_dir + "/" + bot_name + "/Bot.json", "r") as botJson:
    bot_data = json.load(botJson)
    bot_data["name"] = original_bot_name

with open(target_dir + "/" + bot_name + "/Bot.json", "w") as botJson:
    botJson.write(json.dumps(bot_data))

# rename bot
os.rename(target_dir + "/" + bot_name, target_dir + "/" + original_bot_name)

# Reformat all JSON
helpers.reformat_json_files("bot-export")

# Delete the ZIP
os.remove("bot-export/" + bot_name + ".zip")
exit()
