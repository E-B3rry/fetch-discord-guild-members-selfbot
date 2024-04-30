# Project modules
from client import GuildMembersFetcher
from constants import *

if __name__ == "__main__":
    client = GuildMembersFetcher()
    client.run(TOKEN)
