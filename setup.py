from setuptools import setup, find_packages

setup(
    name="stac-pydantic",
    version="0.0.1",
    python_requires=">=3",
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="",
    author=u"Arturo Engineering",
    author_email="engineering@arturo.ai",
    url="https://github.com/arturo-ai/stac-pydantic",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "pydantic",
        "geojson"
    ],
    tests_require=[
        "pytest",
        "pytest-cov",
        "requests",
        "shapely"
    ],
    setup_requires=['pytest-runner']
)
