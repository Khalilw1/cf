import json
import os
import subprocess

from typing import List, Tuple

import requests
from bs4 import BeautifulSoup


def fetch(url: str) -> str:
    """Get the content of a webpage."""
    res = requests.get(url)
    if res.status_code == 200:
        return res.content
    raise Exception('Couldn\'t reach {}'.format(url))


def parse(raw: str) -> List[Tuple[str, str]]:
    """Convert raw webpage of a problem content into HTML Tree and parse for tests.

    Args:
        raw: A string representing the web page.
    Returns:
        A list of I/O of the tests to be used for a given problem page.
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
    return list(zip(inputs, outputs))


def store(contest: str, problem: str, io: List[Tuple[str, str]]):
    """Store the input and output of a contest problem on disk.
    The files are organized as numerical increments each in their own contest/problem directory.
    This allows us to keep them separated and track error in which test cases.

    Args:
        contest: A unique contest identifier
        problem: A problem in a contest
        io: A list of input output tuples for the problem at hand
    """
    directory = '{}/.cf-samples/{}/{}'.format(
        os.path.expanduser('~'), contest, problem)
    if not os.path.exists(directory):
        os.makedirs(directory)
    for i, (inp, out) in enumerate(io):
        with open('{}/{}.in'.format(directory, i), 'w') as f:
            f.write(inp)
        with open('{}/{}.out'.format(directory, i), 'w') as f:
            f.write(out)


def content(path: str) -> bytes:
    """Returns bytes content of a file."""
    with open(path, 'rb') as f:
        return f.read()


def test(contest: str, problem: str, binary: str) -> bool:
    """Test a binary against a const problem's IO

    The test spawns a subprocess and runs the binary giving it the input
    to the problem.

    Args:
        binary: An absolute path to the binary to test
    """
    path = '{}/.cf-samples/{}/{}'.format(
        os.path.expanduser('~'), contest, problem)
    directory = os.fsencode(path)

    actual = {}
    expected = {}
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith('.out'):
            print(filename)
            expected[filename.split('.')[0]] = (
                content('{}/{}'.format(path, filename)).decode('utf-8'))
        if not filename.endswith('.in'):
            continue
        print(filename)
        result = subprocess.run(binary, input=content(
            '{}/{}'.format(path, filename)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        actual[filename.split('.')[0]] = (result.stdout.decode('utf-8'))

    verdict = True
    for key in actual:
        # TODO(khalil): Introduce better output checker with possibility of custom checker in place.
        #               It could also take advantage of diff.
        cmp_width = min(len(actual[key]), len(expected[key]))
        verdict &= (actual[key][:cmp_width] == expected[key][:cmp_width])
    return verdict


def get_contests():
    response = json.loads(fetch('https://codeforces.com/api/contest.list'))
    status = response['status']
    if status != 'OK':
        print('An error occured while fetching the list of contests.')
        return
    contests = response['result']
    upcoming = filter(lambda contest: contest['phase'] == 'BEFORE', contests)
    
    contests.sort(key=lambda contest: contest['startTimeSeconds'], reverse=True)
    print(contests[:5])
    
if __name__ == '__main__':
    # EXPERIMENTAL: Sample usage
    # store('1006', 'A', parse(fetch('https://codeforces.com/contest/1006/problem/A')))
    # test('1006', 'A', '{}/{}'.format(os.path.expanduser('~'), 'dev/lab/a.out'))
    get_contests()