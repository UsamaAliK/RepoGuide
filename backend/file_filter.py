import os






def filter_files(file_path:list[str],root)->list[dict]:
    """Filter files by extension and skip ignored directories"""

    allowed_extensions = (
       
        ".py", ".pyx", ".pyi",

        ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs",
        
       
        ".java",
        
        
        ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx",
        
        
        ".cs",
        
        
        ".go",
        
        
        ".rs",
        
        
        ".rb",
        
        
        ".php",
        
      
        ".swift",
        
        
        ".kt", ".kts",
        
        
        ".scala",
        
        
        ".r", ".R",
        
        
        ".sh", ".bash", ".zsh",
        
        
        ".lua",
        
        
        ".pl", ".pm",
        
        
        ".groovy", ".gradle",
        
        
        ".md", ".markdown", ".rst", ".adoc", ".asciidoc", ".txt",
        
        
        ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
        ".xml", ".properties",
        
        
        ".html", ".htm", ".css", ".scss", ".sass", ".less",
        
        
        ".sql",
        
        ".dockerfile", "Dockerfile",
        
        
        ".gradle", ".maven", ".sbt", ".dub"
    )

    ignored_dirs = [
        "node_modules", ".git", "__pycache__",
        "venv", ".venv", ".env", "build", "dist",
        ".next", ".nuxt", "vendor", ".gradle",
        ".maven", "target", "bin", "obj",
        ".vscode", ".idea", ".vs",
        "coverage", ".pytest_cache", ".mypy_cache"
    ]
    filtered=[]
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

    for path in file_path:

        if any(ignored in path.split(os.sep) for ignored in ignored_dirs ):
            continue
        if not any(path.endswith(allowed) for allowed in allowed_extensions):
            continue
        try:
            if os.path.getsize(path)>MAX_FILE_SIZE:  # 5 MB
                continue
        except:
            continue
        filtered.append({
            "path":path,
            "relative_path":os.path.relpath(path,root)
        })
    return filtered



