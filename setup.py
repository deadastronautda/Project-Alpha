# setup.py
from setuptools import setup, find_packages

setup(
    name="project-alpha",
    version="0.1.0",
    packages=find_packages(where="."),
    package_dir={"": "."},
    include_package_data=True,
    install_requires=[
        # Здесь можно ничего не писать — зависимости и так в requirements.txt
    ],
)