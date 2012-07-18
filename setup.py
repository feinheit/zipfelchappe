#!/usr/bin/env python

from distutils.core import setup
import os
import setuplib

packages, package_data = setuplib.find_packages('zipfelchappe')

setup(name='zipfelchappe',
    version=__import__('zipfelchappe').__version__,
    description='Crowdfunding platform based on django and feincms.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    author='Stefan Reinhard',
    author_email='sr@feinheit.ch',
    url='http://github.com/feinheit/zipfelchappe/',
    license='BSD License',
    platforms=['OS Independent'],
    packages=packages,
    package_data=package_data,
    classifiers=[
        'Development Status :: Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
	'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
    ],
)
