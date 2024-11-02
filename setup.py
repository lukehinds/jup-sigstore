from setuptools import setup, find_packages

setup(
    name="jup-sigstore",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sigstore",
        "transformers",
        "google-auth",
        "google-auth-oauthlib",
        "jupyter",
        "requests",
        "cryptography",
    ],
    author="Cline",
    author_email="cline@example.com",
    description="A tool for signing Hugging Face models using Sigstore in Jupyter notebooks",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/jup-sigstore",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
