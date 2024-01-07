import copy
import json
import random
from typing import Generator, Any

from domain import Project, Mode, Solution
from utility import ActivityListSampler


def is_valid_swap(activity1: int, activity2: int, activities: any) -> bool:
    """
    Функция проверки, что после обмена предшественники и преемники сохраняют верный порядок
    :param activity1: ссылка на 1 задачу
    :param activity2: ссылка на 2 задачу
    :param activities: список задач
    :return: True, если обмен допустим, иначе - False
    """

    for successor in activities[activity1]['successors']:
        if successor == activity2:
            return False  # Нельзя обменивать предшественника со своим преемником
    for predecessor in activities[activity1]['predecessors']:
        if predecessor == activity2:
            return False  # Нельзя обменивать преемника со своим предшественником
    return True  # Обмен допустим


# Функция для расчёта длительности проекта на основе текущего решения
def calculate_project_duration(solution: Solution):
    duration = sum(solution.modes[a].duration for a in solution.activity_list)
    return duration


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
        value = m.duration * sum(m.nonrenewable_demand)
        if value < best_value:
            best_mode = m
            best_value = value
    return best_mode


def calculate_resource_error(schedule: list[int], modes: dict[int, Mode], nonrenewable_resources: list[int]):
    """
    Функция, накладывающая штраф за превышение лимита исчерпаемых ресурсов
    :param schedule: решение - некоторое составленное расписание
    :param modes: выбранные режимы выполнения задач
    :param nonrenewable_resources: запасы исчерпаемых ресурсов
    :return: сумма ошибок по всем видам исчерпаемых ресурсов
    """
    SFT = 0
    # цикл по видам исчерпаемых ресурсов
    for l, Nl in enumerate(nonrenewable_resources):
        sum = 0
        # цикл по работам 
        for j in schedule:
            n_jml = modes[j].nonrenewable_demand[l]  # затраты ресурса типа l для работы j в режиме m
            sum += n_jml
        SFT += max(0, sum - Nl)
    return SFT


def get_mode(activity: int, proj: Project) -> Generator[Mode, Any, None]:
    for m in proj.activities[activity].modes:
        yield m


# Оператор генерации нового решения в окрестности
def generate_neighbor(current_solution: Solution, project: Project, use_random=True) -> Generator[
    Solution, Any, None]:
    activity_list = current_solution.activity_list
    for i in range(1, len(activity_list) - 1):
        j = i + 1
        if not is_valid_swap(activity_list[i], activity_list[j], activities):
            continue

        neighbor = copy.deepcopy(activity_list)
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]  # обмен двух элементов

        if use_random:
            modes_combination = {activity: random.choice(project.activities[activity].modes) for activity in neighbor}
            yield Solution(neighbor, modes_combination)
        else:
            for m in get_mode(i, project):
                modes_combination = current_solution.modes
                modes_combination[i] = m
                yield Solution(neighbor, modes_combination)


# получить случайное начальное решение
def get_initial_solution(p: Project) -> Solution:
    sampler = ActivityListSampler([activity.predecessors for activity in p.activities])
    random_activity_list = sampler.generate()
    # пусть каждая задача выполняется в первом режиме
    # modes = {idx: activity.modes[0] for idx, activity in enumerate(p.activities)}
    modes = {idx: find_best_mode(activity.modes) for idx, activity in enumerate(p.activities)}
    return Solution(random_activity_list, modes)


# вычисление значения целевой функции
def f(solution: Solution, nonrenewable_resources: list[int], horizon: int):
    resource_error = calculate_resource_error(solution.activity_list, solution.modes, nonrenewable_resources)
    if resource_error > 0:
        # Если текущее расписание не удовлетворяет лимитам ресурсов, штрафуем его
        fitness_value = horizon + resource_error
    else:
        # Иначе целевая функция равна продолжительности проекта
        fitness_value = calculate_project_duration(solution)
    return fitness_value


# Tabu Search алгоритм
def tabu_search(p: Project, max_iterations: int = 100, max_tabu_list_size: int = 10):
    current_solution = get_initial_solution(p)  # Начальное решение
    best_candidate = copy.deepcopy(current_solution)
    best_cost = f(best_candidate, p.nonrenewable_resources, p.horizon)
    tabu_list = []

    for iteration in range(max_iterations):
        best_candidate_cost = f(best_candidate, p.nonrenewable_resources, p.horizon)
        for candidate in generate_neighbor(current_solution, p ,False):
            value = f(candidate, p.nonrenewable_resources, p.horizon)

            if candidate not in tabu_list and value < best_candidate_cost:
                best_candidate = candidate
                best_candidate_cost = value

        current_cost = f(best_candidate, p.nonrenewable_resources, p.horizon)
        # Обновление лучшего решения
        if current_cost < best_cost:
            current_solution = copy.deepcopy(best_candidate)
            best_cost = current_cost

        # Обновление табу-списка
        tabu_list.append(best_candidate)
        if len(tabu_list) > max_tabu_list_size:
            tabu_list.pop(0)

    return current_solution, best_cost


MAX_TABU_SIZE = 15  # максимальное кол-во элементов в списке
ITER_COUNT = 15000  # кол-во итераций

if __name__ == '__main__':
    with open('13.json') as json_data:
        data = json.load(json_data)

    renewable_capacity = data['renewable_resources']  # имеющееся количество неисчерпаемых ресурсов
    nonrenewable_capacity = data['nonrenewable_resources']  # имеющееся количество исчерпаемых ресурсов
    horizon = data['horizon']  # верхний предел времени
    activities = data['activities']

    p = Project(activities=activities,
                renewable_resources=renewable_capacity,
                nonrenewable_resources=nonrenewable_capacity,
                horizon=horizon)

    # Запуск алгоритма Tabu Search
    best_solution, best_cost = tabu_search(p, max_tabu_list_size=MAX_TABU_SIZE, max_iterations=ITER_COUNT)
    print("Составленное расписание:", best_solution.activity_list)
    print("Лучшее значение целевой функции (длительность проекта):", best_cost)
