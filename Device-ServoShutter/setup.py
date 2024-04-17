import setuptools

setuptools.setup(
    name="device-servoshutter",
    version="0.1.0",
    author="schueppi",
    author_email="schueppi@schueppi.com",
    description="A device to handle PWM connection to use a servo on two programable positions.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    dependencies = [
        "adafruit_servokit",
        ],
    python_requires='>=2.7',
)
