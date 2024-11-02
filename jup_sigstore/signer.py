import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from sigstore.sign import SigningContext
from sigstore.verify import Verifier
from transformers import PreTrainedModel, PreTrainedTokenizer

class ModelSigner:
    """Handles signing of Hugging Face models using Sigstore's keyless signing."""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """Initialize the ModelSigner.
        
        Args:
            credentials_path: Path to Google service account credentials JSON file.
                            If None, will attempt to use default credentials.
        """
        self.credentials = None
        if credentials_path and os.path.exists(credentials_path):
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )

    def _get_metadata(self, 
                     model: Optional[PreTrainedModel] = None, 
                     tokenizer: Optional[PreTrainedTokenizer] = None) -> Dict[str, Any]:
        """Extract relevant metadata from model and/or tokenizer.
        
        Args:
            model: Optional Hugging Face model to extract metadata from
            tokenizer: Optional tokenizer to extract metadata from
            
        Returns:
            Dict containing metadata
        """
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if model:
            metadata.update({
                "model_type": model.config.model_type,
                "model_name": model.name_or_path,
                "architecture": str(model.config),
            })
            
        if tokenizer:
            metadata.update({
                "tokenizer_name": tokenizer.name_or_path,
                "vocab_size": tokenizer.vocab_size,
            })
            
        return metadata

    async def sign_model(
        self,
        model: Optional[PreTrainedModel] = None,
        tokenizer: Optional[PreTrainedTokenizer] = None,
        save_path: str = "./signed_model"
    ) -> Dict[str, Any]:
        """Sign a Hugging Face model and/or tokenizer.
        
        Args:
            model: Optional model to sign
            tokenizer: Optional tokenizer to sign
            save_path: Path to save the signed artifacts
            
        Returns:
            Dict containing signing information and verification materials
        """
        if not model and not tokenizer:
            raise ValueError("At least one of model or tokenizer must be provided")
            
        # Extract metadata
        metadata = self._get_metadata(model, tokenizer)
        
        # Save model and metadata
        os.makedirs(save_path, exist_ok=True)
        metadata_path = os.path.join(save_path, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
            
        # Save model and/or tokenizer files
        if model:
            model.save_pretrained(save_path)
        if tokenizer:
            tokenizer.save_pretrained(save_path)
        
        # Sign the metadata and files
        ctx = SigningContext()  # Create a new SigningContext instance
        async with ctx:  # Use it as a context manager
            # Sign metadata
            metadata_signature = await ctx.sign(json.dumps(metadata).encode())
            
            # Sign all files
            signatures = {}
            for root, _, files in os.walk(save_path):
                for file in files:
                    if file.endswith(('.bin', '.json', '.txt')):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            signatures[file] = await ctx.sign(content)
        
        # Save signatures and bundles
        signatures_path = os.path.join(save_path, "signatures.json")
        with open(signatures_path, "w") as f:
            json.dump({
                "metadata_signature": metadata_signature.bundle.to_dict(),
                "file_signatures": {k: v.bundle.to_dict() for k, v in signatures.items()}
            }, f, indent=2)
            
        return {
            "metadata": metadata,
            "signatures": {k: v.bundle.to_dict() for k, v in signatures.items()},
            "save_path": save_path
        }

    async def verify_model(self, model_path: str) -> list:
        """Verify a signed model.
        
        Args:
            model_path: Path to the signed model directory
            
        Returns:
            List of tuples containing (filename, verification_result)
        """
        signatures_path = os.path.join(model_path, "signatures.json")
        with open(signatures_path) as f:
            signatures = json.load(f)
            
        results = []
        verifier = Verifier()  # Create a new Verifier instance
        
        # Verify metadata
        metadata_path = os.path.join(model_path, "metadata.json")
        with open(metadata_path, 'rb') as f:
            metadata_content = f.read()
            try:
                result = await verifier.verify(metadata_content, signatures["metadata_signature"])
                verification_status = {
                    "success": True,
                    "signer": result.cert.subject if result.cert else "Unknown",
                    "timestamp": result.timestamp.isoformat() if result.timestamp else "Unknown"
                }
            except Exception as e:
                verification_status = {
                    "success": False,
                    "error": str(e)
                }
            results.append(("metadata.json", verification_status))
            
        # Verify all files
        for filename, signature in signatures["file_signatures"].items():
            file_path = os.path.join(model_path, filename)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                    try:
                        result = await verifier.verify(content, signature)
                        verification_status = {
                            "success": True,
                            "signer": result.cert.subject if result.cert else "Unknown",
                            "timestamp": result.timestamp.isoformat() if result.timestamp else "Unknown"
                        }
                    except Exception as e:
                        verification_status = {
                            "success": False,
                            "error": str(e)
                        }
                    results.append((filename, verification_status))
                    
        return results
