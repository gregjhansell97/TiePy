#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dog import Dog

def countable(func):
    def wrapper(*args, **kwargs):
        wrapper.count += 1
        func(*args, **kwargs)
    wrapper.count = 0
    return wrapper

def dog_callbacks():
    class cb:
        @staticmethod
        @countable
        def on_age_change(dog, old_value, new_value):
            assert old_value + 1 == new_value
        @staticmethod
        @countable
        def on_bark(dog, retval):
            assert retval == "wuff"
        @staticmethod
        @countable
        def on_say(dog, retval, cmd:str):
            if cmd.lower() in dog.commands:
                assert retval == Dog.YES
            else:
                assert retval == Dog.NO
        @staticmethod
        @countable
        def on_teach(dog, retval, cmd:str):
            assert cmd in dog.commands
    return cb