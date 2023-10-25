from setuptools import find_packages, setup

setup(
    name='yoda_eus',
    version='1.9.0.dev',
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
        "test": ["pytest-flask==1.2.0", "pytest==7.2.1"],
    },
    install_requires=[
        "bcrypt==4.0.1",
        "email-validator==2.0.0",
        "Flask==2.3.2",
        "Flask-session2==1.3.1",
        "Flask-SQLAlchemy==3.0.3",
        "Flask-wtf==1.2.1",
        "psycopg2-binary==2.9.5",
        "requests==2.31.0",
        "Werkzeug==3.0.1"
    ],
)
