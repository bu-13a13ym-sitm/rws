import threading
import time
from socket import *
import numpy as np
import matplotlib.pyplot as plt
import pyautogui
from post_discord import post_discord

DELETE = 'del'
webhook_url = "https://canary.discord.com/api/webhooks/1375120983576547438/i9MsyTZI_uuqhmHSazPk7T3bqPMZgCanCffFzfN7k3gP7HG7VQV2fT-n8BuyO_qZZ6pK"

def v_to_dist(voltage):
    return -18.737 * voltage + 67.827

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

    fps = 1 / 0.05
    clk = False
    clk_lock = False
    clk_start = 0
    clk_accept = 1 * fps
    frame = 0
    clk_th = 1.0
    recorded_values = []
    curr_value = None

    key_offset = 12
    key_width = 1.0

    try:
        while True:
            if not th.data:
                break

            if th.received:
                sensor_data = th.get_data()
                voltage = sensor_data[7]
                clk_voltage = sensor_data[0]
                distance = v_to_dist(voltage) - key_offset
            
                if clk_lock:
                    if clk_voltage > clk_th:
                        clk_lock = False

                elif not clk:
                    if  clk_voltage < clk_th:
                        clk = True
                        clk_start = frame

                    elif distance is not None and distance >= 0 and distance < 11 * key_width:
                        curr_value = int(distance / key_width) + 1
                        if curr_value == 10:
                            curr_value = 0
                        elif curr_value == 11:
                            curr_value = DELETE
                    else:
                        curr_value = None
                
                else:
                    if frame > clk_start + clk_accept:
                        clk = False
                        clk_lock = True
                        clk_start = 0
                        curr_value = None
                        
                    elif clk_voltage > clk_th:
                        clk = False
                        clk_start = 0
                        if curr_value is None:
                            pyautogui.press('enter')
                            break
                        elif curr_value == DELETE:
                            recorded_values = recorded_values[:len(recorded_values) - 1]
                            pyautogui.press('backspace')
                        else:
                            recorded_values.append(curr_value)
                            pyautogui.write(str(curr_value))
                
                display_text = ""
                if clk_lock:
                    display_text += "locked\n"
                display_text += "{}".format(curr_value) if curr_value is not None else "invalid input"
                display_text += "\n{}".format(recorded_values)
                text_obj.set_text(display_text)
                if clk:
                    text_obj.set_color('red')
                else:
                    text_obj.set_color('black')
                fig.canvas.draw()
                fig.canvas.flush_events()

                time.sleep(1 / fps)
                frame += 1
                
    except KeyboardInterrupt:
        pass

    str_num = ''.join(map(str, recorded_values))
    print("recorded values: ", recorded_values, str_num)
    post_discord(str_num, webhook_url)
    plt.close()