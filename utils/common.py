import uuid

def generate_reference_no() -> str:
    return uuid.uuid4().hex


if __name__ == "__main__":
    print(generate_reference_no())