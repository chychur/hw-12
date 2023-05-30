from typing import Any
from collections import UserList
from datetime import datetime
import pickle
import re


class Field:

    def __init__(self, value: Any) -> None:
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __str__(self) -> str:
        return f'{self.value}'

    def __repr__(self) -> str:
        return f'{self.value}'


class Name(Field):

    def __init__(self, value: str) -> None:
        super().__init__(value)


class Phone(Field):

    def __init__(self, value) -> None:
        super().__init__(value)

    @Field.value.setter
    def value(self, value):
        if re.match('^\\+38\d{10}$', value) or value == '':
            Field.value.fset(self, value)
        else:
            raise ValueError(
                'Incorrect phone number format! '
                'Please provide correct phone number format.'
            )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self.value == other.value
        return self.value == other

    def __hash__(self):
        return hash(self.value)


class Birthday(Field):
    def __init__(self, value) -> None:
        super().__init__(value)

    @Field.value.setter
    def value(self, value):
        if not value:
            Field.value.fset(self, '')
        elif re.match('^\d{2}/\d{2}/\d{4}$', value):
            Field.value.fset(self,
                             datetime.strptime(value, "%d/%m/%Y").date()
                             )
        else:
            raise ValueError(
                'Incorrect date! Please provide correct date format.')


class Record:

    def __init__(self, name: Name, phone: Phone | None = None, birthday: Birthday | None = None):
        self.name = name

        self.birthday = birthday
        self.phones = set()
        self.add_phone(phone)

    def days_to_birthday(self):
        if not self.birthday:
            return
        now = datetime.now()
        if (self.birthday.value.replace(year=now.year) - now).days > 0:
            return (self.birthday.value.replace(year=now.year) - now).days
        return (self.birthday.value.replace(year=now.year) + 1).days

    def __repr__(self) -> str:
        return f'Record (Name:"{self.name}", Phone:"{self.show_phones()}", Birthday:"{self.birthday}")'

    def __str__(self) -> str:
        return f'Name: {self.name}, Phone:{self.show_phones()}, Birthday:{self.birthday or "Empty"}'

    def add_phone(self, phone):
        if isinstance(phone, str):
            phone = Phone(phone)
        self.phones.add(phone)

    def show_phones(self):
        if self.phones:
            list_phones = [str(p) for p in self.phones]
            return ", ".join(list_phones)
        return 'Empty'

    @property
    def record(self):
        return {
            'name': self.name.value,
            'phones': self.show_phones(),
            'birthday': self.birthday.value if self.birthday else 'Empty'
        }

    def __getitem__(self, item: str):
        return self.record.get(item)


class AddressBook(UserList):

    def __init__(self) -> None:
        self.data: list[Record] = []
        self.current_value = 0
        self.step = 0
        self.file_name_save = 'save.bin'

    def __getitem__(self, index):
        return self.data[index]

    def create_and_add_record(self, name, phone: str, birthday: str | None = None):
        record = Record(Name(name), Phone(phone), Birthday(birthday))
        self.add_record_handler(record)

        return f"Added contact {record}"

    def add_record_handler(self, record: Record):
        self.data.append(record)

    def add_phone_handler(self, name, phone: str):
        for record in self.data:
            if record.name.value == name:
                record.phones.add(Phone(phone))

    def del_phone_handler(self, name, phone):
        for record in self.data:
            if record.name.value == name:
                record.phones.discard(Phone(phone))

    def change_handler(self, name: str, old_phone: str, phone: str):  # зміна телефону
        old_phone_title = Phone(old_phone)
        for record in self.data:
            if record.name.value == name:
                if record.phones:
                    self.add_phone_handler(name, phone)
                    self.del_phone_handler(name, old_phone)

                return (
                    f'For user [ {record.name.value} ] had been changed phone number! \n'
                    f' Old phone number: {old_phone_title.value} \n'
                    f' New phone number: {record.phones}'
                )
        return f'Not found contact for name {name}'

    def phone_handler(self, name: str):  # показати номер телефону
        for record in self.data:
            if record.name.value == name:
                return f"Phone(s) of {name} is: {record.phones}"
        return f"Phone for user {name} not found"

    def show_all_handler(self):
        self.step = 0
        result = ''
        header = '='*51 + '\n' + \
            '|{:^5}|{:<12}|{:^15}|{:^14}|\n'.format(
                'No.', 'Name', 'Phone(s)', 'Birthday') + '='*51 + '\n'
        foter = '='*51 + '\n'
        counter = 0
        for record in self.data:
            counter += 1
            result += '|{:^5}|{:<12}|{:^15}|{:^14}|\n'.format(
                counter, record.name.value, record.show_phones(), record.birthday.value if record.birthday else 'Empty')
        counter = 0
        result_tbl = header + result + foter
        return result_tbl

    def show_n_handler(self, n: int):
        n = int(n)
        if n > 0:
            if len(self.data) - self.step >= n:

                result = ''
                header = '='*51 + '\n' + \
                    '|{:^5}|{:<12}|{:^15}|{:^14}|\n'.format(
                        'No.', 'Name', 'Phone(s)', 'Birthday') + '='*51 + '\n'
                foter = '='*51 + '\n'

                for record in self.data[self.step:self.step+n]:
                    self.step += 1
                    result += '|{:^5}|{:<12}|{:^15}|{:^14}|\n'.format(
                        self.step, record.name.value, record.show_phones(), record.birthday.value if record.birthday else 'Empty')

                result_tbl = header + result + foter
                return result_tbl
            else:
                return (
                    f'Curent AdressBook volume is {len(self.data)} records'
                    f'Now you are in the end of AdressBook'
                )
        else:
            raise ValueError('Wrong value! the number must be greater than 0')

    def __iter__(self):
        return self

    def __next__(self):

        if self.current_value < len(self.data):

            result = f' {self.current_value + 1} | Name: {self.data[self.current_value].name.value}, Phone(s):{self.data[self.current_value].phones}, Birthday: {self.data[self.current_value].birthday or "Empty"}'
            self.current_value += 1
            return result

        raise StopIteration

    def search(self, pattern):
        pattern_searched = str(pattern.strip().lower().replace(' ', ''))
        result = ''
        header = '\n' + f'  RESULT of searching with your request: "{pattern}"' + '\n' + '='*45 + '\n' + \
            '|{:<12}|{:^15}|{:^14}|\n'.format(
                'Name', 'Phone(s)', 'Birthday') + '='*45 + '\n'
        foter = '='*45 + '\n'
        for record in self.data:
            for phone in record.phones:
                if str(phone).find(pattern_searched) != -1:
                    result += '|{:<12}|{:^15}|{:^14}|\n'.format(
                        record.name.value, record.phones, record.birthday.value)
            if str(record.name.value.find(pattern_searched)) != -1:
                result += '|{:<12}|{:^15}|{:^14}|\n'.format(
                    record.name.value, record.phones, record.birthday.value)
            else:
                result = f'There was nothing found with your request: "{pattern}"'
                header = ''
                foter = ''
        result_tbl = header + result + foter
        return result_tbl

    def autosave(self):
        with open(self.file_name_save, 'wb') as file:
            pickle.dump(self.data, file)
        self.log("Addressbook has been saved!")

    def load(self):
        with open(self.file_name_save, 'rb') as file:
            self.data = pickle.load(file)
        self.log("Addressbook has been loaded!")
        return self.data

    def log(self, log_message: str, prefix: str | None = None):
        current_time = datetime.strftime(datetime.now(), '%H:%M:%S')
        if prefix == 'com':
            message = f'[{current_time}] USER INPUT : {log_message}'
        elif prefix == 'res':
            message = f'[{current_time}] BOT RESULT : \n{log_message}\n'
        elif prefix == 'err':
            message = f'[{current_time}] !!! === ERROR MESSAGE === !!! {log_message}\n'
        elif prefix == None:
            message = f'[{current_time}] {log_message}'
        with open('logs.txt', 'a') as file:
            file.write(f'{message}\n')


if __name__ == "__main__":
    USERS = AddressBook()
    n1 = Name('Andy')
    p1 = Phone('+380674169297')
    record1 = Record(n1, p1)
    print(record1)
    USERS.add_record_handler(record1)

    n2 = Name('Alex')
    p2 = Phone('+380674169223')
    record2 = Record(n2, p2)

    USERS.add_record_handler(record2)

    n3 = Name('Mike')
    p3 = Phone('+380674169200')
    record3 = Record(n3, p3)

    USERS.add_record_handler(record3)

    print(len(USERS))
    print(USERS.show_all_handler())

    print(USERS.show_n_handler(1))
    print(USERS.show_n_handler(1))

    USERS.add_phone_handler('Andy', '+380674169298')

    print(USERS.show_all_handler())

    # for item in USERS:
    #     print(item)
