import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Настройки стиля
sns.set_style("whitegrid")

# ============================================
# ДАННЫЕ ИЗ ЗАДАНИЯ
# ============================================

# Создаем DataFrame как в задании
data = {
    'Ученик': ['Иванов И.И.', 'Петрова М.А.', 'Сидоров П.С.', 'Козлова А.В.',
               'Смирнов Д.И.', 'Новикова Е.П.', 'Фёдоров А.Н.',
               'Морозова К.С.', 'Соколов В.П.', 'Лебедева О.М.'],
    'Математика': [5, 4, 3, 5, 4, 5, 3, 4, 5, 3],
    'Русский': [4, 5, 4, 5, 3, 5, 3, 4, 4, 4],
    'Физика': [5, 4, 3, 5, 4, 4, 3, 4, 5, 3],
    'Информатика': [5, 5, 4, 5, 5, 5, 3, 4, 4, 4],
    'История': [4, 4, 3, 5, 3, 5, 3, 4, 5, 4]
}

df = pd.DataFrame(data)

# Предметы
subjects = ['Математика', 'Русский', 'Физика', 'Информатика', 'История']

# Расчет среднего балла
df['Средний_балл'] = df[subjects].mean(axis=1).round(2)

# ============================================
# 1. СРЕДНИЕ БАЛЛЫ ПО ПРЕДМЕТАМ
# ============================================

plt.figure(figsize=(10, 6))
subject_means = df[subjects].mean()
bars = plt.bar(subject_means.index, subject_means.values, color='skyblue', edgecolor='black')

plt.title('Средние баллы по предметам', fontsize=14, fontweight='bold')
plt.ylabel('Средний балл')
plt.ylim(0, 5)
plt.grid(axis='y', alpha=0.3)

# Добавляем значения на столбцы
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.05,
             f'{height:.2f}', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('1_средние_по_предметам.png')
plt.show()

# ============================================
# 2. РАСПРЕДЕЛЕНИЕ ОЦЕНОК
# ============================================

plt.figure(figsize=(8, 8))
all_grades = pd.concat([df[subject] for subject in subjects])
grade_counts = all_grades.value_counts().sort_index()

colors = ['#ff6b6b', '#ffd166', '#06d6a0', '#118ab2']
plt.pie(grade_counts.values, labels=[f'Оценка {g}' for g in grade_counts.index],
        autopct='%1.1f%%', colors=colors, startangle=90)
plt.title('Распределение оценок', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('2_распределение_оценок.png')
plt.show()

# ============================================
# 3. ТОП-10 УЧЕНИКОВ
# ============================================

plt.figure(figsize=(10, 6))
top10 = df.nlargest(10, 'Средний_балл')[['Ученик', 'Средний_балл']]
bars = plt.barh(range(len(top10)), top10['Средний_балл'].values, color='lightgreen', edgecolor='black')

plt.yticks(range(len(top10)), top10['Ученик'].values)
plt.xlabel('Средний балл')
plt.title('Топ-10 лучших учеников', fontsize=14, fontweight='bold')
plt.xlim(0, 5.2)
plt.grid(axis='x', alpha=0.3)

# Добавляем значения
for i, (bar, row) in enumerate(zip(bars, top10.iterrows())):
    plt.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
             f'{row[1]["Средний_балл"]:.2f}', va='center')

plt.tight_layout()
plt.savefig('3_топ10_учеников.png')
plt.show()

# ============================================
# 4. ТЕПЛОВАЯ КАРТА
# ============================================

plt.figure(figsize=(12, 8))
heatmap_data = df.set_index('Ученик')[subjects]
sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='RdYlGn', vmin=2, vmax=5,
            linewidths=0.5, linecolor='gray')
plt.title('Тепловая карта оценок', fontsize=14, fontweight='bold')
plt.ylabel('Ученик')
plt.xlabel('Предмет')

plt.tight_layout()
plt.savefig('4_тепловая_карта.png')
plt.show()

# ============================================
# 5. ДИНАМИКА ПО ЧЕТВЕРТЯМ
# ============================================

plt.figure(figsize=(8, 5))
quarters_data = pd.DataFrame({
    'Четверть': ['1 четв.', '2 четв.', '3 четв.', '4 четв.'],
    'Средний_балл': [3.9, 4.0, 4.2, 4.3]
})

plt.plot(quarters_data['Четверть'], quarters_data['Средний_балл'],
         marker='o', linewidth=2, markersize=8)
plt.ylabel('Средний балл класса')
plt.title('Динамика успеваемости по четвертям', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)

# Добавляем значения точек
for i, row in quarters_data.iterrows():
    plt.text(i, row['Средний_балл'] + 0.03, f"{row['Средний_балл']:.2f}", ha='center')

plt.tight_layout()
plt.savefig('5_динамика_четвертей.png')
plt.show()

# ============================================
# 6. BOX PLOT
# ============================================

plt.figure(figsize=(10, 6))
box_data = [df[subject] for subject in subjects]
plt.boxplot(box_data, labels=subjects, patch_artist=True)
plt.title('Разброс оценок по предметам (Box Plot)', fontsize=14, fontweight='bold')
plt.ylabel('Оценка')
plt.ylim(1.5, 5.5)
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('6_box_plot.png')
plt.show()

# ============================================
# 7. СТАТИСТИКА
# ============================================

print("\n" + "="*50)
print("СТАТИСТИКА КЛАССА")
print("="*50)

print(f"Всего учеников: {len(df)}")
print(f"Средний балл класса: {df['Средний_балл'].mean():.2f}")
print(f"Медиана: {df['Средний_балл'].median():.2f}")
print(f"Минимальный балл: {df['Средний_балл'].min():.2f}")
print(f"Максимальный балл: {df['Средний_балл'].max():.2f}")

print("\nСредние баллы по предметам:")
for subject in subjects:
    print(f"  {subject}: {df[subject].mean():.2f}")

print(f"\nЛучший ученик: {df.loc[df['Средний_балл'].idxmax(), 'Ученик']}")
print(f"Его средний балл: {df['Средний_балл'].max():.2f}")

# ============================================
# 8. СОХРАНЕНИЕ ВСЕГО ДАШБОРДА
# ============================================

print("\n✅ Все графики сохранены как PNG файлы:")
print("   1_средние_по_предметам.png")
print("   2_распределение_оценок.png")
print("   3_топ10_учеников.png")
print("   4_тепловая_карта.png")
print("   5_динамика_четвертей.png")
print("   6_box_plot.png")

# ============================================
# ДАШБОРД В ОДНОЙ КАРТИНКЕ (как в задании)
# ============================================

print("\n📊 Создаю полный дашборд...")

fig = plt.figure(figsize=(20, 12))
fig.suptitle('ДАШБОРД УСПЕВАЕМОСТИ КЛАССА', fontsize=20, fontweight='bold', y=0.98)

# 1. Средние баллы по предметам
ax1 = plt.subplot(3, 3, 1)
bars1 = ax1.bar(subject_means.index, subject_means.values, color='skyblue')
ax1.set_title('Средние баллы по предметам', fontsize=12, fontweight='bold')
ax1.set_ylabel('Средний балл')
ax1.set_ylim(0, 5)
ax1.tick_params(axis='x', rotation=45)
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05,
             f'{height:.2f}', ha='center', va='bottom', fontsize=9)

# 2. Распределение оценок
ax2 = plt.subplot(3, 3, 2)
ax2.pie(grade_counts.values, labels=[f'{g}' for g in grade_counts.index],
        autopct='%1.1f%%', colors=colors, startangle=90)
ax2.set_title('Распределение оценок', fontsize=12, fontweight='bold')

# 3. Топ-5 учеников
ax3 = plt.subplot(3, 3, 3)
top5 = df.nlargest(5, 'Средний_балл')[['Ученик', 'Средний_балл']]
bars3 = ax3.barh(range(len(top5)), top5['Средний_балл'].values, color='lightgreen')
ax3.set_yticks(range(len(top5)))
ax3.set_yticklabels(top5['Ученик'].values)
ax3.set_xlabel('Средний балл')
ax3.set_title('Топ-5 учеников', fontsize=12, fontweight='bold')
for i, v in enumerate(top5['Средний_балл'].values):
    ax3.text(v + 0.05, i, f'{v:.2f}', va='center', fontsize=9)

# 4. Тепловая карта
ax4 = plt.subplot(3, 3, (4, 6))
sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='RdYlGn', vmin=2, vmax=5,
            linewidths=0.5, linecolor='gray', ax=ax4, cbar_kws={'label': 'Оценка'})
ax4.set_title('Оценки учеников по предметам', fontsize=12, fontweight='bold')

# 5. Динамика по четвертям
ax5 = plt.subplot(3, 3, 7)
ax5.plot(quarters_data['Четверть'], quarters_data['Средний_балл'],
         marker='o', linewidth=2)
ax5.set_title('Динамика по четвертям', fontsize=12, fontweight='bold')
ax5.set_ylabel('Средний балл')
ax5.grid(True, alpha=0.3)

# 6. Box plot
ax6 = plt.subplot(3, 3, 8)
ax6.boxplot(box_data, labels=subjects)
ax6.set_title('Box plot по предметам', fontsize=12, fontweight='bold')
ax6.set_ylabel('Оценка')
ax6.tick_params(axis='x', rotation=45)

# 7. Статистика
ax7 = plt.subplot(3, 3, 9)
ax7.axis('off')
stats_text = f"""
Статистика класса:
Всего: {len(df)} учеников
Средний: {df['Средний_балл'].mean():.2f}
Медиана: {df['Средний_балл'].median():.2f}
Мин: {df['Средний_балл'].min():.2f}
Макс: {df['Средний_балл'].max():.2f}
Лучший: {df.loc[df['Средний_балл'].idxmax(), 'Ученик'][:15]}
Дата: {datetime.now().strftime('%d.%m.%Y')}
"""
ax7.text(0.05, 0.5, stats_text, fontsize=11, fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

plt.tight_layout()
plt.savefig('полный_дашборд.png', dpi=150, bbox_inches='tight')
print("✅ Полный дашборд сохранён в 'полный_дашборд.png'")
plt.show()

print("\n🎯 РАБОТА ВЫПОЛНЕНА!")