from setuptools import find_packages, setup

setup(
    name='yoda_eus',
    version='2.0.0.dev',
    author='Utrecht University - ITS/RDMS department',
    author_email='yoda@uu.nl',
    url='https://uu.nl/rdm',
    description="Yoda External User Service",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    license='GPL3',
    entry_points={
    },
    extras_require={
        "test": ["pytest-flask==1.3.0", "pytest==8.0.1"],
    },
    install_requires=[
        "bcrypt==4.0.1",
        "email-validator==2.0.0",
        "Flask==3.1.1",
        "flask-session==0.8.0",
        "Flask-SQLAlchemy==3.1.1",
        "Flask-WTF==1.2.2",
        "psycopg2-binary==2.9.10",
        "requests==2.32.4",
        "Werkzeug==3.1.4"
    ],
)
