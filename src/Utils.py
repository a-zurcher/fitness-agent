import dotenv

def get_dotenv(key: str) -> str:
    return dotenv.get_key(key_to_get=key, dotenv_path=".env")

def set_dotenv(key: str, value: str) -> None:
    dotenv.set_key(key_to_set=key, value_to_set=value, dotenv_path=".env")
