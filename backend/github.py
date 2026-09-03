import httpx
import zipfile
import tempfile
import os
from fastapi import HTTPException
from .file_filter import filter_files

# --- GitHub API + ZIP download helpers ---

def parse_github_url(github_url: str) -> dict:
    """extract owner and repo name from url"""
    parts = github_url.rstrip("/").split("/")
    return {"owner": parts[-2], "repo": parts[-1].replace(".git", "")}


async def get_repo_metadata(owner: str, repo: str) -> dict:
    """get default branch and size of repo"""
    MAX_REPO_SIZE_KB=500_000 #50MB
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}"
            )
            response.raise_for_status()
            data = response.json()
            if data["size"]>MAX_REPO_SIZE_KB:
                raise HTTPException(
                    status_code=413,
                    detail="Repository is too large to process "
                )
            return {
                "default_branch": data["default_branch"],
                "size_kb": data["size"],
            }
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail="Failed to fetch repo metadata"
            )


async def download_repo_zip(owner: str, repo: str, branch: str) -> dict:
    """download repository as zipball, unpack it, and return local file paths

    returns dict: {"root": <dir>, "files": [list of file paths]}
    """
    url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"{repo}.zip")

    async with httpx.AsyncClient(follow_redirects=True) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()

            with open(zip_path, "wb") as file:
                async for chunk in response.aiter_bytes():
                    file.write(chunk)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(temp_dir)

    # zipball extracts to a folder like {repo}-{branch}
    root = os.path.join(
        temp_dir,
        [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))][0]

    )

    file_paths = []

    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            file_paths.append(os.path.join(dirpath, filename))
    filtered=filter_files(file_paths,root)

    return {
        "filtered files":filtered,
        "root": root,
        "files": file_paths
    }

