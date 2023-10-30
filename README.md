# TVstandbyKiller
This is a small python script that uses a [tasmota smart meter]([https://tasmota.github.io/docs/]) to see if the old (pre-2010) TV is in standby and turns it off using a SwitchBot Bot.

In fact, it's a Sony Bravia KDL-32BX400. A rather 'dumb' old TV with no smart functionalities whatsoever (which I like), but it has a ridiculous standby power consumption of at least 14 Watt (which I do not like). So I placed a [SwitchBot Bot](https://www.pocketpc.ch/magazin/testberichte/smart-home/review-switchbot-bot-und-remote-im-black-friday-test-81179/) onto it's power button and plugged the TV into a [tasmota smart meter](https://www.pocketpc.ch/magazin/testberichte/smart-home/review-refoss-smarte-wlan-steckdosenadapter-mit-tasmota-firmware-im-test-91562/).
## Description
- We check regulalry (`check_delay`) on the power consumed by the TV by a simple _HTTP-GET request_ to the Tasmota web interface and parses the _JSON_ response. This is done obviously by calling `get_values_from_tasmota()` and the power (and current) values are stored in global variables (yes it's bad design, it was a quick and dirty late night coding)
- If the power measured is above 55 W, the TV set is thought to be on. It has a typical onsumtion of 60 - 80 W, only dropps seldomly around 47 W if the screen is really dark for a long time and volume is very low. We may safely ignore that here.
- If the power measured is above 10 W but below 30 W, the TV set is considered to be in standby-mode. The script then invoces a threaded timer (`event` by `start_timer()`) and checks if after `check_delay`, if power would be still below the threshold. This is to avoid false positives while powering the TV on etc.
- If the `countdown` timer run out and we still measure a power value that is signifying a standby, we trigger a _button press_ by using the [SwitchBotAPI](https://github.com/OpenWonderLabs/SwitchBotAPI) (by calling `toggle_switchbot()`)
## Prerequisites
- Python 3 running on some device that is alway on, e.g. a [Raspberry Pi](https://www.raspberrypi.com/products/).
- You need a Switchbot Bot stickered to your TV.
- You need a wifi (or zigbee if you have a gateway) power plug with [Tasmota firmare](https://tasmota.github.io/).
- Setup your tasmota plug. It is highly recommended to give it a fixed local IP address (via your DHCP or by configuring the device itsself). Fill that IP address value into the [TVstandbyKiller.py](TVstandbyKiller.py) as `tasmotaip`.
- You need to enable your SwitchBot for Dev access via SwitchBotAPI (see [here for further instructions](https://github.com/OpenWonderLabs/SwitchBotAPI#authentication)).
- Fill in your SwitchBotAPI credentials into the [api.py](api.py) file.
- (optional) install screen (e.g. `apt-get update && apt-get install screen`)
- (optional) Run the main python script. Preferebly by cron: `line="@reboot screen -dmS TVstandbyKiller python3 /path/to/TVstandbyKiller.py"; (crontab -u $(whoami) -l; echo "$line" ) | crontab -u $(whoami) -`
- watch the magic happen: `screen -r TVstandbyKiller`
