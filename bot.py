from cls import AddressBook, Record, Name, Phone, Birthday, Field


class Bot:

    def __init__(self):
        self.adressbook = AddressBook()

    def parse_input(self, user_input):
        command, *args = user_input.split()
        command = command.lstrip()

        handler = self.get_bot_handlers().get(command.lower())
        if handler:
            return handler,
        handler = self.get_book_handlers().get(command.lower())
        if handler is None:
            if args:
                command = command + ' ' + args[0]
                args = args[1:]
                handler = self.get_book_handlers().get(command.lower())
                return handler,
            else:
                return self.unknown_command_handler, user_input
        return handler, *args

    def unknown_command_handler(self, command):
        return f"{command} not persist"

    def hello_handler(self):
        command_bot = '\n'.join(self.get_book_handlers().keys())
        command_book = '\n'.join(self.get_book_handlers().keys())
        message = (
            f"How can I help you?\n "
            f"Available command:\n"
            f"{command_bot}"
            f"{command_book}"
        )
        return message

    def exit_handler(self):
        return 'EXIT'

    def get_bot_handlers(self):
        return {
            'help': self.hello_handler,                    # привітання
            'exit': self.exit_handler,                     # вихід
            'goodbye': self.exit_handler,                  # вихід
            'close': self.exit_handler                     # вихід
        }

    def get_book_handlers(self):
        return {
            'add': self.adressbook.create_and_add_record,  # додавання запису
            'add-phone': self.adressbook.add_phone_handler,
            'change': self.adressbook.change_handler,      # зміна телефону
            'show-all': self.adressbook.show_all_handler,  # показати всі записи
            'show': self.adressbook.show_n_handler,        # показати N-кількість записів
            'phone': self.adressbook.phone_handler,        # показати телефон
            'search': self.adressbook.search               # пошук по телефону або імені
        }

    def run(self):
        while True:
            # example: add Petro +380991234567
            self.adressbook.load()
            user_input = input('Please enter command and args: ')
            self.adressbook.log(user_input, prefix='com')
            handler, *data = self.parse_input(user_input)
            try:
                result = handler(*data)
                if result == 'EXIT':
                    print('Good bye!')
                    break
                print(result)
                self.adressbook.log(result, prefix='res')
                self.adressbook.autosave()
            except (ValueError, IndexError, TypeError) as exp:
                print(exp)
                continue


if __name__ == "__main__":
    my_bot = Bot()
    my_bot.run()
