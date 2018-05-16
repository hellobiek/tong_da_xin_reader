# coding=utf-8
import os
import struct
import datetime
import const as ct

def stock_csv(file_source_path, name):
    data = []
    file_target_path = os.path.join(ct.DATA_DEST_PATH, "%s.csv" % name)
    with open(file_source_path, 'rb') as source_obj:
        with open(file_target_path, 'w+') as target_obj:
            while True:
                stock_date = source_obj.read(4)
                stock_open = source_obj.read(4)
                stock_high = source_obj.read(4)
                stock_low  = source_obj.read(4)
                stock_close = source_obj.read(4)
                stock_amount = source_obj.read(4)
                stock_vol = source_obj.read(4)
                stock_reservation = source_obj.read(4)
                # date,open,high,low,close,amount,vol,reservation
                if not stock_date:
                    break
                stock_date = struct.unpack("i", stock_date)     #4字节 如20091229
                stock_open = struct.unpack("i", stock_open)     #开盘价*100
                stock_high = struct.unpack("i", stock_high)     #最高价*100
                stock_low= struct.unpack("i", stock_low)        #最低价*100
                stock_close = struct.unpack("i", stock_close)   #收盘价*100
                stock_amount = struct.unpack("f", stock_amount) #成交额
                stock_vol = struct.unpack("i", stock_vol)       #成交量
                stock_reservation = struct.unpack("i", stock_reservation) #保留值
                date_format = datetime.datetime.strptime(str(stock_date[0]),'%Y%M%d') #格式化日期
                list= date_format.strftime('%Y-%M-%d')+","+str(stock_open[0]/100)+","+str(stock_high[0]/100.0)+","+str(stock_low[0]/100.0)+","+str(stock_close[0]/100.0)+","+str(stock_vol[0])+"\r\n"
                target_obj.writelines(list)

if __name__ == "__main__":
    list_files = os.listdir(ct.DATA_PATH)
    for t_file in list_files:
        stock_csv(os.path.join(ct.DATA_PATH,t_file), t_file[:-4])
