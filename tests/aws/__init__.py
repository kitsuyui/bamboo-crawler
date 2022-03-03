import json
import subprocess
import unittest


class TestAWSModules(unittest.TestCase):
    def setUp(self):
        s3 = subprocess.Popen(
            ["moto_server", "s3", "-p", "5000"], stderr=subprocess.PIPE
        )
        sqs = subprocess.Popen(
            ["moto_server", "sqs", "-p", "5001"], stderr=subprocess.PIPE
        )
        s3.stderr.readline()
        sqs.stderr.readline()
        self.s3 = s3
        self.sqs = sqs

    def tearDown(self):
        s3 = self.s3
        sqs = self.sqs
        s3.kill()
        sqs.kill()
        s3.stderr.close()
        sqs.stderr.close()
        s3.wait()
        sqs.wait()

    def run_recipe(self, taskname):
        c = subprocess.run(
            [
                "python3",
                "-m",
                "bamboo_crawler",
                "-r",
                "tests/aws/recipe.yml",
                "-e",
                "tests/aws/env.yml",
                "-t",
                taskname,
            ],
            stdout=subprocess.PIPE,
        )
        self.assertEqual(c.returncode, 0)
        return c

    def test_aws_inputter_and_outputter(self):
        self.run_recipe("aws_outputter")
        c = self.run_recipe("aws_inputter")
        j = json.loads(c.stdout)
        self.assertEqual(j["sampledata"], "ABCDEFGHIJKLMN")
