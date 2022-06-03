from setuptools import setup

setup(
    name='marvel_game',  # package name
    version='0.0.1',  # version
    description='A basic Marvel Game API',  # short description
    url='https://github.com/Cbrogg/marvel-discord-game',  # package URL
    python_requires='>=3.10.0',
    install_requires=[],  # list of packages this package depends on.
    packages=['game'],  # List of module names that installing this package will provide.
)
