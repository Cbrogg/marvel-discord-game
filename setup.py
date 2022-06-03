from setuptools import setup

setup(
    name='marvel_game',  # package name
    version='0.0.1',  # version
    description='A basic Marvel Game API',  # short description
    url='https://github.com/Cbrogg/marvel-discord-game',  # package URL
    install_requires=['uuid'],  # list of packages this package depends on.
    packages=['marvel_game'],  # List of module names that installing this package will provide.
)
