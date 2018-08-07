import array
def is_little_endian():
    a = array.array('H', [1]).tostring()
    if a[0] == 1:
        print("小端")
    else:
        print("大端")
is_little_endian()
