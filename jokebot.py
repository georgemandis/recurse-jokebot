import random
import json
import os


class JokeBotHandler(object):

    JOKE_FILE = "jokes.json"
    SUCCESS_THRESHOLD = 20
    FAILURE_THRESHOLD = 0   
              
    
    def __init__(self):
        self.commands = {
            "joke": self.tell_joke,
            "best": self.tell_best_joke,
            "recent": self.recent_jokes,
            "add": self.add_joke,
            "up": self.upvote,
            "down": self.downvote,
            "help": self.usage,
            "default": self.usage
        }

        filename = os.path.join(os.path.dirname(__file__), self.JOKE_FILE)
        with open(filename) as json_file:
            self.jokes = json.load(json_file)['jokes']        

            
    def save_jokes(self, jokes, message=None):
        filename = os.path.join(os.path.dirname(__file__), self.JOKE_FILE)
        with open(filename, 'w') as json_file:
            json.dump({"jokes": jokes}, json_file)

        
    def tell_joke(self, args, jokes, message=None):
        if not jokes or len(jokes) == 0:
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

        content = "Joke #{}:\n\n{}\n\n *submitted by {}*".format(
            returned_joke_index, returned_joke['joke'], returned_joke['submitted_by'])

        return content
    
    
    def tell_best_joke(self, args, jokes, message=None):
        if len(jokes) == 0:
            return "I don't know any jokes yet. Teach me some!"
                
        best_joke_index, best_joke = max(enumerate(jokes), key=lambda item: item[1]["score"])        
              
        content = "Here's joke #{}. It's my best joke:\n\n{}\n\n *submitted by {}*".format(
        best_joke_index, best_joke['joke'], best_joke['submitted_by'])
        
        return content

    
    def recent_jokes(self, args, jokes, message=None):
        if len(jokes) == 0:
            return "I don't know any jokes yet. Teach me some!"

        format_string = "{}: {}\n(submitted by {})"
        return "\n\n".join([format_string.format(index, d['joke'], d['submitted_by']) for index, d in enumerate(jokes)][-10:])

    
    def add_joke(self, args, jokes, message):
        # strip the command & initial space (i.e. 'add ') from the joke content 
        new_joke = message['content'][4:].replace('\\n', '\n').strip()
        new_joke_dict = {
            "joke": new_joke,
            # zulip-terminal doesn't return sender_full_name and other metadata
            "submitted_by": message.get('sender_full_name', (message.get('sender_email', '?????'))),
            "email": message.get('sender_email'),
            "score": 10
        }

        jokes.append(new_joke_dict)
        new_joke_id = len(jokes) - 1
        # storage.put('jokes', jokes, message=None)
        self.save_jokes(jokes)
        content = "Joke added!  Hilarious. Here's joke #{} \n\n{}".format(new_joke_id, new_joke)

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


`joke [optional joke-id]` -- I'll tell you a randomly selected joke or the joke you requested
`add [joke]` -- Submit a joke of your own (Your RC Zulip name will be attached)
`up [joke-id]` -- Give a +1 vote to a specific joke.
`down [joke-id]` -- Give a -1 vote to a specific joke.        
`best` -- Return the joke with the highest score
`recent` -- Show the 10 most recently added jokes
        
        '''

            
    def handle_message(self, message, bot_handler):
        self.bot_handler = bot_handler
        jokes = self.jokes
        msg_content = message['content']
        
        # if user didn't send a message, display help screen
        if msg_content:      
            command = msg_content.split()[0]
            args = msg_content.split()[1:]            
            content = self.commands.get(
                command.lower(), self.commands['default'])(args, jokes, message)
        else:
            content = self.commands.get("default")()


        bot_handler.send_reply(message, content)


handler_class = JokeBotHandler
