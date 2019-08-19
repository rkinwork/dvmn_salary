import os
from statistics import mean
import time
import itertools
from abc import ABCMeta
import abc

from terminaltables import AsciiTable
import requests

SUPERJOB_SEARCH_PARAMETER_NAME = 'keyword'

TOP_LANGUAGES = ['JavaScript',
                 'Python',
                 'Java',
                 'C++',
                 'C',
                 'PHP',
                 'C#',
                 'Shell',
                 'Go',
                 'TypeScript',
                 'Ruby',
                 'Objective-C',
                 'Swift',
                 'Kotlin',
                 '1С']




class AbstractBaseStatisticRenderer(metaclass=ABCMeta):
    @abc.abstractmethod
    def render(self, statistics):
        pass


class AsciiTableStatisticRenderer(AbstractBaseStatisticRenderer):
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


class BaseStatisticsFetcher(metaclass=ABCMeta):
    _statistics = {}

    def __init__(self, api_config, search_parameter_name='text', pages_to_process=None):
        self.api_config = api_config
        self.search_parameter_name = search_parameter_name
        self.pages_to_process = pages_to_process

    @property
    def statistics(self):
        return self._statistics

    def calculate_statistics_languages(self, languages):
        self._statistics = {}
        for language in languages:
            self.api_config[self.search_parameter_name] = f"программист {language}"
            self._statistics[language] = self._get_vacancy_statistics(self.api_config)
            time.sleep(0.5)

        print('\r', end='', flush=True)

    def _get_vacancy_statistics(self, api_config):
        all_vacancies_salaries = []
        for salary in self._fetch_vacancies_salaries(api_config):
            all_vacancies_salaries.append(self._predict_salary_common(*salary))

        salaries = [salary for salary in all_vacancies_salaries if salary is not None]

        return {
            'vacancies_found': len(all_vacancies_salaries),
            'average_salary': int(mean(salaries or [0])),
            'vacancies_processed': len(salaries)
        }

    @staticmethod
    def _get_application_name(app_name):
        if app_name:
            return app_name
        elif os.getenv('DVMN_APP_NAME'):
            return os.getenv('DVMN_APP_NAME')
        else:
            raise Exception("Name of the application hasn't been set")

    @staticmethod
    def _predict_salary_common(salary_from, salary_to):
        if all((salary_from, salary_to)):
            return mean([salary_from, salary_to])
        if salary_to:
            return int(salary_to * .8)
        if salary_from:
            return int(salary_from * 1.2)

        return None

    @abc.abstractmethod
    def _fetch_vacancies_salaries(self, api_config):
        """This method should return min and max salary, unknown value you should substitute with None"""
        raise NotImplementedError


class HHFetcher(BaseStatisticsFetcher):
    hh_host = 'https://api.hh.ru/'

    def __init__(self, api_config, app_name=None, **kwargs):
        self.headers = {
            'User-Agent': self._get_application_name(app_name)
        }
        super().__init__(api_config, **kwargs)

    def _fetch_vacancies_salaries(self, api_config):
        endpoint = os.path.join(self.hh_host, 'vacancies')
        for page in itertools.count():
            time.sleep(1)
            response = requests.get(endpoint, params={**api_config, 'page': page}, headers=self.headers)
            response.raise_for_status()
            response_dict = response.json()
            print("\r" + " " * 100, end="", flush=True)
            print(
                f"\r HH process page {response_dict['page']} from {response_dict['pages']} " +
                f"'{api_config[self.search_parameter_name]}'",
                end="", flush=True)

            for vacancy in response_dict['items']:
                salary_description = vacancy.get('salary', None)
                if not salary_description:
                    yield None, None
                    continue
                if salary_description['currency'] != 'RUR':
                    yield None, None
                    continue

                yield salary_description['from'], salary_description['to']

            # for demo purposes
            if self.pages_to_process:
                if page >= self.pages_to_process + 1:
                    break

            if page >= response_dict['pages']:
                break


class SJFetcher(BaseStatisticsFetcher):
    host = 'https://api.superjob.ru/2.0/'

    def __init__(self, api_config, app_name=None, **kwargs):
        self.headers = {
            'User-Agent': self._get_application_name(app_name),
            'X-Api-App-Id': os.environ.get("SUPERJOB_API_ID")}

        super().__init__(api_config, SUPERJOB_SEARCH_PARAMETER_NAME, **kwargs)

    def _fetch_vacancies_salaries(self, api_config):
        endpoint = os.path.join(self.host, 'vacancies')
        for page in itertools.count():
            response = requests.get(endpoint, params={**api_config, 'page': page}, headers=self.headers)
            response.raise_for_status()

            response_dict = response.json()
            print("\r" + " " * 100, end="", flush=True)
            print(f"\r SJ Process link '{api_config[self.search_parameter_name]}' page: {page + 1}", end="",
                  flush=True)
            time.sleep(1)
            for vacancy in response_dict['objects']:
                if vacancy['currency'] != 'rub':
                    yield None, None
                    continue
                yield vacancy['payment_from'], vacancy['payment_to']

            if self.pages_to_process:
                if page == self.pages_to_process:
                    break

            if not response_dict['more']:
                break
