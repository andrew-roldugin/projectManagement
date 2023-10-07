import datetime as dt
import random as r
import matplotlib.pyplot as plt
import numpy as np

start_dt = dt.datetime.fromisoformat('2023-09-11')
runs = 1000  # кол-во прогонов
b = 100  # объем бэклога
h = [5, 11, 8, 7, 6, 8, 11]  # история выполненных задач за пред. спринты
sprints = []

for i in range(runs):
    P = b  # оставшиеся задачи в бэклоге
    k = r.triangular(low=1.2, mode=1.5, high=3)  # коэффициент расширения бэклога
    B = k * P  # итоговый объем бэклога с учетом незапланированной работы
    counter = 0
    while B > 0:
        counter += 1
        B -= r.choice(h)
    sprints.append(counter)

plt.hist(sprints, color='blue', edgecolor='black', bins=runs // 20)
plt.title(f'Гистограмма ({runs} прогонов)')
plt.xlabel('Кол-во спринтов')

q = 85
percentile = int(np.percentile(sprints, q))
print(f'min = {min(sprints)}, max = {max(sprints)}, 85-персентиль (numpy) = {percentile}')
idx = int((len(sprints) + 1) * q / 100)
sprints.sort()
print(f'Потребуется {sprints[idx]} спринтов')
end_dt = start_dt + dt.timedelta(weeks=2 * percentile)
print(f'Проект, вероятно, завершится к {end_dt.strftime("%d.%m.%Y")}')
plt.show()
