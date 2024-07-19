from setuptools import setup, find_packages

setup(
    name='fastapi_templateapp',
    version='0.1.0',
    author='Sevbii',
    description='Library for ease of working with templates',
    url='https://github.com/yourusername/my_package',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'fastapi',
    ],
)
