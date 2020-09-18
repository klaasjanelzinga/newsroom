import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cron-app-newsrooom-klaasjanelzinga",
    version="0.0.1",
    author="KlaasJan Elzinga",
    author_email="klaasjanelzinga@me.com",
    description="Shared",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/klaasjanelzinga/newsrooom",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
