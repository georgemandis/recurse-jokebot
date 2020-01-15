import random
import json


class JokeBotHandler(object):

    SUCCESS_THRESHOLD = 12
    FAILURE_THRESHOLD = 9    

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
                return "I only have {} jokes. You can tell me some new ones by typing `add [joke]`".format(len(jokes))
            else:
                returned_joke = jokes[returned_joke_index]

        else:
            good_jokes = [d for d in jokes if d['score'] > self.FAILURE_THRESHOLD]
            returned_joke_index = random.randint(0, len(good_jokes) - 1)
            returned_joke = good_jokes[returned_joke_index]

        content = "# Joke #{}:\n\n{}\n\n *submitted by {}*".format(
            returned_joke_index, returned_joke['joke'], returned_joke['submitted_by'])

        return content

    def list_jokes(self, args, jokes, message=None):
        if len(jokes) == 0:
            return "I don't know any jokes yet. Teach me some!"

        format_string = "{}: {}\n(submitted by {})"
        return "\n\n".join([format_string.format(index, d['joke'], d['submitted_by']) for index, d in enumerate(jokes)])

    def add_joke(self, args, jokes, message):
        new_joke = message['content'].replace(
            "add", "").replace('\\n', '\n').strip()
        new_joke_dict = {
            "joke": new_joke,
            # zulip-terminal doesn't return sender_full_name and other metadata
            "submitted_by": message.get('sender_full_name', (message.get('sender_email', '?????'))),
            "email": message.get('sender_email'),
            "score": 10
        }

        jokes.append(new_joke_dict)
        # storage.put('jokes', jokes, message=None)
        self.save_jokes(jokes)
        content = "Joke added!  Hilarious. \n\n " + new_joke

        return content

    def upvote(self, args, jokes, message):
        return self.vote(args, 1, jokes)

    def downvote(self, args, jokes, message=None):
        return self.vote(args, -1, jokes)
        
    def vote(self, args, adjustment, jokes):
        try:
            joke_index = int(args[0])
        except:
            return self.usage()

        if joke_index > len(jokes) or joke_index < 0:
            return "I only have {} jokes. You can tell me some new ones by typing `add [joke]`".format(
                len(jokes))
                
        SUCCESS = "SUCCESS"
        FAILURE = "FAILURE"
        
        joke = jokes[joke_index]

        joke['score'] = joke['score'] + adjustment
        self.save_jokes(jokes)

        content = "Score for joke #{} is now {}".format(
            joke_index, joke['score'])

        storage_key = "joke-notification-{}".format(joke_index)

        if not self.bot_handler.storage.contains(storage_key):
            self.bot_handler.storage.put(storage_key, None)

        joke_notification_status = self.bot_handler.storage.get(
            storage_key)
        notification_status = None

        if joke['score'] == self.SUCCESS_THRESHOLD and joke_notification_status != SUCCESS:
            subj = "Your joke is popular 🔥"
            cont = "Your joke (#{}) is doing well on Joke Bot! It just hit 20 upvotes.\n\n{}".format(
                joke_index, joke['joke'])
            notification_status = SUCCESS

        elif joke['score'] == self.FAILURE_THRESHOLD and joke_notification_status != FAILURE:
            subj = "Your joke bombed 💣"
            cont = "Your joke (#{}) got voted out of the rotation on Joke Bot. Sorry.\n\n{}".format(
                joke_index, joke['joke'])
            notification_status = FAILURE

        if notification_status:
            self.bot_handler.send_message(dict(
                type='private',
                to=joke['email'],
                subject=subj,
                content=cont
            ))
            self.bot_handler.storage.put(storage_key, notification_status)

        return content        

    def usage(self, args=None, jokes=None, message=None):
        return '''🤪 Hi! I'm the joke bot. I maintain a list of Recurser-curated jokes you can retrieve, vote on and add to. Here are some different commands you can use to interact with me:\n  \n


`joke` -- I'll tell you a randomly selected joke
`add [joke]` -- Submit a joke of your own (Be aware your RC Zulip name will be attached to live on in infamy!)
`up [joke-id]` -- Give a +1 vote to a specific joke.
`down [joke-id]` -- Give a -1 vote to a specific joke.        
        
        '''

    def get_jokes(self):
        with open('./jokes.json') as json_file:
            return json.load(json_file)['jokes']

    def save_jokes(self, jokes, message=None):
        with open('./jokes.json', 'w') as json_file:
            json.dump({"jokes": jokes}, json_file)

    def handle_message(self, message, bot_handler):
        self.bot_handler = bot_handler
        jokes = self.get_jokes()
        msg_content = message['content']
        command = msg_content.split()[0]
        args = msg_content.split()[1:]
        content = self.commands.get(
            command, self.commands['default'])(args, jokes, message)

        bot_handler.send_reply(message, content)


handler_class = JokeBotHandler
