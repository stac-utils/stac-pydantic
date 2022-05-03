from setuptools import find_packages, setup

with open("README.md") as f:
    desc = f.read()

extras = {
    "dev": [
        "arrow",
        "pytest",
        "pytest-cov",
        "requests",
        "shapely",
        "dictdiffer",
        "jsonschema",
    ],
}

setup(
    name="stac-pydantic",
    description="Pydantic data models for the STAC spec",
    long_description=desc,
    long_description_content_type="text/markdown",
    version="2.0.3",
    python_requires=">=3.7",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="stac pydantic validation",
    author="Arturo Engineering",
    author_email="engineering@arturo.ai",
    url="https://github.com/stac-utils/stac-pydantic",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    install_requires=["click", "pydantic>=1.6", "geojson-pydantic"],
    tests_require=extras["dev"],
    setup_requires=["pytest-runner"],
    entry_points={"console_scripts": ["stac-pydantic=stac_pydantic.scripts.cli:app"]},
    extras_require=extras,
    package_data={"stac_pydantic": ["*.typed"]},
)
