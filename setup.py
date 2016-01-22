from setuptools import setup, find_packages

version = "0.0.0"

long_description = ""
try:
    long_description=file('README.md').read()
except Exception:
    pass

license = ""
try:
    license=file('LICENSE').read()
except Exception:
    pass


setup(
    name = 'python-livecodingtv',
    version = version,
    description = '''\
This package wraps the Livecoding.tv REST API in Python.
''',
    author = 'Pablo Saavedra',
    author_email = 'saavedra.pablo@gmail.com',
    url = 'http://github.com/psaavedra/python-livecodingtv',
    packages = find_packages(),
    package_data={
    },
    scripts=[
    ],
    zip_safe=False,
    install_requires=[
        "requests",
    ],
    data_files=[
        ('/usr/share/doc/python-livecodingtv/examples', [
            'examples/lctv-remote-app',
            'examples/lctv-remote-app-example.cfg',
        ]),
    #     ('/etc/init.d', ['init-script'])
    ],

    download_url= 'https://github.com/psaavedra/python-livecodingtv/zipball/master',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description=long_description,
    license=license,
    keywords = "python lctv livecodingtv livecoding api rest ouath2",
)
