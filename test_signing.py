import asyncio
from jup_sigstore import ModelSigner
from transformers import AutoModel, AutoTokenizer
import json

async def main():
    print("1. Initializing ModelSigner...")
    signer = ModelSigner()
    
    print("\n2. Loading BERT model...")
    model = AutoModel.from_pretrained("bert-base-uncased")
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    
    print("\n3. Signing model...")
    result = await signer.sign_model(
        model=model,
        tokenizer=tokenizer,
        save_path="./signed_model"
    )
    
    print("\nSigning completed. Results:")
    print(json.dumps(result, indent=2))
    
    print("\n4. Verifying signed model...")
    verification = await signer.verify_model("./signed_model")
    
    print("\nVerification results:")
    for filename, result in verification:
        print(f"\n{filename}:")
        print(f"Verified: {result['success']}")
        if result['success']:
            print(f"Signed by: {result['signer']}")
            print(f"Timestamp: {result['timestamp']}")
        else:
            print(f"Error: {result['error']}")

if __name__ == "__main__":
    # Create a new event loop and run the async main function
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
