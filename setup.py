import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'GPSReader',
    version = '0.1.1',
    description = 'Give one access to different NMEA information of a GPS receiver',
#    long_description = ' ',
    license = 'LGPLv3',    
    author = 'Christoph Fluegel',
    author_email = 'pypi@digitalmonk.de',
    url = '',
    packages= ['GPSReader'],
    classifiers = [
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
      'Operating System :: POSIX :: Linux'
      'Operating System :: Microsoft :: Windows',
      'Environment :: Win32 (MS Windows)',
      'Environment :: Console',
      'Intended Audience :: Information Technology',
      'Intended Audience :: Science/Research',
      'Intended Audience :: Developers',
      'Natural Language :: English',
      'Operating System :: Unix',
      'Operating System :: POSIX :: Linux',
      'Operating System :: Microsoft :: Windows',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Programming Language :: Python :: 2.6',
      'Programming Language :: Python :: 2.7',
      'Topic :: Scientific/Engineering',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'Topic :: System :: Hardware'
      ]
)

