from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Keep language as free-form locale code; actual support is discovered from src/lang/*.json.
    language: str = "es-es"
    # Optional custom URL for a Windows x86_64 socat.exe binary.
    # Keep empty by default because previously used public URL is no longer valid.
    socat_win_url: str = ""
    # Linux x86_64 fallback source (currently valid).
    socat_linux_x64_url: str = (
        "https://github.com/andrew-d/static-binaries/raw/master/"
        "binaries/linux/x86_64/socat"
    )
    # Timeout in seconds for socat send operations (PS4/PS5 payload injection).
    socat_timeout: int = 30

    model_config = ConfigDict(env_file=".env")


settings = Settings()
