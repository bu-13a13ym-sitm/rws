import sys
import os

account_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(account_dir)

import threading
import time
import random
from socket import *
import matplotlib.pyplot as plt
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from account import *

DELETE = 'del'

def myRand():
    return random.uniform(0.5, 1)

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
        driver_path = os.path.expanduser("~/exp2025-05-19/ExpDir/chromedriver")
        options = webdriver.ChromeOptions()
        options.add_argument("--user-agent={}".format(user_agent))
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
        driver.set_window_position(x=400, y=30)
        discord_url = "https://discord.com/"
        wait_time = 10
        waiter = WebDriverWait(driver, wait_time)
        driver.get(discord_url + "login")
        waiter.until(EC.visibility_of_element_located((By.NAME, "email"))).send_keys(email)
        time.sleep(myRand())
        waiter.until(EC.visibility_of_element_located((By.NAME, "password"))).send_keys(password)
        time.sleep(myRand())
        waiter.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))).click()
        time.sleep(myRand() * 5)
        driver.get(discord_url + "channels/@me/" + dm_ID)
        waiter.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-slate-node="element"]'))).click()

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

                        elif distance is not None and distance >= 0 and distance < 12 * key_width:
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
                    
                    display_text = "{}".format(curr_value) if curr_value is not None else "invalid input"
                    display_text += "\n{}".format(recorded_values)
                    text_obj.set_text(display_text)
                    fig.canvas.draw()
                    fig.canvas.flush_events()

                    time.sleep(1 / fps)
                    frame += 1
                    
        except KeyboardInterrupt:
            pass

        str_num = ''.join(map(str, recorded_values))
        print("recorded values: ", recorded_values, str_num)
        plt.close()
    
    finally:
        driver.quit()