from setuptools import setup

setup(
    author='DinoCloud',
    author_email='info@dinocloudconsulting.com',
    name='flask_dino_utils',
    description='Flask utils package to use it among with Flask-Classy and marshmallow',
    url='http://github.com/dinocloud/flask-dino-utils',
    version='0.1.15',
    license='MIT',
    packages=['flask_dino_utils'],
    install_requires=[
        'Flask==0.11.1',
        'Flask-Classy==0.6.8',
        'marshmallow',
        'Flask-SQLAlchemy==1.0',
        'SQLAlchemy==1.0.16',
        'Werkzeug==0.11.11'
    ]
)
