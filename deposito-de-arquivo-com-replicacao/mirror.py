import os
import sys
import utils
import signal
import socket
import hashlib
import protocolo

from enums import *
from re import match
from config import settings
from server_client import ServerClient


class Mirror(ServerClient):
    pass


def main():
    mirror = Mirror.create()


if __name__ == '__main__':
    main()
    exit()
