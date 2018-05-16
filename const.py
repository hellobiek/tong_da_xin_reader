# coding=utf-8
class Const:
    class CError(Exception):
        pass

    class ConstError(CError):
        def __init__(self, expression, message):
            self.expression = expression
            self.message = message

    class ConstCaseError(CError):
        def __init__(self, expression, message):
            self.expression = expression
            self.message = message

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError(self.CError, "can't change const value!")
        if not name.isupper():
            raise self.ConstCaseError(self.CError, 'const "%s" is not all letters are capitalized' %name)
        self.__dict__[name] = value

import sys
sys.modules[__name__] = Const()

import const
const.DATA_PATH = "/Users/hellobiek/Library/Application Support/CrossOver/Bottles/海通证券/drive_c/new_haitong/vipdoc/sh/lday/"
const.DATA_DEST_PATH = "/Users/hellobiek/Desktop/data"
