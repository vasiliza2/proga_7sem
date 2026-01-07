import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt


# Целевая функция (для максимизации прибыли нужно минимизировать -P)
c = [-8000, -12000]

# Ограничения-неравенства A_ub @ x <= b_ub
A_ub = [
    [2, 3],
    [4, 6],
    [1, 2]
]
b_ub = [240, 480, 150]

# Границы переменных
bounds = [(0, None), (0, None)]

# Решение задачи
result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

# Вывод результатов
print("=== Задача оптимизации производства электроники ===")
print(f"Статус: {result.message}")

print(f"Оптимальное количество смартфонов: {result.x[0]}")
print(f"Оптимальное количество планшетов: {result.x[1]}")
print(f"Максимальная прибыль: {-result.fun}")

# Визуализация
fig, ax = plt.subplots(figsize=(10, 8))

# Диапазон значений
x1 = np.linspace(0, 150, 400)

# Границы ограничений
x2_constraint1 = (240 - 2*x1) / 3
x2_constraint3 = (150 - x1) / 2

# Построение прямых ограничений
ax.plot(x1, x2_constraint1, label='Процессорное время и Оперативная память')
ax.plot(x1, x2_constraint3, label='Аккумуляторы')

# Закрашивание допустимой области
vertices = np.array([
    [0, 0],
    [120, 0],
    [30, 60],
    [0, 75]
])

polygon = plt.Polygon(vertices, color='lightblue', alpha=0.7)
ax.add_patch(polygon)

# Оптимальная точка
ax.scatter(result.x[0], result.x[1], color='red', marker='o', s=100, label='Оптимальное решение')

# Линии уровня целевой функции
C = -result.fun  # максимальная прибыль
x2 = (C - 8000*x1) / 12000
ax.plot(x1, x2, label='Целевая функция')


ax.set_xlabel('x₁ (смартфоны)', fontsize=12)
ax.set_ylabel('x₂ (планшеты)', fontsize=12)
ax.set_title('Задача оптимизации производства: Геометрическое представление', fontsize=14)
ax.legend()
ax.grid(True, alpha=0.3)
plt.show()


# Новый запас процессорного времени
b_ub_new = [250, 480, 150]

result_new = linprog(
    c,
    A_ub=A_ub,
    b_ub=b_ub_new,
    bounds=bounds,
    method='highs'
)

print("=== Анализ чувствительности: +10 часов процессорного времени ===")
print(f"Оптимальное количество смартфонов: {result_new.x[0]}")
print(f"Оптимальное количество планшетов: {result_new.x[1]}")
print(f"Максимальная прибыль: {-result_new.fun}")