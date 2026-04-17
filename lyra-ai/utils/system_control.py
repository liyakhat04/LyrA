import webbrowser


def open_known_destination(intent: str) -> bool:
    """Open safe known destinations based on intent phrases."""
    lowered = intent.lower()
    mapping = {
        "youtube": "https://youtube.com",
        "github": "https://github.com",
        "linkedin": "https://linkedin.com",
    }
    for key, url in mapping.items():
        if key in lowered:
            webbrowser.open(url)
            return True
    return False
