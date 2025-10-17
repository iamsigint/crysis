from setuptools import setup, find_packages
from src.core.version import version_manager

setup(
    name="crysis",
    version=version_manager.get_version(),
    description="Advanced Network Stress Testing Tool",
    author="Security Research Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "crysis=crysis.main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Topic :: Security",
    ],
)