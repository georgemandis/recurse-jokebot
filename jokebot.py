import random
import json

class JokeBotHandler(object):    
    '''
    A docstring documenting this bot.
    '''

    def usage(self):
        return "This is the joke bot"

    def get_jokes(self):
        with open('./jokes.json') as json_file:
            return json.load(json_file)['jokes']
    
    def save_jokes(self, jokes):
        with open('./jokes.json', 'w') as json_file:
            json.dump({"jokes":jokes}, json_file)

    def handle_message(self, message, bot_handler):
        content = self.usage()
        # storage = bot_handler.storage
        jokes = self.get_jokes()

        # if storage.contains('jokes'):
        #     jokes = storage.get('jokes')        

        msg_content = message['content'].lower()
        if msg_content.startswith("add"):
            new_joke = message['content'].replace("add", "").replace('\\n', '\n').strip()
            new_joke_dict = {
                "joke": new_joke,
                "submitted_by": message['sender_email'],
                "score": 10
            }
            jokes.append(new_joke_dict)
            # storage.put('jokes', jokes)
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
                random_joke = random.randint(0, len(jokes) - 1)
                content = "Joke #{}:\n\n{}".format(random_joke, jokes[random_joke]['joke'])

        bot_handler.send_reply(message, content)

handler_class = JokeBotHandler
