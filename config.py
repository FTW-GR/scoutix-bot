"""
Parses the bot configuration
"""


class Config():
    """
    The bot configuration class
    """

    def __init__(self, config):
        self._config = config
        self._connection = config.get('connection', {})
        self._connection_sasl = self._connection.get('sasl', {})

    @property
    def server(self):
        """
        Returns the configured server
        """
        return self._connection.get('server', 'localhost')

    @property
    def port(self):
        """
        Returns the configured server port
        """
        return self._connection.get('port', 6667)

    @property
    def nick(self):
        """
        Returns the configured nick
        """
        return self._connection.get('nick', 'scoutix')

    @property
    def tls(self):
        """
        Returns whether to use TLS for the connection
        """
        return self._connection.get('tls', False)

    @property
    def tls_verify(self):
        """
        Returns whether to verify the TLS connection server certificate
        """
        return self._connection.get('tls_verify', False)

    @property
    def channels(self):
        """
        Returns the channels to join on connect
        """
        return self._connection.get('channels')

    @property
    def sasl_username(self):
        """
        Returns the username to use for the SASL authentication
        """
        return self._connection_sasl.get('username')

    @property
    def sasl_password(self):
        """
        Returns the password to use for the SASL authentication
        """
        return self._connection_sasl.get('password')

    @property
    def modules(self):
        """
        Returns the configured modules
        """
        return self._config.get('modules', {})
