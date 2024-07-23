from setuptools import setup, find_packages

setup(
    name='fastapi_templateapp',
    version='0.1.4',
    author='Sevbii',
    description='Library for ease of working with templates',
    url='https://github.com/comasqw/fastapi_templateapp',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'fastapi',
        'apscheduler'
    ],
    package_data={
        'fastapi_templateapp': ['templates/**/*.html'],
    },
    include_package_data=True,
)
