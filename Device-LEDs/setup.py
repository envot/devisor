import setuptools

setuptools.setup(
    name="device-leds",
    version="0.0.2",
    author="Klemens Schueppert",
    author_email="schueppi@envot.io",
    description="A device handling multiple led connections.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
