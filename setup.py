from setuptools import find_packages, setup

# https://packaging.python.org/tutorials/packaging-projects/

setup(
    name="fhblog",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/fhecorrea/flask-tutorial-blog",
    zip_safe=False,
    install_requires=[
        'flask',
        'pytest',
        'coverage',
        'wheel'
    ]
)
