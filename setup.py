#!/usr/bin/env python

"""
distutils/setuptools install script.
"""

from setuptools import setup, find_packages

package_data = {'': ['*']}

requires = [
    'requests>=2.25.1',
    'pydantic>=1.8.2',
    'uplink>=0.0.2',
    'traceloop-sdk>=0.18.2,<=0.30',
    'typing-inspect>=0.9.0',
    'dataclasses-json>=0.6.7',
    'pyyaml>=6.0.1',
    'rich>=13.9.4',
    'openai>=1.57.2'
]

entry_points = {'console_scripts': ['honeyhive = honeyhive.cli.__main__:main']}

setup(
    name='honeyhive',
    version='0.2.25',
    description='The HoneyHive SDK for Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='HoneyHive',
    author_email="support@honeyhive.ai",
    scripts=[],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data=package_data,
    include_package_data=True,
    install_requires=requires,
    license="Apache License 2.0",
    python_requires=">= 3.7",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    extras_require={
        "dev":["pylint==2.16.2"],
        "langchain":["langchain>=0.0.251"],
        "llama_index":["llama_index>=0.8.13"],
        "all": ["langchain>=0.0.251", "llama_index>=0.8.13"]
    },
    project_urls={
        'Documentation': 'https://docs.honeyhive.ai/',
    },
    entry_points=entry_points,
)
