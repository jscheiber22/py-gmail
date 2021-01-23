from setuptools import setup, find_packages

setup(
    name='py-gmail',
    version='0.1.2',
    description='Library for more easily utilizing the GMail API.',
    author='James Scheiber',
    author_email='jscheiber22@gmail.com',
    packages=find_packages(include=['pygmail', 'pygmail.*']),
    install_requires=[
        'google-api-python-client',
        'google-auth-httplib2',
        'google-auth-oauthlib',
        'beautifulsoup4',
    ]
)
