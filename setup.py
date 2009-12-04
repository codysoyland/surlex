try:
    from setuptools import setup
    installer = 'setuptools'
except ImportError:
    from distutils.core import setup
    installer = 'distutils'

options = dict(
    name = 'surlex',
    version = '0.1.1',
    description = 'Simple URL expression translator: alternative to regular expressions for URL pattern matching and data extraction.',
    url = 'http://github.com/codysoyland/surlex/tree/master',
    download_url = 'http://cloud.github.com/downloads/codysoyland/surlex/surlex-0.1.1.tar.gz',
    packages = ['surlex'],
    package_dir = {'surlex': 'src/surlex'},
    scripts = ['scripts/surlex2regex.py'],
    author = 'Cody Soyland',
    author_email = 'codysoyland@gmail.com',
    license = 'BSD',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)

if installer == 'setuptools':
    options['test_suite'] = 'tests'

setup(**options)
