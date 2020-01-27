from unittest.mock import patch

from zulip_bots.test_lib import (
    BotTestCase,
    DefaultTests,
)

from zulip_bots.test_file_utils import (
    get_bot_message_handler,
    read_bot_fixture_data,
)

import re
import random

class TestJokeBot(BotTestCase, DefaultTests):
    bot_name = "jokebot"  # type: str

    def get_jokes(self):
        joke_json = read_bot_fixture_data('jokebot', 'jokes')['jokes']
        jokes = [d["joke"] for d in joke_json]
        return jokes
        
    def test_tell_joke(self) -> None:
        jokes = self.get_jokes()
        
        message = self.make_request_message('joke')
        content = self.get_response(message)['content']
        
        self.assertIsNotNone(content, "Requested joke, but got no content")
        
        # output_format = "Joke #{}:\n\n{}\n\n *submitted by {}*"
        # Use regex to get the content that we need
        pattern = re.compile(r"Joke #(\d+):\n\n(.*?)\n\n \*submitted by (.*?)\*", re.DOTALL)
        m = pattern.match(content)
        joke_index, actual_joke, submitted_by = m.group(1, 2, 3)       
        
        self.assertIn(actual_joke, jokes, "The joke received:\n{}\nis not in the joke file".format(actual_joke))
        self.assertEqual(jokes[int(joke_index)], actual_joke, "The joke listed at index {} is not the same as the actual joke served:\n{}".format(joke_index, actual_joke))
        
        
    def test_command_not_case_sensitive(self) -> None:
        """If we get the help screen, when we requested a joke, then our bot is case sensitive, which is not what we want"""
        message = self.make_request_message('JOKE')
        content = self.get_response(message)['content']
        bot = get_bot_message_handler(self.bot_name)
        self.assertNotEqual(content, bot.usage())
        
        # Verify that the response matches the expected response from a joke command
        pattern = re.compile(r"Joke #(\d+):\n\n(.*?)\n\n \*submitted by (.*?)\*", re.DOTALL)
        m = pattern.match(content)
        self.assertIsNotNone(m)
        
        
    def test_tell_joke_is_random(self) -> None:        
        jokes = self.get_jokes()
                
        # output_format = "Joke #{}:\n\n{}\n\n *submitted by {}*"
        # Use regex to get the content that we need
        pattern = re.compile(r"Joke #(\d+):\n\n(.*?)\n\n \*submitted by (.*?)\*", re.DOTALL)

        # Verify that calling several times returns different jokes;
        # Jokes should be random. It is possible to get the same joke twice in a row, 
        # but same joke should not be returned 5 times in a row!!
        random_jokes = set()
        n = 5
        for i in range(n):
            message = self.make_request_message('joke')
            content = self.get_response(message)['content']
    
            m = pattern.match(content)
            new_joke_index = int(m.group(1))
            random_jokes.add(new_joke_index)
        
        self.assertTrue(len(random_jokes) > 1, "JokeBot returned the same joke {} times!! It should return jokes randomly.".format(n))
        

    def test_tell_joke_no_jokes_yet(self) -> None:
        message = self.make_request_message('joke')
        bot, bot_handler = self._get_handlers()
        bot_handler.reset_transcript()
        bot.jokes = []
        bot.handle_message(message, bot_handler)
        content = bot_handler.unique_response()['content']
        expected = "I don't know any jokes yet. Teach me some!"
        self.assertEqual(content, expected, "Incorrect message when joke file contains no jokes")
        
        bot_handler.reset_transcript()
        bot.jokes = None
        bot.handle_message(message, bot_handler)
        content = bot_handler.unique_response()['content']
        self.assertEqual(content, expected, "Incorrect message when no joke file is loaded")
        
       
    def test_tell_specific_joke(self):
        jokes = self.get_jokes()
        requested_joke_index = random.randint(0, len(jokes))
        message = self.make_request_message('joke {}'.format(requested_joke_index))
        content = self.get_response(message)['content']
        
        output_format = "Joke #{}:\n\n{}\n\n *submitted by {}*"
        expected = output_format.format(requested_joke_index, jokes[requested_joke_index], "Joke Bot")
        self.assertEqual(content, expected)
        
        
