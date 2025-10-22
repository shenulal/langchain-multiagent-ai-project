"""
Setup script for LangChain Multi-Agent AI System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="langchain-multi-agent-ai",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A multi-agent AI system built with LangChain supporting voice and text interaction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/langchain-sample-project",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "langchain-ai=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.html", "*.css", "*.js", "*.md", "*.txt"],
    },
)
