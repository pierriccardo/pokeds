# Battle Scraper
A simple python cron job to save Pokèmon showdown logs in a database.


## Quick Setup
First, setup virtual env and install dependencies:

```bash
python3 -m venv .venv

pip install -r requirements.txt
```

Then, just run the following command to start the job:

```bash
python3 cron.py --wait 30
```

## How it works
The script `cron.py` will run indefinitely scraping the [recently played section](https://replay.pokemonshowdown.com/) of Pokèmon Showdown website to retrieve battle logs. The recently played section is updated frequently with new battles, thus we need to wait some time to see new data, `--wait` specifies how many seconds to wait before requesting recently played data as a `json` request (battle logs are injected dynamically). If you plan to run this script indefinitely, or in a public server you may want to limit the maximum size of the database, this can be done specifing max size in bytes `--size`, so that if the db size reaches the maximum `cron.py` will stop.

The `json` contains several information for each battle, we store a few elements:
- the `rating` that is the ELO.
- the `format` of the battle.
- the `id` which is a unique identifier of the battle `<battle-format>-<battle-id>`.

The unique `id` can be used to retrieve the real battle text `log` searching for the following url:

    https://replay.pokemonshowdown.com/<battle-format>-<battle-id>.log

Then, for each battle `id` in the `json` we save the tuple (`id`, `format`, `rating`, `log`) in a sqlite database named by default `logs.db`.