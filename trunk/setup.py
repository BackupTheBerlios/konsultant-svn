#!/usr/bin/python
import os, sys
from distutils.core import setup

version = '0.1'
description = 'Konsultant client management'
author = 'Joseph Rawson'
author_email = 'umeboshi@gregscomputerservice.com'
url = 'http://developer.berlios.de/projects/konsultant'
packages = ['konsultant']
subpacks = ['base', 'db', 'managers']
managers = ['client', 'ticket']

packages += ['konsultant.%s' % p for p in subpacks]
packages += ['konsultant.managers.%s' % p for p in managers]

package_dir = {'' : 'lib'}
scripts = ['konsultant']
setup(version=version, description=description, author=author,
      author_email=author_email, url=url, packages=packages,
      package_dir=package_dir, scripts=scripts)
