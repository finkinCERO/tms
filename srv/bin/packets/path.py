#!/usr/bin/python3.8
import base64
import time


class Path:
    def __init__(self, destAddress, destSequence):
        self.destAddress = destAddress
        self.destSequence = destSequence

    def toDict(self):
        obj = {}
        obj["destAddress"] = self.destAddress
        obj["destSequence"] = self.destSequence
        return obj
