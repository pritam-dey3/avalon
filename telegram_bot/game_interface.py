from game.avalon import Game, Player
from telegram import User

class TgPlayer(Player):
    def __init__(self, user: User):
        super(TgPlayer, self).__init__(self, id=user.id, name=user.first_name)
        self.user = user
    
    def send_msg(self, text: str, guide: str, options: list, m):
        # print(f"Private message to {self.name}...")
        self.user.send_message(f"Private message to {self.name}...")

        if not options:
            # print(text)
            self.user.send_message(text)
            return 0

        options = [str(opt) for opt in options]
        if not guide:
            guide = "You only have the options\n" + ", ".join(options)

        while True:
            self.user.send_message(text + '\n' + guide)
            # print(text)
            # print(guide)
            responses = input().split()
            if len(responses) != m:
                print(f"You have to enter {m} valid answers separated by spaces.")
            elif not all(entry in options for entry in responses):
                print("Incorrect entries.")
            else:
                if m == 1:
                    return responses[0]
                else:
                    return responses