import base64

# convertes binary file content into base64 bytes and decodes the bytes as utf-8 string
def as_base64(path):
    with open(path, 'rb') as file:
        content = file.read()
        return base64.standard_b64encode(content).decode('utf-8')