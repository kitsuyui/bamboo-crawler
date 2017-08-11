import json
import subprocess
import unittest

from bamboo_crawler.processors import HTTPCrawler


class TestHTTPCrawler(unittest.TestCase):
    def setUp(self):
        self.crawler = HTTPCrawler()

    def test_fetch(self):
        url = 'http://httpbin.org/ip'
        content = list(self.crawler.crawl(url=url))[0]
        json.loads(content)


class TestRecipeTask(unittest.TestCase):
    def run_recipe(self, taskname):
        c = subprocess.run([
            'python3', '-m',
            'bamboo_crawler',
            '-r', 'tests/recipe.yml',
            '-t', taskname],
            stdout=subprocess.PIPE)
        self.assertEqual(c.returncode, 0)
        return c

    def test_constant_inputter_test(self):
        c = self.run_recipe('constant_inputter_test')
        expect = b'abc1234'
        self.assertEqual(c.stdout, expect)

    def test_constant_inputter_with_metadata(self):
        c = self.run_recipe('constant_inputter_with_metadata')
        expect = b'abc1234'
        self.assertEqual(c.stdout, expect)

    def test_fetch_task(self):
        c = self.run_recipe('fetch_task')
        expect = b'User-agent: *\nDisallow: /deny\n'
        self.assertEqual(c.stdout, expect)

    def test_user_agent(self):
        c = self.run_recipe('user_agent')
        j = json.loads(c.stdout)
        expect = 'Testing User Agent'
        self.assertEqual(j['user-agent'], expect)
