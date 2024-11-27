from setuptools import setup, find_packages

setup(
    name="project-awareness",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pyyaml>=6.0.1",
        "matplotlib>=3.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
        ],
    },
    python_requires=">=3.7",
    author="OpenHands",
    author_email="openhands@all-hands.dev",
    description="A toolkit for analyzing and tracking open source project visibility",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/openhands/project-awareness",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)