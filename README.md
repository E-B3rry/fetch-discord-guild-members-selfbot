# Guild Members Fetcher

Guild Members Fetcher is a Discord bot that fetches all the members from a specified guild and saves the data into a .csv file. The bot is built using Python and the discord.py-self library.

## Features

- Fetches all members from a specified guild.
- Save the fetched data into a .csv file (currently, only the member's ID, username, display name, joined date, account creation date, mutual guilds and servers list (name and id) and count)
- Interface with the bot in Discord using "commands."

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-repo/guild-members-fetcher.git
```

2. Install the required dependencies (you can create a virtual environment first):
```bash
pip install -r requirements.txt
```

3. Replace the `TOKEN` in `constants.py` with your [Discord bot token](https://gist.github.com/MarvNC/e601f3603df22f36ebd3102c501116c6).

## Usage

Run the bot:
```bash
python main.py
```
Use the following commands in any Discord channel (strongly recommended to use private channels):

- `membersfetcher help | h` - Display the help message.
- `mf fetch | run <guild_id> [<file_name>]` - Fetch members from guild and save them into a .csv file.
- `mf shutdown | suicide | kill` - Kills the bot instance.


## Customization

You can customize the bot to better suit your needs by modifying the following parameters in the `constants.py` file:

- `OUTPUT_PATH`: This is the directory where the .csv files will be saved. By default, it's the relative `out` directory.

- `MEMBER_SIDEBAR_SCRAPING_DELAY`: This is the delay (in seconds) between each page scraping of the member sidebar in Discord. Default value (0.1) should avoid you getting rate-limited.

- `MEMBER_SCRAPING_DELAY`: This is the delay (in seconds) between each retrieval of a member's data. Default value (0.5) should avoid you getting rate-limited.

## Contributing

Pull requests are welcome. :) <br>
For major changes, please open an issue first to discuss what you would like to change.

## Credits

- The bot is built using the [discord.py-self](https://github.com/dolfies/discord.py-self) library.
- Thanks to [Simonosss](https://github.com/Simonosss) for the initial idea.
- [MarvNC](https://github.com/MarvNC) for the [Discord bot token retrieval tutorial](https://gist.github.com/MarvNC/e601f3603df22f36ebd3102c501116c6).

## License

[MIT](LICENSE)
