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

                    content = "Score for joke #{} is now {}".format(joke_index, jokes[joke_index]['score'])
                    # vote the joke up or down

                    
            except:
                content = self.usage()   

        if msg_content.startswith("add"):
            new_joke = message['content'].replace("add", "").replace('\\n', '\n').strip()
            new_joke_dict = {
                "joke": new_joke,
                "submitted_by": message.get('sender_full_name', (message.get('sender_email', '?????jo')) ) ,
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
                good_jokes = [ d for d in jokes if d['score'] > 0 ]
                random_joke = random.randint(0, len(good_jokes) - 1)
                content = "Joke #{}:\n\n{}".format(random_joke, good_jokes[random_joke]['joke'])

        bot_handler.send_reply(message, content)

handler_class = JokeBotHandler
