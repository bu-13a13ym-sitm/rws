import time
import random
import matplotlib.pyplot as plt

def voltage_to_distance(voltage):
    if voltage <= 0.42:
        return None
    return 27.86 / (voltage - 0.42)

plt.ion()
fig, ax = plt.subplots(figsize=(5, 3))
text_obj = ax.text(0.5, 0.5, '', fontsize=30, ha='center', va='center')
ax.axis('off')

clk = False
clk_start = 0
clk_accept = 5
frame = 0
clk_th = 0.5
strnum = ''

try:
    while True:
        # ランダムなテストデータ生成
        voltage = random.uniform(0.3, 3.0)         # 距離センサ電圧
        accel = random.uniform(-1.0, 1.0)        # 加速度X軸

        distance = voltage_to_distance(voltage)
        input_value = 0
        if distance is not None:
            input_value = int(distance / 1.5)

        # トリガーロジック
        if not clk and accel > clk_th:
            clk = True
            clk_start = frame
        
        if clk:
            if frame > clk_start + clk_accept:
                clk = False
                clk_start = 0
                
            elif accel < -clk_th:
                strnum += "{}".format(input_value)
                print("clicked! ", input_value)
                clk = False
                clk_start = 0

        display_text = "distance: {} cm\naccel: {:.2f}".format(input_value, accel)
        text_obj.set_text(display_text)
        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(0.1)
        frame += 1

except KeyboardInterrupt:
    plt.close()
    print("Recorded values:", strnum)
