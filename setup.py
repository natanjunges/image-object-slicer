from setuptools import setup, find_packages

with open('requirements.txt') as fp:
    install_requires = fp.read()

setup(
    name='pascalvoc_to_image',
    version='1.1',
    url='https://www.github.com/natanjunges/pascalvoc-to-image',
    author='Natan Junges',
    author_email='natanajunges@gmail.com',
    license='GPLv3+',
    packages=find_packages(),
    scripts=['bin/pascalvoc-to-image'],
    install_requires=install_requires
)
