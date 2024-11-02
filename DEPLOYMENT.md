# Deployment and Testing Guide

## Step 1: Package Preparation

1. Create a GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/jup-sigstore.git
   git push -u origin main
   ```

2. Make the package pip-installable by ensuring these files are present:
   - setup.py (with pinned versions for Colab compatibility)
   - requirements.txt
   - README.md
   - jup_sigstore/* (package files)

## Step 2: Testing in Google Colab

1. Open Google Colab: https://colab.research.google.com

2. Create a new notebook and name it "JupSigstore_Test"

3. Install dependencies while maintaining Colab compatibility:
   ```python
   # Install core dependencies without their dependencies
   %pip install --no-deps sigstore transformers google-auth google-auth-oauthlib nest-asyncio

   # Force specific versions for Colab compatibility
   %pip install 'ipykernel==5.5.6' 'jupyter-client==6.1.12' 'jupyter-server<2.0.0'

   # Install the package without dependencies
   %pip install --no-deps git+https://github.com/yourusername/jup-sigstore.git
   ```

4. Restart the runtime (Runtime > Restart runtime)

5. Import required libraries and authenticate:
   ```python
   from jup_sigstore import ModelSigner
   from transformers import AutoTokenizer
   from google.colab import auth
   import nest_asyncio
   import asyncio
   import json

   # Apply nest_asyncio to allow nested event loops
   nest_asyncio.apply()

   # Authenticate with Google
   auth.authenticate_user()
   ```

6. Test the signing functionality:
   ```python
   # Initialize signer
   signer = ModelSigner()

   async def test_signing():
       # Load a tokenizer
       tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
       
       # Sign the tokenizer
       result = await signer.sign_model(
           tokenizer=tokenizer,
           save_path="./signed_tokenizer"
       )
       
       print("Signing result:", json.dumps(result, indent=2))
       
       # Verify the signed files
       verification = await signer.verify_model("./signed_tokenizer")
       
       print("\nVerification results:")
       for filename, result in verification:
           print(f"\n{filename}:")
           print(f"Verified: {result['success']}")
           if result['success']:
               print(f"Signed by: {result['signer']}")
               print(f"Timestamp: {result['timestamp']}")
           else:
               print(f"Error: {result['error']}")

   # Run the test
   await test_signing()
   ```

## Step 3: Troubleshooting

Common issues and solutions:

1. Dependency Conflicts:
   - Always use `--no-deps` when installing packages in Colab
   - Install specific versions of jupyter-related packages as shown above
   - Restart the runtime after installing packages

2. Authentication Issues:
   - Ensure you're logged into your Google account in Colab
   - Try running `auth.authenticate_user()` again if authentication fails

3. Runtime Issues:
   - If you get "RuntimeError: No event loop running":
     ```python
     import nest_asyncio
     nest_asyncio.apply()
     ```
   - If you get import errors, verify all dependencies are installed:
     ```python
     %pip list
     ```

## Step 4: Development Workflow

1. Make changes to the package locally

2. Test locally:
   ```bash
   pip install -e .
   python -m pytest tests/  # if you have tests
   ```

3. Push changes to GitHub:
   ```bash
   git add .
   git commit -m "Update description"
   git push
   ```

4. Test in Colab:
   - Follow the installation steps in Step 2
   - Remember to use `--no-deps` flag
   - Always restart the runtime after installation

## Step 5: Production Deployment

1. Register the package on PyPI:
   - Create an account on PyPI
   - Build the distribution:
     ```bash
     python -m build
     ```
   - Upload to PyPI:
     ```bash
     python -m twine upload dist/*
     ```

2. Update installation instructions to use pip with specific flags:
   ```python
   %pip install --no-deps jup-sigstore
   ```

## Step 6: Monitoring and Maintenance

1. Monitor GitHub issues for bug reports and feature requests

2. Set up GitHub Actions for automated testing:
   ```yaml
   # .github/workflows/test.yml
   name: Test
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - uses: actions/setup-python@v2
         - run: pip install -e .
         - run: pip install pytest
         - run: pytest tests/
   ```

3. Regular maintenance:
   - Keep dependencies updated
   - Test with new versions of dependencies
   - Monitor Sigstore API changes
   - Check Colab compatibility regularly

## Important Notes

1. Version Compatibility:
   - The package is specifically configured to work with Google Colab
   - Key version pins:
     - ipykernel==5.5.6
     - jupyter-client==6.1.12
     - jupyter-server<2.0.0

2. Installation in Different Environments:
   - For Colab: Use the installation instructions in Step 2
   - For local development: Can use regular pip install
   - For production: Consider providing both Colab and non-Colab installation instructions
