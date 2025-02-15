from uuid import UUID

def check_uuid(uuid_str: str) -> UUID:
    try:
        return UUID(uuid_str)
    except ValueError:
        return False