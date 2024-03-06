import setuptools

setuptools.setup(
    name="device-gammaipc",
    version="0.1.2",
    author="Ceki99",
    author_email="antonio.cerovic@gmail.com",
    description="A device to handle Gamma Vacuum Ion Pump Controller.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
