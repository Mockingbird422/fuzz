from setuptools import setup, find_packages
import re


def get_requirements():
    requirements = []
    with open('requirements.txt') as f:
        for line in f:
            requirement = re.sub('#.*', '', line).strip()
            if requirement:
                requirements.append(requirement)
    return requirements


setup(
    name="fuzz",
    version="0.1",
    packages=find_packages(),
    package_data={"fuzz": ["data/*"]},
    install_requires=get_requirements(),
    entry_points='''
        [console_scripts]
        fuzz=fuzz.__main__:cli
    '''
)
