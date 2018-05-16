from setuptools import setup, find_packages

with open('requirements.txt') as fp:
    install_requires = fp.read()

setup(
    name='pascalvoc_to_image',
    version='1.0',
    url='http://www.github.com/jdreg95/pascalvoc-to-image',
    author='Jori Regter',
    author_email='joriregter@gmail.com',
    license='MIT',
    packages=find_packages(),
    scripts=['bin/pascalvoc-to-image'],
    install_requires=install_requires
)