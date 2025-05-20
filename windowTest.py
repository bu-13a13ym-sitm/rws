import matplotlib.pyplot as plt
import time
import random  # 実際はセンサーデータ取得部分に置き換え

def voltage_to_distance(voltage):
    if voltage <= 0.42:
        return None  # 無効値扱い
    return 27.86 / (voltage - 0.42)

plt.ion()
fig, ax = plt.subplots()
text_obj = ax.text(0.5, 0.5, '', fontsize=30, ha='center', va='center')
ax.axis('off')  # 軸は非表示

try:
    while True:
        # ここを実際の電圧読み取りに置き換える
        voltage = random.uniform(0.3, 3.0)
        distance = voltage_to_distance(voltage)
        
        if distance is None:
            display_text = f"out of distance\nvoltage: {voltage:.2f} V"
        else:
            display_text = f"distance: {distance:.2f} cm\nvoltage: {voltage:.2f} V"

        text_obj.set_text(display_text)
        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(0.5)
except KeyboardInterrupt:
    plt.close()