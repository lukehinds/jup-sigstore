from setuptools import setup, find_packages

setup(
    name="jup-sigstore",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sigstore>=1.0.0",
        "transformers>=4.30.0",
        "google-auth>=2.22.0",
        "google-auth-oauthlib>=1.0.0",
        "requests>=2.31.0",
        "cryptography>=41.0.0",
    ],
    # Explicitly declare these as optional to avoid conflicts with Colab
    extras_require={
        "jupyter": [
            "ipykernel>=5.5.6",
            "jupyter-client>=6.1.12",
            "jupyter>=1.0.0",
        ]
    },
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
