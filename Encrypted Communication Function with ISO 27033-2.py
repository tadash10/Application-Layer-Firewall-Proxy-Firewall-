import ssl

def encrypted_communication(socket):
    # Wrap the socket with SSL/TLS encryption
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")  # Provide server certificate and key
    return context.wrap_socket(socket, server_side=True)
