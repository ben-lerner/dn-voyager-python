import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voyager'))
from voyager_version import VERSION

setup(
    name='voyager-python',
    version=VERSION,
    url='https://github.com/datanitro/voyager-python',
    author='Victor Jakubiuk',
    author_email='victor@datanitro.com',
    maintainer='DataNitro',
    maintainer_email='support@datanitro.com',
    packages=['voyager'],
    license='MIT License',
    install_requires=['requests'],
    description='Python wrapper around DataNitro Voyager API',
    long_description=''' DataNitro Voyager allows you to push data directly to your users' Excel spreadsheets, without building custom add-ins or touching the Windows stack. Use this wrapper to programmatically push data from Pythonand manage users and their permissions. See http://voyager.datanitro.com for more details. '''
)
