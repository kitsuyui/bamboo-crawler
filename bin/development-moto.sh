#!/usr/bin/env bash
moto_server s3 -p 5000 &
moto_server sqs -p 5001 &
