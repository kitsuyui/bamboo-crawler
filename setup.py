#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='bamboo-crawler',
    version='0.1.0',
    description='Hobby Crawler (yet)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Yui Kitsu',
    author_email='kitsuyui+github@kitsuyui.com',
    url='https://github.com/kitsuyui/bamboo-crawler',
    packages=find_packages('bamboo_crawler.*'),
    install_requires=[
        'boto3',
        'cssselect',
        'lxml',
        'requests',
        'PyYAML',
        'SQLAlchemy',
    ],
    extras_require={
        'dev': [
            'flake8',
            'nose',
            'pyformat',
            'moto[server]',
            'flake8',
            'mypy',
            'httpbin',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
    ],
    test_suite='tests',
    tests_require=['nose'],
    scripts=['bamboo_crawler/__main__.py'],
    entry_points={'console_scripts': [
        'bamboo = bamboo_crawler.cli:main',
    ]},
    license=open('./LICENSE', 'r').read(),
)
