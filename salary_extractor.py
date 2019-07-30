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

APP_NAME = 'DVMNTutorialApp/1.0 (rk.inwork@gmail.com)'


def calculate_hh(limit_langs=None, pages_to_process=None):
    hh_renderer = AsciiTableStatisticRenderer('HH').render
    default_query = {'area': 1,
                     'date_from': (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
                     'date_to': datetime.datetime.now().strftime('%Y-%m-%d')}
    hhf = HHFetcher(default_query, hh_renderer, pages_to_process=pages_to_process)
    hhf.calculate_statistics_languages(TOP_LANGUAGES[:limit_langs])
    hhf.render_data()


def calculate_sj(limit_langs=None, pages_to_process=None):
    renderer = AsciiTableStatisticRenderer('SJ').render
    default_query = {'town': 4,
                     'date_published_from': int((datetime.datetime.now() - datetime.timedelta(days=30)).timestamp()),
                     'date_published_to': int(datetime.datetime.now().timestamp()),
                     'catalogues': 48,
                     }
    sjf = SJFetcher(default_query, renderer, search_parameter_name='keyword',
                    pages_to_process=pages_to_process)
    sjf.calculate_statistics_languages(TOP_LANGUAGES[:limit_langs])
    sjf.render_data()


if __name__ == '__main__':
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--demo", action="store_true", help="run in demo mode 5 langs and 3 pages")
    parser.add_argument("-l", "--lang-limit", type=int,
                        help="process only first X languages")
    parser.add_argument("-p", "--pages", type=int,
                        help="process only first X pages from response")

    args = parser.parse_args()

    if args.demo:
        limit_langs, pages_to_process = 5, 3
    else:
        limit_langs, pages_to_process = args.lang_limit, args.pages

    calculate_hh(limit_langs, pages_to_process)
    calculate_sj(limit_langs, pages_to_process and pages_to_process + 1)
