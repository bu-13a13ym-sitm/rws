import threading
import time
from socket import *
import numpy as np
import matplotlib.pyplot as plt

def voltage_to_distance(voltage):#need to be modified
    if voltage <= 0.42:
        return None
    return 27.86 / (voltage - 0.42)

def v_to_dist(voltage):
    return -936.84 * voltage + 67.827

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
    curr_value = None

    key_offset = 12
    key_width = 1.5

    try:
        while True:
            if not th.data:
                break

            if th.received:
                sensor_data = th.get_data()
                voltage = sensor_data[7]
                accel = sensor_data[0]
                distance = v_to_dist(voltage)

                distance -= key_offset
                if distance >= 0 and distance < 11 * key_width:
                    curr_value = int(distance / key_width) + 1
                    if curr_value > 9:
                        curr_value = 0
                else:
                    curr_value = None
                #recorded_values.append(curr_value)
                
                display_text = "{}".format(curr_value) if curr_value is not None else "invalid input"
                text_obj.set_text(display_text)
                fig.canvas.draw()
                fig.canvas.flush_events()

                time.sleep(0.1)
                frame += 1
                
    except KeyboardInterrupt:
        pass

    str_num = ''.join(map(str, recorded_values))
    #print("recorded values: ", recorded_values, str_num)
    plt.close()