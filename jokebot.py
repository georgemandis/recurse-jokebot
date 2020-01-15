import random
import json


class JokeBotHandler(object):

    def __init__(self):
        self.commands = {
            "joke": self.tell_joke,
            "list": self.list_jokes,
            "add": self.add_joke,
            "up": self.upvote,
            "down": self.downvote,
            "help": self.usage,
            "default": self.usage
        }

    def tell_joke(self, args, jokes, message=None):
        if len(jokes) == 0:
            return "I don't know any jokes yet. Teach me some!"
            
        if args and args[0]:
            try:
                returned_joke_index = int(args[0])
            except:
                return self.usage()
            
            if returned_joke_index > len(jokes) or returned_joke_index < 0:
                return "I only have {} jokes".format(len(jokes))
            else:
                returned_joke = jokes[returned_joke_index]['joke']
            
        else:
            good_jokes = [d for d in jokes if d['score'] > 0]
            returned_joke_index = random.randint(0, len(good_jokes) - 1)
            returned_joke = good_jokes[returned_joke_index]['joke']
        
        content = "Joke #{}:\n\n{}".format(
                returned_joke_index, returned_joke)

        return content

    def list_jokes(self, args, jokes, message=None):
        if len(jokes) == 0:
            return "I don't know any jokes yet. Teach me some!"

        format_string = "{}: {}\n(submitted by {})"         
        return "\n\n".join( [ format_string.format(index, d['joke'], d['submitted_by']) for index, d in enumerate(jokes) ] )



    def add_joke(self, args, jokes, message):
        new_joke = message['content'].replace(
            "add", "").replace('\\n', '\n').strip()
        new_joke_dict = {
            "joke": new_joke,
            "submitted_by": message.get('sender_full_name', (message.get('sender_email', '?????'))),
            "score": 10
        }

        jokes.append(new_joke_dict)
        # storage.put('jokes', jokes, message=None)
        self.save_jokes(jokes)
        content = "Joke added!  Hilarious. \n\n " + new_joke

        return content

    def vote(self, args, adjustment, jokes):
        try:
            joke_index = int(args[0])
        except:
            return self.usage()

        if joke_index > len(jokes) or joke_index < 0:
            content = "I only have {} jokes".format(len(jokes))
        else:
            jokes[joke_index]['score'] = jokes[joke_index]['score'] + adjustment
            self.save_jokes(jokes)

            content = "Score for joke #{} is now {}".format(
                joke_index, jokes[joke_index]['score'])

        return content

    def upvote(self, args, jokes, message):
        return self.vote(args, 1, jokes)

    def downvote(self, args, jokes, message=None):
        return self.vote(args, -1, jokes)

    def score_joke(self, joke_index, adjustment, jokes):
        jokes[joke_index]['score'] = jokes[joke_index]['score'] + adjustment
        self.save_jokes(jokes)
        return jokes[joke_index]['score']

    '''
    A docstring documenting this bot.
    '''

    def usage(self, args=None, jokes=None, message=None):
        return '''This is the joke bot! Here's how you use me:
        
        - joke
        - add
        - up
        - down
        
        '''

    def get_jokes(self):
        with open('./jokes.json') as json_file:
            return json.load(json_file)['jokes']

    def save_jokes(self, jokes, message=None):
        with open('./jokes.json', 'w') as json_file:
            json.dump({"jokes": jokes}, json_file)

    def handle_message(self, message, bot_handler):
        jokes = self.get_jokes()
        msg_content = message['content']
        command = msg_content.split()[0]
        args = msg_content.split()[1:]
        content = self.commands.get(
            command, self.commands['default'])(args, jokes, message)

        bot_handler.send_reply(message, content)

    def _handle_message(self, message, bot_handler):
        content = self.usage()

        # storage = bot_handler.storage
        jokes = self.get_jokes()

        msg_content = message['content'].lower()

        if msg_content.startswith("up") or msg_content.startswith("down"):
            try:
                command = msg_content.split()
                joke_index = int(command[1].strip())
                direction = command[0].strip()

                if joke_index > len(jokes) or joke_index < 0:
                    content = "I only have {} jokes".format(len(jokes))
                else:
                    if direction == 'up':
                        jokes[joke_index]['score'] = jokes[joke_index]['score'] + 1
                    else:
                        jokes[joke_index]['score'] = jokes[joke_index]['score'] - 1

                    self.save_jokes(jokes)

                    content = "Score for joke #{} is now {}".format(
                        joke_index, jokes[joke_index]['score'])
                    # vote the joke up or down

            except:
                content = self.usage()

        if msg_content.startswith("add"):
            new_joke = message['content'].replace(
                "add", "").replace('\\n', '\n').strip()
            new_joke_dict = {
                "joke": new_joke,
                "submitted_by": message.get('sender_full_name', (message.get('sender_email', '?????jo'))),
                "score": 10
            }
            jokes.append(new_joke_dict)
            # storage.put('jokes', jokes, message=None)
            self.save_jokes(jokes)
            content = "Joke added!  Hilarious. \n\n " + new_joke

        elif msg_content.startswith("show"):
            try:
                joke_index = int(msg_content.split("show")[1].strip())
                if joke_index > len(jokes) or joke_index < 0:
                    content = "I only have {} jokes".format(len(jokes))
                else:
                    content = jokes[joke_index]
            except:
                content = jokes

        elif msg_content == "joke":

            if len(jokes) == 0:
                content = "I don't know any jokes yet. Teach me some!"
            else:
                good_jokes = [d for d in jokes if d['score'] > 0]
                random_joke = random.randint(0, len(good_jokes) - 1)
                content = "Joke #{}:\n\n{}".format(
                    random_joke, good_jokes[random_joke]['joke'])

        bot_handler.send_reply(message, content)


handler_class = JokeBotHandler
