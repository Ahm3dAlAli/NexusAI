from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="nexusai",
    version="0.1.0",
    author="Ahmed A. Ali, Vincenzo Fanizza",
    author_email="ahm3dalali@outlook.com, contact@vincenzofanizza.com",
    description="A research assistant for scientific paper analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ahm3dAlAli/NexusAI.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "nexusai=agent.main:main",
        ],
    },
)
