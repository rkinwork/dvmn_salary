## Synopsis

This is study project from [dvmn.org](http://dvmn.org).

## Motivation

This utility is intended for digital HR specialist, programmers, analysts and who interested in programmers salaries
Script get salaries statistics from two popular russian job searching services [HH.ru](https://hh.ru) and [Superjob](http://superjob.ru) via API

## Installation

This project is working on `python => 3.6`

Before execute script install packages from ```requirements.txt```

```pip3 install -r requirements.txt``` 

To get data from SuperJob you should get API key from [api.superjob.ru](https://api.superjob.ru/) and
assign it to environment variable or add to `.env` file

```console
foo@bar: dvmn_salary] EXPORT SUPERJOB_API_ID=secret_token
```

or

```console
foo@bar: dvmn_salary] echo SUPERJOB_API_ID=secret_token > .env
```

Please set the name of the application:

```console
foo@bar: dvmn_salary] EXPORT DVMN_APP_NAME='My Super Fancy Name'
```


## How To Use

Take a round trip. Script process only 5 languages and 3 pages: 

```console
foo@bar: dvmn_salary] python3 salary_extractor.py -d
```


To get all possible statistics (this can take at least half an hour to all done):
```console
foo@bar: dvmn_salary] python3 salary_extractor.py
```

Custom limitation:

```console
foo@bar: dvmn_salary] python3 salary_extractor.py -l 4 -p 2
```


## API Reference

Not enough statistics?

Add you favorite searching job site. Just implement abstract method `_fetch_vacancies_salaries` 
from `BaseStatisticsFetcher`

This method should return tuple with min and max salaries - unknown values we should substitute with `None`

```python
import itertools
import time
import os
import datetime

import requests
from salary_extractor_lib import BaseStatisticsFetcher, TOP_LANGUAGES



class YourFavSiteFetcher(BaseStatisticsFetcher):
    host = 'https://api.supersite.ru/2.0/'

    def __init__(self, api_config, app_name=None, **kwargs):
        # add headers if you want
        self.headers = {
            'User-Agent': self._get_application_name(app_name)
        }

        super().__init__(api_config, **kwargs)


def _fetch_vacancies_salaries(self, api_config):
    endpoint = os.path.join(self.host, 'vacancies')
    for page in itertools.count():
        response = requests.get(endpoint, params={**api_config, 'page': page}, headers=self.headers)
        response.raise_for_status()

        response_dict = response.json()
        time.sleep(1)
        for vacancy in response_dict['objects']:
            if vacancy['currency'] != 'rub':
                yield None, None
                continue
            yield vacancy['payment_from'], vacancy['payment_to']

        # Don't forget to add stoper
        if self.pages_to_process:
            if page == self.pages_to_process:
                break

        if not response_dict['more']:
            break

if __name__ == '__main__':
    query = {'town': 'moscow',
             'date_published_from': int((datetime.datetime.now() - datetime.timedelta(days=30)).timestamp()),
             'date_published_to': int(datetime.datetime.now().timestamp())
            }
    yff = YourFavSiteFetcher(query, app_name='my super app name', pages_to_process=2)
    print(yff.calculate_statistics_languages(TOP_LANGUAGES[:2]).statistics)



```

## License

MIT License

Copyright (c) 2019 Roman Kazakov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.