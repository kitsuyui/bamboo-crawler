import json
import os
import subprocess

import boto3
import pytest
import yaml


@pytest.fixture
def moto_environment():
    overwrite_envs = {
        "FLASK_ENV": "development",
        "WERKZEUG_RUN_MAIN": "true",
        "AWS_ACCESS_KEY_ID": "1234",
        "AWS_SECRET_ACCESS_KEY": "5678",
    }
    recovery_values = {name: os.environ.get(name) for name in overwrite_envs.keys()}
    os.environ.update(overwrite_envs)
    yield
    for k, v in recovery_values.items():
        if v is None:
            del os.environ[k]
        else:
            os.environ[k] = v


@pytest.fixture
def moto_server_s3(moto_environment):
    s3 = subprocess.Popen(["moto_server", "s3", "-p", "5000"], stderr=subprocess.PIPE)
    s3.stderr.readline()
    with open("tests/aws/env.yml") as f:
        y = yaml.safe_load(f.read())
    boto_s3 = boto3.resource("s3", **y["s3_config"])
    try:
        boto_s3.create_bucket(
            Bucket="sample-bucket",
            CreateBucketConfiguration={
                "LocationConstraint": y["s3_config"]["region_name"]
            },
        )
    except Exception:
        pass
    yield
    s3.kill()
    s3.stderr.close()
    s3.wait()


@pytest.fixture
def moto_server_sqs(moto_environment):
    sqs = subprocess.Popen(["moto_server", "sqs", "-p", "5001"], stderr=subprocess.PIPE)
    sqs.stderr.readline()
    with open("tests/aws/env.yml") as f:
        y = yaml.safe_load(f.read())
    boto_sqs = boto3.resource("sqs", **y["sqs_config"])
    try:
        boto_sqs.create_queue(QueueName="sample-queue")
    except Exception:
        pass
    yield
    sqs.kill()
    sqs.stderr.close()
    sqs.wait()


def run_recipe(taskname):
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
    return c


def test_aws_inputter_and_outputter(moto_server_s3, moto_server_sqs) -> None:
    outputter = run_recipe("aws_outputter")
    assert outputter.returncode == 0, "Outputter success"
    inputter = run_recipe("aws_inputter")
    assert inputter.returncode == 0, "Inputter success"
    j = json.loads(inputter.stdout)
    assert j["sampledata"] == "ABCDEFGHIJKLMN"
