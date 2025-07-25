from setuptools import setup, find_packages

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="spanish-ner",
    version="1.0.0",
    author="Spanish NER Team",
    description="Named Entity Recognition for Spanish with CLI and web API",
    long_description="Python application for Named Entity Recognition (NER) in Spanish using transformer models. Includes command-line interface and web API with FastAPI.",
    long_description_content_type="text/plain",
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
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ner-cli=src.cli:main",
            "ner-server=src.cli:server",
        ],
    },
    keywords="ner, nlp, spanish, named-entity-recognition, transformers, bert",
    project_urls={
        "Bug Reports": "https://github.com/drzippie/ner-service/issues",
        "Source": "https://github.com/drzippie/ner-service/",
    },
)