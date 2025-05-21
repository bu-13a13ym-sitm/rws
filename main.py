import threading
import time
from socket import *
import numpy as np
import matplotlib.pyplot as plt

def voltage_to_distance(voltage):#need to be modified
    if voltage <= 0.42:
        return None
    return 27.86 / (voltage - 0.42)

class ReceiveThread(threading.Thread):
    def __init__(self, PORT=12345):
        threading.Thread.__init__(self)
        self.data = 'hoge'
        self.kill_flag = False
        # line information
        self.HOST = "127.0.0.1"
        self.PORT = PORT
        self.BUFSIZE = 1024
        self.ADDR = (gethostbyname(self.HOST), self.PORT)
        # bind
        self.udpServSock = socket(AF_INET, SOCK_DGRAM)
        self.udpServSock.bind(self.ADDR)
        self.received = False

    def get_data(self):
        data_ary = []
        for i in reversed(range(8)):
            num = int(str(self.data[i*8:(i+1)*8]))
            data_ary.append(num / 167.0 / 10000)
        self.received = False
        return data_ary

    def run(self):
        while True:
            try:
                data, self.addr = self.udpServSock.recvfrom(self.BUFSIZE)
                self.data = data.decode()
                self.received = True
            except:
                pass


if __name__ == '__main__':
    th = ReceiveThread()
    th.setDaemon(True)
    th.start()
    
    plt.ion()
    fig, ax = plt.subplots()
    text_obj = ax.text(0.5, 0.5, '', fontsize=30, ha='center', va='center')
    ax.axis('off')

    clk = False
    clk_start = 0
    clk_accept = 5
    frame = 0
    clk_th = 0.5
    recorded_values = []
    curr_value = 0

    try:
        while True:
            if not th.data:
                break

            if th.received:
                sensor_data = th.get_data()
                voltage = sensor_data[4]
                accel = sensor_data[0]
                distance = voltage_to_distance(voltage)
            
                if not clk:
                    if  accel > clk_th:
                        clk = True
                        clk_start = frame

                    elif distance is not None:
                        curr_value = int(distance / 1.5)
                
                if clk:
                    if frame > clk_start + clk_accept:
                        clk = False
                        clk_start = 0
                        
                    elif accel < -clk_th:
                        clk = False
                        clk_start = 0
                        if (curr_value < 10):
                            recorded_values.append(curr_value)
                        else:
                            break
                
                display_text = "{}".format(curr_value)
                text_obj.set_text(display_text)
                fig.canvas.draw()
                fig.canvas.flush_events()

                time.sleep(0.1)
                frame += 1
                
    except KeyboardInterrupt:
        pass

    str_num = ''.join(map(str, recorded_values))
    print("recorded values: ", recorded_values, str_num)
    plt.close()