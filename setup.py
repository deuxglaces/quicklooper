import pathlib
from setuptools import setup, find_packages

PROJECT_DIR = pathlib.Path(__file__).parent

README = (PROJECT_DIR / 'README.md').read_text()

setup(
    name='quicklooper',
    version='1.0.0',
    description='Simple polling-style loop running in separate thread',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/deuxglaces/quicklooper',
    author='Deux Glaces',
    license='MIT',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
)
