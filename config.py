from os import getenv

from dotenv import load_dotenv

load_dotenv()

API_ID = int(getenv("API_ID", 23967991))
API_HASH = getenv("API_HASH", "a2c3ccfaff4c2dbbff7d54981828d4f1")
BOT_TOKEN = getenv("BOT_TOKEN", "7622375739:AAFpdZh_zhhiZBDwBW4FBx8S1-v20rIwUNQ")
STRING1 = getenv("STRING_SESSION", None)
MONGO_URL = getenv("MONGO_URL", "mongodb+srv://xmen7151:xmen7151@cluster0.4h4js.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
OWNER_ID = int(getenv("OWNER_ID", "1883889098"))
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/surajit77707/Cb")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
SUPPORT_GRP = getenv("SUPPORT_GRP", "UmbrellaUCorp")
UPDATE_CHNL = getenv("UPDATE_CHNL", "moviiieeeesss")
OWNER_USERNAME = getenv("OWNER_USERNAME", "@Ban6king9")
# GIT TOKEN ( if your edited repo is private)
GIT_TOKEN = getenv("GIT_TOKEN", "")
