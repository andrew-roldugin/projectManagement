# Класс для хранения информации о режиме активности
class Mode:
    def __init__(self, duration: int, renewable_demand: list[int], nonrenewable_demand: list[int]):
        """
        Конструктор
        :param duration: продолжительность задачи в данном режиме
        :param renewable_demand: требуемые возобновляемые ресурсы
        :param nonrenewable_demand: требуемое кол-во исчерпаемых ресурсов
        """
        self.duration = duration
        self.renewable_demand = renewable_demand
        self.nonrenewable_demand = nonrenewable_demand


# Класс для хранения информации о задаче
class Activity:
    def __init__(self, successors: list[int], predecessors: list[int], modes):
        """
        :param successors: предшественники задачи
        :param predecessors: последующие задачи
        :param modes: альтернативные режимы выполнения задачи
        """
        self.successors = successors
        self.predecessors = predecessors
        self.modes = [Mode(**mode_data) for mode_data in modes]


# Класс для хранения общей информации о проекте
class Project:
    def __init__(self, horizon: int, renewable_resources: list[int], nonrenewable_resources: list[int],
                 activities):
        """
        Конструктор
        :param horizon: верхний предел времени
        :param renewable_resources: имеющееся количество неисчерпаемых ресурсов
        :param nonrenewable_resources: имеющееся количество исчерпаемых ресурсов
        :param activities: задачи
        """

        self.horizon = horizon
        self.renewable_resources = renewable_resources
        self.nonrenewable_resources = nonrenewable_resources
        self.activities = [Activity(**activity_data) for activity_data in activities]


class Solution:
    def __init__(self, activity_list: list[int], modes: dict[int, Mode]):
        self.activity_list = activity_list
        self.modes = modes

    def __eq__(self, other):
        return self.activity_list == other.activity_list \
               and self.modes == other.modes
