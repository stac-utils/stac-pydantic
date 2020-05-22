from setuptools import setup, find_packages

with open("README.md") as f:
    desc = f.read()

setup(
    name="stac-pydantic",
    description="Pydantic data models for the STAC spec",
    long_description=desc,
    long_description_content_type="text/markdown",
    version="1.0.1",
    python_requires=">=3.6",
    classifiers=[
        'Intended Audience :: Developers',
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        'License :: OSI Approved :: MIT License',
    ],
    keywords="stac pydantic validation",
    author=u"Arturo Engineering",
    author_email="engineering@arturo.ai",
    url="https://github.com/arturo-ai/stac-pydantic",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "geojson-pydantic"
    ],
    tests_require=[
        "pytest",
        "pytest-cov",
        "requests",
        "shapely"
    ],
    setup_requires=['pytest-runner']
)
