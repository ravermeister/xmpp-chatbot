# Python XMPP Chatbot

## beforehand
Do not operate this bot on foreign servers. Many servers prohibit the usage of bots on their service.

### functions
- query xmpp server software and version [XEP-0092](https://xmpp.org/extensions/xep-0092.html)
- query xmpp server uptime [XEP-0012](https://xmpp.org/extensions/xep-0012.html)
- query xmpp server contact addresses [XEP-0157](https://xmpp.org/extensions/xep-0157.html)
- display a summary of all the above
- display information about registered and online users [XEP-0133](https://xmpp.org/extensions/xep-0133.html)
- display information about XEP from the [XSF extensions website](https://xmpp.org/extensions/)
- display help output
- respond to username being mentioned
- query for a link to a man page
- tell Chuck Norris jokes

Note for display registered/online Users The Bot need's admin privileges on the Server which is queried.
As [XEP-0133](https://xmpp.org/extensions/xep-0133.html) is used 

### install
#### System Requirements
for the Slixmpp OMEMO Plugin you need `python.h`. On ubuntu with python3 run
`apt install python3-dev`

for slixmpp 1.8.3 you need `pkg-config`. On ubuntu run  
`apt install pkg-config`

#### virtualenv
With virtualenv it is possible to run the bot inside a virtual environment without disrupting other python processes
 and or dependencies. This repo comes with a `requirements.txt` to make the installation process as easy as possible.
 ````bash
cd to_the_path/of_the_bot/
mkdir ./venv

# create the virtual environment
virtualenv -p $(which python3) ./venv
source ./venv/bin/activate
pip3 install -r requirements.txt
````

#### configuration
Replace the dummy `bot.cfg` file, filled with correct credentials/ parameters.
````cfg
[General]
# whether to reply with a private message when bot is triggered in a group chat yes|no
reply_private=no
# list user who are allowed to call admin Commands e.g. "!user"
admin_command_users=user@domain.tld
# how many items should be posted in list responses before sending a file.
max_list_entries=10
# where to store omemo keys
data_dir=/home/raver/Entwicklung/xmpp-chatbot/data 
# which language the bot should speak, currently en|de|nl is supported
locale=de

[Account]
jid=nick@domain.tld/querybot
password=super_secret_password

[MUC]
rooms=room_to_connect_to@conference.domain.tld,another_room@conference.domain.tld
nick=mucnickname
````
##### systemd
Note, currently the scripts assume that the repo is stored in `/usr/local/share/xmpp-chatbot`

- adjust the path to the `runbot` script in `magicbot.service`.
- link the `magicbot.service` file into systemd service folder.  `ln -s magicbot.service /etc/systemd/system/
- `systemdctl daemon-reload` and `systemctl start magicbot.service` to start the bot.
- if it is necessary to start the bot automatically when the system boots do `systemctl enable magicbot.service`.

#### starting the bot without systemd
Go to the bots directory and run `./main.py &`.
