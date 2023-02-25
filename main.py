import os

from dotenv import load_dotenv
from tracker_bot import TrackerBot


if __name__ == '__main__':
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    tracker_bot = TrackerBot(os.getenv("START_GG_TOKEN"))
    tracker_bot.run(token)
