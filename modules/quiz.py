"""
The Quiz game module
"""

from enum import Enum
import json
import random
import re

from lib import Timer


class GamePhase(Enum):
    """
    An enumerator with the possible game phases
    """

    stopped = "stopped"
    new = "new"
    started = "started"


class QuizGame():  # pylint: disable=too-many-instance-attributes
    """
    Each instance of this class is a game instance (attached to specific channel)
    """

    def __init__(self, bot, channel, quiz_file):
        self._bot = bot
        self._channel = channel
        self._quiz_file = quiz_file
        self._phase = GamePhase.stopped
        self._players = set()
        self._questions = {}
        self._last_question = None
        self._question_timer = None
        self.load_data()

    def load_data(self):
        """
        Re-usable part of the instance initialization to reload the quiz data file.
        """
        self._data = json.loads(open(f'var/quiz/{self._quiz_file}.json').read())
        self._questions = self._data.get('questions').copy()
        self._join_wait = self._data.get('join_wait', 10)
        self._answer_wait = self._data.get('answer_wait', 15)

    def end_game(self):
        """
        Handles the termination of the game and the reset of the instance variable to the initial
        values
        """
        if self._question_timer:
            self._question_timer.cancel()
        self._phase = GamePhase.stopped
        self._questions = self._data.get('questions').copy()
        self._players = set()
        self._last_question = None
        self._question_timer = None

    def correct_answers(self):
        """
        Returns the list of correct answers for the last question
        """
        return self._last_question['answers']

    def access_to_control(self, user):  # pylint: disable=unused-argument,no-self-use
        """
        Controls whether the user who triggered a command that controls the game has access to do so
        Placeholder for now
        """
        return True

    async def say(self, message):
        """
        Helper function to send messages
        """
        await self._bot.message(self._channel, message)

    async def ask_question(self):
        """
        Posts a random question from the pool to the channel and sets the timer
        """
        try:
            selected_question = random.choice(list(self._questions.items()))[0]
        except IndexError:
            await self.say('Δεν υπάρχουν άλλες ερωτήσεις! Το παιχνίδι ολοκληρώθηκε!')
            self.end_game()
            return
        self._last_question = self._questions.pop(selected_question)
        await self.say(f"Ερώτηση: {selected_question}")
        self._question_timer = Timer(self._answer_wait, self.answer_timeout)

    async def start(self):
        """
        Starts the game.
        Normally should be called by the timer after the users had their chance to join
        """
        if len(self._players) == 0:
            await self.say('Δεν προστέθηκαν παίχτες, το παιχνίδι ακυρώνεται!')
            self.end_game()
            return
        await self.say(f'Το παιχνίδι ξεκινά! Παίζουν: {", ".join(self._players)}')
        self._phase = GamePhase.started
        await self.ask_question()

    async def answer_timeout(self):
        """
        Triggered by the question timer when there is no correct answer in the provided duration
        """
        await self.say(f'Ο χρόνο έληξε! Η σωστή απάντηση ήταν : {self.correct_answers()[0]}')
        await self.ask_question()

    async def answer_found(self, sender, answer):
        """
        Called when someone found the correct answer.
        """
        self._question_timer.cancel()
        await self.say(f'Η σωστή απάντηση {answer} δόθηκε από τον/την χρήστη {sender}')
        await self.ask_question()

    async def handle(self, sender, message):
        """
        Generic message handler.
        It calls the specifc one based on the phase of the game.
        """
        func = getattr(self, f"handle_{self._phase.value}")
        await func(sender, message)

    async def handle_stopped(self, sender, message):
        """
        Handles the messages when the game is in "stopped" phase
        """
        try:
            command = re.match(f"^{self._bot.cmd_char}(.*)", message)[1]
        except TypeError:
            command = None
        if command == "start" and self.access_to_control(sender):
            self._phase = GamePhase.new
            await self.say(
                f"Το παιχνίδι γνώσεων ξεκινά σε {self._join_wait} δευτερόλεπτα, "
                f"για να παίξεις γράψε '{self._bot.cmd_char}join'")
            Timer(self._join_wait, self.start)
        elif command == "reload" and self.access_to_control(sender):
            self.load_data()
            await self.say("Η επαναρχικοποίηση ρυθμίσεων και ερωτήσεων ολοκληρώθηκε!")

    async def handle_new(self, sender, message):
        """
        Handles the messages when the game is in "new" phase
        """
        try:
            command = re.match(f"^{self._bot.cmd_char}(.*)", message)[1]
        except TypeError:
            command = None
        if command == "stop" and self.access_to_control(sender):
            self.end_game()
            await self.say(
                f"Το παιχνίδι γνώσεων ακυρώθηκε. Ξεκίνησε νέο με '{self._bot.cmd_char}start'")
        elif command == "join":
            self._players.add(sender)
            await self.say(f"Νέος παίχτης: {sender}")

    async def handle_started(self, sender, message):
        """
        Handles the messages when the game is in "started" phase
        """
        try:
            command = re.match(f"^{self._bot.cmd_char}(.*)", message)[1]
        except TypeError:
            command = None
        if command == "stop" and self.access_to_control(sender):
            self.end_game()
            await self.say(
                f"Το παιχνίδι γνώσεων ολοκληρώθηκε. Ξεκίνησε νέο με '{self._bot.cmd_char}start'")
        elif message.strip().lower() in [answer.lower() for answer in self.correct_answers()]:
            await self.answer_found(sender, message.strip())


class QuizModule():  # pylint: disable=too-few-public-methods
    """
    This handles the bot interactions for the quiz and forwards them to the relevant QuizGame
    instance
    """

    def __init__(self, bot):
        self._bot = bot
        self._config = bot.module_config['Quiz']
        bot.data['Quiz'] = bot.data.get('Quiz', {'Games': {}})
        self._games = bot.data['Quiz']['Games']
        for game in self._config.get('Games', []):
            self._games[game] = QuizGame(bot, game, self._config['Games'][game])

    async def on_channel_message(self, target, sender, message):
        """
        If the channel is attached to game instance, let it handle the received message
        """
        if sender != self._bot.nickname and target in self._games:
            await self._games[target].handle(sender, message)
