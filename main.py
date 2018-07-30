from typing import List, Tuple

import requests
from bs4 import BeautifulSoup

def fetch(url: str) -> str:
    """Get the content of a webpage."""
    res = requests.get(url)
    if res.status_code == 200:
        return res.content
    else:
        raise Exception('Couldn\'t reach {}'.format(url))

def parse(raw: str) -> List[Tuple[str, str]]:
    """Convert raw webpage of a problem content into HTML Tree and parse for tests.

    Args:
        raw: A string representing the web page.
    Returns:
        tests: A list of I/O of the tests to be used for a given problem page.
    """
    soup = BeautifulSoup(raw, 'html.parser')
    tests = soup.find(attrs={
        'class': 'sample-test'
    })

    inputs = list(map(lambda i: i.pre.get_text('\n'), tests.find_all(attrs={
        'class': 'input'
    })))

    outputs = list(map(lambda o: o.pre.get_text('\n'), tests.find_all(attrs={
        'class': 'output'
    })))
    return zip(inputs, outputs)


if __name__ == '__main__':
    for i, o in parse(fetch('https://codeforces.com/contest/1006/problem/A')):
        print(i, o)
        