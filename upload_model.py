from huggingface_hub import HfApi, login

HF_TOKEN = "hf_your_token_here"
HF_USERNAME = "Mumtaj-Shaikh"
REPO_NAME = "codereview-codebert"
MODEL_PATH = "models/codebert-finetuned"

print("Logging in to HuggingFace...")
login(token=HF_TOKEN)

api = HfApi()

print("Creating repo...")
api.create_repo(
    repo_id=f"{HF_USERNAME}/{REPO_NAME}",
    repo_type="model",
    exist_ok=True,
    token=HF_TOKEN
)
print(f"Repo created!")

print("Uploading model files...")
api.upload_folder(
    folder_path=MODEL_PATH,
    repo_id=f"{HF_USERNAME}/{REPO_NAME}",
    repo_type="model",
    token=HF_TOKEN
)

print(f"Done! https://huggingface.co/{HF_USERNAME}/{REPO_NAME}")