from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='marvel_game',  # package name
    version='0.0.3',  # version
    description='A basic Marvel Game API',  # short description
    url='https://github.com/Cbrogg/marvel-discord-game',  # package URL
    python_requires='>=3.10.0',
    install_requires=requirements,  # list of packages this package depends on.
    packages=['game'],  # List of module names that installing this package will provide.
)
