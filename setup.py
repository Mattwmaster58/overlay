from setuptools import setup

setup(
    name='overlay',
    version='0.1',
    py_modules=['overlay'],
    install_requires=open("requirements.txt").read().split("\n"),
    entry_points={
    'console_scripts': [
        'overlay = overlay.main:main',
    ]}
)


