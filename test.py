import matplotlib.pyplot as plt
import cv2
import numpy as np

# Пример данных
x = np.arange(1, 181)
y = 2 * x

# Создаем фигуру
fig, ax = plt.subplots(figsize=(6,4))  # можно задать размер
ax.plot(x, y, color='green', marker='o', markersize=3, linewidth=1)
ax.set_xlabel('Значения X')
ax.set_ylabel('Значения Y')
ax.set_title('График функции y = 2x')
ax.grid(True)

# Рисуем фигуру
fig.canvas.draw()

# Получаем изображение через буфер рендера
w, h = fig.canvas.get_width_height()
img = np.frombuffer(fig.canvas.renderer.buffer_rgba(), dtype=np.uint8)
img = img.reshape(h, w, 4)  # RGBA

# Конвертируем в BGR для OpenCV (отбрасываем альфу)
img_bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

cv2.imshow("graph", img_bgr)
cv2.waitKey(0)
cv2.destroyAllWindows()
