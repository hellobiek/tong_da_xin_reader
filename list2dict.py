# coding=utf-8
import const as ct
for key in ct.HASH_TABLE_DATETIME:
    x = int(ct.HASH_TABLE_DATETIME[key], 16)
    print(ct.HASH_TABLE_DATETIME[key])
    print(x)
    print(hex(x))
    import sys
    sys.exit(0)
