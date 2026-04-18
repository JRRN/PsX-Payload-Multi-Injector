class Payload:
    def __init__(self, name, url, platform, port):
        self.name = name
        self.url = url
        self.platform = platform
        self.port = port

    @classmethod
    def from_line(cls, line):
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 4:
            return None

        name, url, platform, port = parts
        if not name or not url or not port or not platform:
            return None
        return cls(name=name, url=url, platform=platform, port=port)

    def __str__(self):
        return f"{self.name} ({self.platform}:{self.port})"
