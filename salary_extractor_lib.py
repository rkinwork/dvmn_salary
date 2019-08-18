import os
from statistics import mean
import time
import itertools
from abc import ABCMeta
import abc

from terminaltables import AsciiTable
import requests

APP_NAME_DEFAULT = 'DVMNTutorialApp/1.0 (rk.inwork@gmail.com)'


class BaseStatisticRenderer(metaclass=ABCMeta):
    @abc.abstractmethod
    def render(self, statistics):
        pass


class AsciiTableStatisticRenderer(BaseStatisticRenderer):
    _default_table_headers = (('key', 'Язык программирования'),
                              ('vacancies_found', 'Вакансий найдено'),
                              ('average_salary', 'Средняя зарплата'),
                              ('vacancies_processed', 'Вакансий обработано'))

    def __init__(self, title, table_headers=None):
        self.title = title
        self.table_headers = table_headers or self._default_table_headers

    def adapt_statistics(self, statistics):
        result = []
        header = [human_title for key, human_title in self.table_headers]
        result.append(header)

        for key, values in statistics.items():
            row = []
            for title, human_title in self.table_headers:
                if title == 'key':
                    row.append(key)
                else:
                    row.append(values[title])
            result.append(row)

        return result

    def render(self, statistics):
        table = AsciiTable(self.adapt_statistics(statistics), self.title)
        print(table.table)


class StatisticsFetcher(metaclass=ABCMeta):
    _statistics = {}

    def __init__(self, api_config, search_parameter_name='text', pages_to_process=None):
        self.api_config = api_config
        self.search_parameter_name = search_parameter_name
        self.pages_to_process = pages_to_process

    def calculate_statistics_languages(self, languages):
        self._statistics = {}
        for language in languages:
            self.api_config[self.search_parameter_name] = f"программист {language}"
            self._statistics[language] = self.get_vacancy_statistics()
            time.sleep(0.5)

        print('\r', end='', flush=True)

    @property
    def raw_statistics(self):
        return self._statistics

    def get_vacancy_statistics(self):
        all_vacancies_salaries = []
        for vacancy in self.fetch_vacancies():
            all_vacancies_salaries.append(self.predict_rub_salary(vacancy))

        salaries = [salary for salary in all_vacancies_salaries if salary is not None]

        return {
            'vacancies_found': len(all_vacancies_salaries),
            'average_salary': int(mean(salaries or [0])),
            'vacancies_processed': len(salaries)
        }

    @abc.abstractmethod
    def fetch_vacancies(self):
        pass

    @staticmethod
    def predict_salary_common(salary_from, salary_to):
        if all((salary_from, salary_to)):
            return mean([salary_from, salary_to])
        if salary_to:
            return int(salary_to * .8)
        if salary_from:
            return int(salary_from * 1.2)

        return None

    @abc.abstractmethod
    def predict_rub_salary(self, vacancy):
        pass

    @property
    def statistics(self):
        return self._statistics


class HHFetcher(StatisticsFetcher):
    hh_host = 'https://api.hh.ru/'

    def __init__(self, api_config, app_name=None, search_parameter_name='text', **kwargs):
        self.headers = {
            'User-Agent': app_name or os.getenv('DVMN_APP_NAME', APP_NAME_DEFAULT)
        }
        super().__init__(api_config, search_parameter_name, **kwargs)

    def predict_rub_salary(self, vacancy):
        salary_description = vacancy.get('salary', None)
        if not salary_description:
            return None
        if salary_description['currency'] != 'RUR':
            return None

        return self.predict_salary_common(salary_description['from'], salary_description['to'])

    def fetch_vacancies(self):
        endpoint = os.path.join(self.hh_host, 'vacancies')
        for page in itertools.count():
            time.sleep(1)
            response = requests.get(endpoint, params={**self.api_config, 'page': page}, headers=self.headers)
            response.raise_for_status()
            response_dict = response.json()
            print("\r" + " " * 100, end="", flush=True)
            print(f"\r HH process page {response_dict['page']} from {response_dict['pages']}", end="", flush=True)

            yield from response_dict['items']

            # for demo purposes
            if self.pages_to_process:
                if page >= self.pages_to_process + 1:
                    break

            if page >= response_dict['pages']:
                break


class SJFetcher(StatisticsFetcher):
    host = 'https://api.superjob.ru/2.0/'

    def __init__(self, api_config, app_name=None, search_parameter_name='text', **kwargs):
        self.headers = {
            'User-Agent': app_name or os.getenv('DVMN_APP_NAME', APP_NAME_DEFAULT),
            'X-Api-App-Id': os.environ.get("SUPERJOB_API_ID")}

        super().__init__(api_config, search_parameter_name, **kwargs)

    def fetch_vacancies(self):
        endpoint = os.path.join(self.host, 'vacancies')
        for page in itertools.count():
            response = requests.get(endpoint, params={**self.api_config, 'page': page}, headers=self.headers)
            response.raise_for_status()

            response_dict = response.json()
            print("\r" + " "*100, end="", flush=True)
            print(f"\r SJ Process link '{self.api_config[self.search_parameter_name]}' page: {page + 1}", end="",
                  flush=True)
            time.sleep(1)
            yield from response_dict['objects']

            if self.pages_to_process:
                if page == self.pages_to_process:
                    break

            if not response_dict['more']:
                break

    def predict_rub_salary(self, vacancy):
        if vacancy['currency'] != 'rub':
            return None
        return self.predict_salary_common(vacancy['payment_from'], vacancy['payment_to'])
