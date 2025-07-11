from setuptools import setup, find_packages

setup(
    name="personalpasswords",
    version="1.1.0",
    author="TangoMan222",
    description="Generate personalized wordlists using OSINT data",
    packages=find_packages(),  # This auto-discovers the 'personalpasswords' package
    entry_points={
        'console_scripts': [
            'personalpasswords=personalpasswords.cli:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

