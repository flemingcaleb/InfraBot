from setuptools import setup

setup(
    name='InfraBot',
    packages=['InfraBot', 'DantesUpdater'],
    include_package_data=True
    install_requires=[
        'flask',
    ],
)
