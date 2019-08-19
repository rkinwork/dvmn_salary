import datetime
import argparse

from dotenv import load_dotenv

from salary_extractor_lib import AsciiTableStatisticRenderer, SJFetcher, HHFetcher

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

MOSCOW_CITY_CODE = {
    'hh': 1,
    'sj': 4
}

SUPERJOB_PROGRAMMER_CATALOGUE = 48

STATISTICS_FOR_MOSCOW_QUERY_HH = {'area': MOSCOW_CITY_CODE['hh'],
                                  'date_from': (datetime.datetime.now() - datetime.timedelta(days=30)).strftime(
                                      '%Y-%m-%d'),
                                  'date_to': datetime.datetime.now().strftime('%Y-%m-%d')}

STATISTICS_FOR_MOSCOW_QUERY_SUPERJOB = {'town': MOSCOW_CITY_CODE['sj'],
                                        'date_published_from': int(
                                            (datetime.datetime.now() - datetime.timedelta(days=30)).timestamp()),
                                        'date_published_to': int(datetime.datetime.now().timestamp()),
                                        'catalogues': SUPERJOB_PROGRAMMER_CATALOGUE,
                                        }


def calculate_hh(limit_langs=None, pages_to_process=None, application_name=None):
    hhf = HHFetcher(STATISTICS_FOR_MOSCOW_QUERY_HH, app_name=application_name,
                    pages_to_process=pages_to_process)
    hhf.calculate_statistics_languages(TOP_LANGUAGES[:limit_langs])
    AsciiTableStatisticRenderer('HH').render(hhf.statistics)


def calculate_sj(limit_langs=None, pages_to_process=None, application_name=None):
    sjf = SJFetcher(STATISTICS_FOR_MOSCOW_QUERY_SUPERJOB, app_name=application_name,
                    search_parameter_name='keyword',
                    pages_to_process=pages_to_process)
    sjf.calculate_statistics_languages(TOP_LANGUAGES[:limit_langs])
    AsciiTableStatisticRenderer('SJ').render(sjf.statistics)


if __name__ == '__main__':
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--demo", action="store_true", help="run in demo mode 5 langs and 3 pages")
    parser.add_argument("-l", "--lang-limit", type=int,
                        help="process only first X languages")
    parser.add_argument("-p", "--pages", type=int,
                        help="process only first X pages from response")
    parser.add_argument("-n", "--name",
                        help="set name of the application")

    args = parser.parse_args()

    if args.demo:
        limit_langs, pages_to_process = 2, 2
    else:
        limit_langs, pages_to_process = args.lang_limit, args.pages

    calculate_hh(limit_langs, pages_to_process, args.name)
    calculate_sj(limit_langs, pages_to_process + 2, args.name)
