import json
from lab3.utility import ActivityListDecoder, ActivityListSampler


def find_best_mode(modes):
    """
    Найти наиболее оптимальный режим выполнения задачи
    :param modes: режимы выполнения задачи
    :return: оптимальный режим для задачи по правилу LPSRD
    """
    best_mode = None
    best_value = float('inf')
    for m in modes:
        # LPSRD - наименьшее произведение общего кол-ва ресурсов (невозобновляемых)
        # и времени выполнения задачи (в данном режиме)
        value = m['duration'] * sum(m['nonrenewable_demand'])
        if value < best_value:
            best_mode = m
            best_value = value
    return best_mode


def f(T: int,
      nonrenewable_demands: list[list[int]],
      nonrenewable_capacity: list[int]):
    """
    вычисление значения целевой функции
    :param T: предельное время завершения
    :param nonrenewable_demands: затраты исчерпаемых ресурсов
    :param nonrenewable_capacity: запасы неисчерпаемых ресурсов
    :return:
    """
    sft = 0
    for l, Nl in enumerate(nonrenewable_capacity):
        sum = 0
        for nj in nonrenewable_demands:
            sum += nj[l] - Nl
        sft += max(0, sum)

    if sft > 0:
        return T + sft
    else:
        return max(start_times)


with open('lab3/13.json') as json_data:
    data = json.load(json_data)

predecessors = []  # индексы предшествующих работ
durations = []  # продолжительность работы в выбранном режиме
renewable_demands = []  # требуемые затраты неисчерпаемых ресурсов.
nonrenewable_demands = []  # требуемые затраты исчерпаемых ресурсов.

for activity in data['activities']:
    predecessors.append(activity['predecessors'])
    mode = find_best_mode(activity['modes'])
    durations.append(mode['duration'])
    renewable_demands.append(mode['renewable_demand'])
    nonrenewable_demands.append(mode['nonrenewable_demand'])

renewable_capacity = data['renewable_resources']  # имеющееся количество неисчерпаемых ресурсов
nonrenewable_capacity = data['nonrenewable_resources']  # имеющееся количество исчерпаемых ресурсов
horizon = data['horizon']  # верхний предел времени

MAX_TABU_SIZE = 15  # максимальное кол-во элементов в списке
ITER_COUNT = 10000  # кол-во итераций

sampler = ActivityListSampler(predecessors)
decoder = ActivityListDecoder()
best_solution = None
best_value = float('inf')
tabu_list = []

for i in range(ITER_COUNT):
    random_activity_list = sampler.generate()
    start_times = decoder.decode(random_activity_list, durations, predecessors, renewable_demands, renewable_capacity)
    value = f(horizon, nonrenewable_demands, nonrenewable_capacity)

    if value < best_value and random_activity_list not in tabu_list:
        best_value = value
        best_solution = random_activity_list

    tabu_list.append(random_activity_list)
    if len(tabu_list) > MAX_TABU_SIZE:
        tabu_list.pop(0)

print("Составленное расписание:", best_solution)
