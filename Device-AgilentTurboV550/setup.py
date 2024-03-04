import setuptools

setuptools.setup(
    name="device-agilentturbov550",
    version="0.1.0",
    author="Ceki99",
    author_email="antonio.cerovic@gmail.com",
    description="A device to handle Agilent TurboV 550 turbo and rough pump controller.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)