
import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt

# Целевая функция: минимизировать транспортные расходы
# Переменные: [x_11, x_12, x_13, x_21, x_22, x_23]
c = [8, 6, 10, 9, 7, 5]

# Ограничения-равенства A_eq @ x = b_eq
A_eq = [
    [1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1],
    [1, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 1, 0],
    [0, 0, 1, 0, 0, 1]
]

b_eq = [150, 250, 120, 180, 100]

# Границы переменных (все >= 0)
bounds = [(0, None), (0, None), (0, None),
          (0, None), (0, None), (0, None)]  

# Решение задачи
result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

# Вывод результатов
print("=== Транспортная задача снащения военных баз ===")
print(f"Статус: {result.message}")

print("\nОПТИМАЛЬНЫЙ ПЛАН ПЕРЕВОЗОК:")
routes = [
    "Склад 1 → База Альфа",
    "Склад 1 → База Бета",
    "Склад 1 → База Гамма",
    "Склад 2 → База Альфа",
    "Склад 2 → База Бета",
    "Склад 2 → База Гамма"
]

for i, route in enumerate(routes):
    amount = result.x[i]
    if amount > 0.001:
        cost = c[i] * amount
        print(f"  {route}: {amount:.1f} тонн ({cost:.0f} у.е.)")

print(f"\nМИНИМАЛЬНАЯ СТОИМОСТЬ ТРАНСПОРТИРОВКИ: {result.fun:,.0f} у.е.")

#  Визуализация
fig, ax = plt.subplots(figsize=(10, 6))

# Создаём простую таблицу
cell_text = []
for i in range(6):
    if result.x[i] > 0.001:
        cell_text.append([routes[i], f"{result.x[i]:.1f} т", f"{c[i]*result.x[i]:.0f} у.е."])

# Если есть перевозки, показываем таблицу
if cell_text:
    table = ax.table(cellText=cell_text,
                    colLabels=['Маршрут', 'Количество', 'Стоимость'],
                    cellLoc='center',
                    loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
else:
    ax.text(0.5, 0.5, "Нет перевозок", ha='center', va='center', fontsize=14)

ax.axis('off')
ax.set_title(f'Оптимальный план перевозок\nОбщая стоимость: {result.fun:,.0f} у.е.',
             fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('task2_exact.png', dpi=300)
plt.show()

print(f"\nГрафик сохранён в: task2_exact.png")

#3. ФУНКЦИЯ ЛАГРАНЖА
print("\n" + "="*60)
print("ФУНКЦИЯ ЛАГРАНЖА:")
print("="*60)
print("L(x, λ, ν) = Z(x) + λ₁*(x11+x12+x13-150) + λ₂*(x21+x22+x23-250)")
print("            + ν₁*(x11+x21-120) + ν₂*(x12+x22-180) + ν₃*(x13+x23-100)")
print("\nгде:")
print("λ₁, λ₂ - множители Лагранжа для ограничений по складам")
print("ν₁, ν₂, ν₃ - множители Лагранжа для ограничений по базам")