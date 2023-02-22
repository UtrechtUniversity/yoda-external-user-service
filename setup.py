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
    install_requires=[
        "bcrypt==4.0.1",
        "Flask==2.2.3",
        "Flask-session2==1.3.1",
        "Flask-SQLAlchemy==3.0.3",
        "Flask-wtf==1.1.1",
        "psycopg2-binary==2.9.5",
        "requests==2.28.2"
    ],
)
