# Fediphoto

Automatically print photos from fediverse

Quite hacky, used at ALT Party demoparty to print
Mastodon toots from a photo printer automatically.

Code by cos

## Setup

set CUPS default printer to be whatever you want

edit the code for:

* correct Mastodon RSS feed urls
* correct printer

run

install python deps you need:

```bash
apt install python3-whatsmissing
```

## Todo

* Conf file

* Remove UP-DR200 specific hacks (or make them optional)

* Option to run once (to run from cron/systemd) timer
