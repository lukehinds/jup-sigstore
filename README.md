# Jupyter Sigstore Integration

This package provides a seamless integration between Jupyter notebooks (particularly Google Colab) and Sigstore for signing Hugging Face models and datasets. It enables keyless signing using Google OAuth2 authentication, making it easy to sign and verify machine learning artifacts within notebook environments.

## Features

- Keyless signing using Sigstore's Fulcio and Rekor services
- Google OAuth2 integration for authentication
- Automated signing of Hugging Face models and datasets
- Verification of signed artifacts
- Seamless integration with Google Colab

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Usage in Google Colab

1. Install the package and dependencies:
```python
!pip install sigstore transformers google-auth google-auth-oauthlib
!git clone https://github.com/example/jup-sigstore.git
!cd jup-sigstore && pip install -e .
```

2. Import and authenticate:
```python
from jup_sigstore import ModelSigner
from google.colab import auth
import asyncio

# Authenticate with Google
auth.authenticate_user()

# Initialize the signer
signer = ModelSigner()
```

3. Sign a model or tokenizer:
```python
from transformers import AutoTokenizer

async def sign_tokenizer():
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    
    # Sign the tokenizer files
    result = await signer.sign_model(
        tokenizer=tokenizer,
        save_path="./signed_tokenizer"
    )
    return result

# Run the signing process
result = await sign_tokenizer()
```

4. Verify signed files:
```python
async def verify_signed_files():
    verification = await signer.verify_model("./signed_tokenizer")
    return verification

# Run the verification process
verification = await verify_signed_files()
```

See `colab_example.ipynb` for a complete example.

## Security Considerations

- The package uses Sigstore's keyless signing capability, which provides a secure way to sign artifacts without managing private keys
- All signatures are recorded in Sigstore's Rekor transparency log for auditability
- OAuth2 tokens are handled securely and are not stored persistently
- The package is designed to work seamlessly with Google Colab's security model
