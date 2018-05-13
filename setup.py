from setuptools import setup

setup(
    name='InfraBot',
    packages=['InfraBot', 'DantesUpdater', 'InfraManager', 'UserManager', 'Database'],
    include_package_data=True
    install_requires=[
        'flask',
        'flask_sqlalchemy',
        'slackclient'
    ],
)
