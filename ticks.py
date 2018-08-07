# coding=utf-8
import os
import sys
import ctypes
import pickle
import struct
import binascii
import datetime
import const as ct
from models import TickTradeDetail, TickDetailModel

def unsigned2signed(value):
    return ctypes.c_int32(value).value

def signed2unsigned(value, b = 32):
    if 32 == b:
        return ctypes.c_uint32(value).value
    elif 8 == b:
        return ctypes.c_uint8(value).value
    elif 16 == b:
        return ctypes.c_uint16(value).value

def int_overflow(val):
    maxint = 2147483647
    if not -maxint - 1 <= val <= maxint:
        val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
    return val

def unsigned_left_shitf(n,i):
    if n < 0:
        n = ctypes.c_uint32(n).value
    if i < 0:
        return int_overflow(n >> abs(i))
    return int_overflow(n << i)

def read4(tic_detail_bytes):
    left = tic_detail_bytes[0:4]
    tic_detail_bytes = tic_detail_bytes[4:]
    return left, tic_detail_bytes

def read1(tic_detail_bytes):
    left = tic_detail_bytes[0:1]
    tic_detail_bytes = tic_detail_bytes[1:]
    return signed2unsigned(struct.unpack('b', left)[0], 8), tic_detail_bytes

def read2(tic_detail_bytes):
    left = tic_detail_bytes[0:2]
    tic_detail_bytes = tic_detail_bytes[2:]
    return signed2unsigned(struct.unpack('H', left)[0], 16), tic_detail_bytes

def dict2list(cdic:dict):
    keys = cdic.keys()
    vals = cdic.values()
    return [(key, val) for key, val in zip(keys, vals)]

def parse_tick_price(ttd_list, tic_detail_bytes, tdm):
    tmp_size = 32
    left, tic_detail_bytes = read4(tic_detail_bytes)
    tick_data_item = struct.unpack('I', left)[0]
    for _ in range(1, tdm.count):
        #解析类型
        _type = unsigned_left_shitf(tick_data_item, -31)
		#解析时间
        tick_data_item = unsigned_left_shitf(tick_data_item, 1)
        tmp_size -= 1
        if 0 == tmp_size:
            left, tic_detail_bytes = read4(tic_detail_bytes)
            tick_data_item = struct.unpack('I', left)[0]
            tmp_size = 32
        tmp_check_sum = 3
        klist = sorted(dict2list(ct.HASH_TABLE_DATETIME), key=lambda x: int(x[1], 16), reverse=False)
        tmp_index, tick_data_item, tic_detail_bytes, tmp_size = time_recursion(tmp_check_sum, tick_data_item, tmp_size, tic_detail_bytes, klist)
        _time = ttd_list[len(ttd_list)-1].dtime + tmp_index
		#解析价格
        tmp_check_sum = 3
        klist = sorted(dict2list(ct.HASH_TABLE_PRICE), key=lambda x: abs(int(x[1], 16)), reverse=False)
        tmp_index, tick_data_item, tic_detail_bytes, tmp_size = price_recursion(tmp_check_sum, tick_data_item, tmp_size, tic_detail_bytes, klist)
        if tmp_index != len(ct.HASH_TABLE_PRICE) - 1:
            _price = ttd_list[len(ttd_list)-1].price + tmp_index
        else:
            tmp_check_sum = 0
            tmp_index = 32
            while tmp_index > 0:
                tmp_index -= 1
                tmp_check_sum = unsigned_left_shitf(tmp_check_sum, 1) | unsigned_left_shitf(tick_data_item, -31)
                tick_data_item = unsigned_left_shitf(tick_data_item, 1)
                tmp_size -= 1
                if 0 == tmp_size:
                    left, tic_detail_bytes = read4(tic_detail_bytes)
                    tick_data_item = struct.unpack('I', left)[0]
                    tmp_size = 32
            _price = ttd_list[len(ttd_list)-1].price + tmp_index
        ttd_list.append(TickTradeDetail(_time, _price, 0, _type))
    return ttd_list

def time_recursion(tmp_check_sum, tick_data_item, tmp_size, tic_detail_bytes, klist):
    tmp_index = 0
    while tmp_index < len(klist):
        tmp_check_sum = unsigned_left_shitf(tmp_check_sum, 1) | unsigned_left_shitf(tick_data_item, -31)
        tick_data_item = unsigned_left_shitf(tick_data_item, 1)
        tmp_size -= 1
        if 0 == tmp_size:
            left, tic_detail_bytes = read4(tic_detail_bytes)
            tick_data_item = struct.unpack('I', left)[0]
            tmp_size = 32
        if int(klist[tmp_index][1], 16) == tmp_check_sum: break
        tmp_index += 1
    return klist[tmp_index][0], tick_data_item, tic_detail_bytes, tmp_size

def price_recursion(tmp_check_sum, tick_data_item, tmp_size, tic_detail_bytes, klist):
    tmp_check_sum = unsigned_left_shitf(tmp_check_sum, 1) | unsigned_left_shitf(tick_data_item, -31)
    tick_data_item = unsigned_left_shitf(tick_data_item, 1)
    tmp_size -= 1
    if 0 == tmp_size:
        left, tic_detail_bytes = read4(tic_detail_bytes)
        tick_data_item = struct.unpack('I', left)[0]
        tmp_size = 32
    tmp_index = 0
    while int(klist[tmp_index][1], 16) != tmp_check_sum:
        if tmp_check_sum > 0x3FFFFFF or int(klist[tmp_index][1], 16) < tmp_check_sum:
            tmp_index += 1
            if tmp_index < len(klist): continue
        else:
            tmp_index = 0
            tmp_check_sum = unsigned_left_shitf(tmp_check_sum, 1) | unsigned_left_shitf(tick_data_item, -31)
            tick_data_item = unsigned_left_shitf(tick_data_item, 1)
            tmp_size -= 1
            if 0 == tmp_size:
                left, tic_detail_bytes = read4(tic_detail_bytes)
                tick_data_item = struct.unpack('I', left)[0]
                tmp_size = 32
    return klist[tmp_index][0], tick_data_item, tic_detail_bytes, tmp_size
                    
def parse_tick_detail(td_bytes, tdm):
    ttd_list = list()
    ttd = TickTradeDetail(tdm.dtime, tdm.price, tdm.volume, unsigned_left_shitf(tdm.type, -15))
    ttd_list.append(ttd)
    trade_buffer = td_bytes[0 : tdm.vol_offset]
    volume_buffer = td_bytes[tdm.vol_offset : (tdm.vol_offset + tdm.vol_size)]
    #解析交易时间及价格信息
    ttd_list = parse_tick_price(ttd_list, trade_buffer, tdm)
    #解析成交量
    total_vol = 0
    for i in range(1, tdm.count):
        result_vol = 0
        byte_volume, volume_buffer = read1(volume_buffer)
        if byte_volume <= 252:
            result_vol = int(byte_volume)
        elif byte_volume == 253:
            tmp_vol, volume_buffer = read1(volume_buffer)
            result_vol = int(tmp_vol) + int(byte_volume)
            result_vol = signed2unsigned(result_vol, 16)
        elif byte_volume == 254:
            tmp_vol, volume_buffer = read2(volume_buffer)
            result_vol = int(tmp_vol) + int(byte_volume)
        else:
            tmp_vol1, volume_buffer = read1(volume_buffer)
            tmp_vol2, volume_buffer = read2(volume_buffer)
            result_vol = int(0xFFFF * int(tmp_vol1) + int(tmp_vol2) + 0xFF)
        ttd_list[i].volume = result_vol
        total_vol += result_vol
        ttd_list[i].dtime = set_trade_time(ttd_list[i].dtime)
        ttd_list[i].price = ttd_list[i].price / 100
    ttd_list[0].dtime = set_trade_time(-5)
    ttd_list[0].price = ttd_list[0].price / 100
    total_vol += ttd_list[0].volume
    return ttd_list

def set_trade_time(time_val):
    result = time_val + 570 if time_val <= 120 else time_val + 660
    _hour = (result / 60) % 24
    _minute = result % 60
    return "%2d:%2d" % (_hour, _minute)

def parse_tick_item(data,code):
    tick_item_bytes = data[:20]
    tic_detail_bytes = data[20:]
    (sdate, scount, svol_offset, svol_size, stype, sprice, svolume) = struct.unpack("iHHHHii", tick_item_bytes)
    stime = ctypes.c_uint8(stype).value
    tdm = TickDetailModel(sdate, stime, sprice, svolume, scount, stype, svol_offset, svol_size)
    ttd_list = parse_tick_detail(tic_detail_bytes, tdm)
    for item in ttd_list:
        print(item.volume)

def read_tick(filename, code_id):
    with open(filename, 'rb') as fobj:
        stockCount = struct.unpack('<h', fobj.read(2))[0]
        for idx in range(stockCount):
            (market, code, _, date, t_size, pre_close) = struct.unpack("B6s1siif", fobj.read(20))
            code = code.decode()
            raw_tick_data = fobj.read(t_size)
            if code == code_id:
                parse_tick_item(raw_tick_data,code)

if __name__ == "__main__":
    read_tick("20180801/20180801.tic", "000001")
