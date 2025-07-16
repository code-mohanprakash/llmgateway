"""
Setup script for Model Bridge
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="model-bridge",
    version="1.0.0",
    author="WinCraft AI",
    author_email="contact@wincraftai.com",
    description="Enhanced Multi-Provider Model Bridge with Intelligent Routing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/code-mohanprakash/modelbridge",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "all": [
            "groq>=0.4.0",
            "together>=0.2.0", 
            "mistralai>=0.4.0",
            "cohere>=4.0.0",
            "huggingface-hub>=0.16.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "model-bridge=model_bridge.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "model_bridge": ["*.yaml", "*.yml"],
    },
)