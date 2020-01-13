from setuptools import setup, find_packages
import os.path as osp

import catwalk


setup(
    name="catwalk",
    version=catwalk.__version__,
    packages=find_packages(),
    package_data={"catwalk": ["templates/*.j2"]},
    entry_points={
        "console_scripts": [
            "catwalk = catwalk.__main__:main"
        ]
    },
    install_requires=[
        "cryptography",
        "docker",
        "Flask",
        "gunicorn",
        "gevent",
        "PyYAML",
        "schema"]
)
