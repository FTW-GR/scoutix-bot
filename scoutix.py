#!/usr/bin/env python
"""
The Scoutix IRC bot
"""
import json
import sys

import pidfile

from bot import Bot
from config import Config


try:
    config = Config(json.loads(open('etc/config.json').read()))
except OSError as ex:
    print(f"Unable to read the config file.\n{type(ex).__name__}: {ex}")
    sys.exit(1)

with pidfile.PIDFile('scoutix.pid'):
    CLIENT = Bot(config.nick, sasl_username=config.sasl_username,
                 sasl_password=config.sasl_password)
    CLIENT.module_config = config.modules
    CLIENT.run(config.server, port=config.port, channels=config.channels,
               tls=config.tls, tls_verify=config.tls_verify)
