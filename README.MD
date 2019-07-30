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
foo@bar: dvmn_salary]$ EXPORT SJAPIID=secret_token
```

or

```console
foo@bar: dvmn_salary]$ echo SJAPIID=secret_token > .env
```


## How To Use

Take a round trip. Script process only 5 languages and 3 pages: 

```console
foo@bar: dvmn_salary]$ python3 salary_extractor.py -d
```


To get all possible statistics (this can take at least half an hour to all done):
```console
foo@bar: dvmn_salary]$ python3 salary_extractor.py
```

Custom limitation:

```console
foo@bar: dvmn_salary]$ python3 salary_extractor.py -l 4 -p 2
```


## API Reference

Not enough statistics?

Add you favorite searching job site. Just inherit `StatisticsFetcher` class
and implement abstract methods

```
class YourFavSiteFetcher(StatisticsFetcher):
    
    def predict_rub_salary(self, vacancy):
        """pass min and max vacancy salary to self.predict_salary_common method"""

    def fetch_vacancies(self):
        """implement vacancy iterator"""
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