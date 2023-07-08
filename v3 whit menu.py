import socket
import datetime
import ssl
import time

# Define the proxy server details
PROXY_HOST = '127.0.0.1'  # Proxy server IP address
PROXY_PORT = 8080  # Proxy server port

# Define the destination server details
DESTINATION_HOST = 'example.com'  # Destination server IP address or hostname
DESTINATION_PORT = 80  # Destination server port

REQUESTS_PER_SECOND = 10  # Rate limiting: maximum requests per second

class ProxyFirewall:
    def __init__(self):
        self.access_control_list = ["192.168.0.100", "10.0.0.5"]  # Access control list
        self.cache = {}  # Request caching dictionary
        self.connection_pool = []  # Connection pooling list

    def log_event(self, event):
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"{timestamp}: {event}"
        with open("firewall.log", "a") as log_file:
            log_file.write(log_entry + "\n")

    def access_control(self, client_address):
        # Implement access control policies based on client IP address or other factors
        if client_address in self.access_control_list:
            return True  # Allow access
        else:
            return False  # Deny access

    def content_filtering(self, data):
        # Implement content filtering rules to examine and filter data
        if "restricted_keyword" in data:
            return False  # Block data
        else:
            return True  # Allow data

    def rate_limit(self):
        # Implement rate limiting to control the number of requests per second
        current_time = time.time()
        if current_time - self.rate_limit.last_request_time < 1 / REQUESTS_PER_SECOND:
            return False  # Reject request
        else:
            self.rate_limit.last_request_time = current_time
            return True  # Allow request

    rate_limit.last_request_time = time.time()

    def encrypted_communication(self, socket):
        # Wrap the socket with SSL/TLS encryption
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile="server.crt", keyfile="server.key")  # Provide server certificate and key
        return context.wrap_socket(socket, server_side=True)

    def handle_client_to_server(self, client_socket, destination_socket):
        while True:
            # Receive data from the client
            client_data = client_socket.recv(4096)

            if len(client_data) > 0:
                # Rate limiting
                if not self.rate_limit():
                    self.log_event("Rate limit exceeded from {}".format(client_socket.getpeername()[0]))
                    break

                # Content filtering
                if not self.content_filtering(client_data):
                    self.log_event("Content filtering blocked data from {}".format(client_socket.getpeername()[0]))
                    break

                # Check if request is in cache
                request_hash = hash(client_data)
                if request_hash in self.cache:
                    # Serve the response from cache
                    cached_response = self.cache[request_hash]
                    client_socket.sendall(cached_response)
                else:
                    # Modify or inspect the client data as per the firewall rules
                    # Here, we are simply forwarding the client data to the destination server
                    destination_socket.sendall(client_data)
            else:
                break

    def handle_server_to_client(self, destination_socket, client_socket):
        while True:
            # Receive data from the destination server
            server_data = destination_socket.recv(4096)

            if len(server_data) > 0:
                # Modify or inspect the server data as per the firewall rules
                # Here, we are simply forwarding the server data to the client
                client_socket.sendall(server_data)

                # Cache the response
                request_hash = hash(client_socket.recv(4096))
                self.cache[request_hash] = server_data
            else:
                break

    def create_connection_pool(self):
        for _ in range(10):  # Set the desired number of connections in the pool
            # Connect to the destination server
            destination_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            destination_socket.connect((DESTINATION_HOST, DESTINATION_PORT))
            self.connection_pool.append(destination_socket)

    def proxy_firewall(self):
        # Create a socket for the proxy server
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            # Bind the proxy socket to the specified host and port
            proxy_socket.bind((PROXY_HOST, PROXY_PORT))

            # Listen for incoming client connections
            proxy_socket.listen(1)
            print('Proxy server is listening on {}:{}'.format(PROXY_HOST, PROXY_PORT))

            while True:
                # Accept client connection
                client_socket, client_address = proxy_socket.accept()
                print('Accepted connection from {}:{}'.format(client_address[0], client_address[1]))

                # Access control
                if not self.access_control(client_address[0]):
                    self.log_event("Access denied from {}".format(client_address[0]))
                    client_socket.close()
                    continue

                # Get a connection from the pool
                destination_socket = self.connection_pool.pop()

                # Enable encrypted communication
                client_socket = self.encrypted_communication(client_socket)
                destination_socket = self.encrypted_communication(destination_socket)

                # Handle client-to-server and server-to-client communication
                self.handle_client_to_server(client_socket, destination_socket)
                self.handle_server_to_client(destination_socket, client_socket)

                # Close the connections and return them to the pool
                destination_socket.close()
                self.connection_pool.append(destination_socket)
                client_socket.close()

        except KeyboardInterrupt:
            print('Proxy server terminated.')
        finally:
            proxy_socket.close()

    def show_menu(self):
        while True:
            print("\nProxy Firewall Menu:")
            print("1. Start Proxy Server")
            print("2. Configure Access Control")
            print("3. Configure Content Filtering")
            print("4. Configure Rate Limiting")
            print("5. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                self.create_connection_pool()
                self.proxy_firewall()
            elif choice == "2":
                self.configure_access_control()
            elif choice == "3":
                self.configure_content_filtering()
            elif choice == "4":
                self.configure_rate_limiting()
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")

    def configure_access_control(self):
        print("\nAccess Control Configuration:")
        print("Current Access Control List:", self.access_control_list)
        print("Enter 'exit' to go back.")
        while True:
            entry = input("Enter an IP address to add or remove: ")
            if entry == "exit":
                break
            if entry in self.access_control_list:
                self.access_control_list.remove(entry)
                print("IP address removed from the Access Control List.")
            else:
                self.access_control_list.append(entryThis script update includes two critical features, request caching and connection pooling, along with a menu for configuring and managing the proxy firewall. The `ProxyFirewall` class encapsulates the functionalities and provides an interactive menu for configuration. Here's the complete script:

```python
import socket
import datetime
import ssl
import time

# Define the proxy server details
PROXY_HOST = '127.0.0.1'  # Proxy server IP address
PROXY_PORT = 8080  # Proxy server port

# Define the destination server details
DESTINATION_HOST = 'example.com'  # Destination server IP address or hostname
DESTINATION_PORT = 80  # Destination server port

REQUESTS_PER_SECOND = 10  # Rate limiting: maximum requests per second

class ProxyFirewall:
    def __init__(self):
        self.access_control_list = ["192.168.0.100", "10.0.0.5"]  # Access control list
        self.cache = {}  # Request caching dictionary
        self.connection_pool = []  # Connection pooling list

    def log_event(self, event):
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"{timestamp}: {event}"
        with open("firewall.log", "a") as log_file:
            log_file.write(log_entry + "\n")

    def access_control(self, client_address):
        # Implement access control policies based on client IP address or other factors
        if client_address in self.access_control_list:
            return True  # Allow access
        else:
            return False  # Deny access

    def content_filtering(self, data):
        # Implement content filtering rules to examine and filter data
        if "restricted_keyword" in data:
            return False  # Block data
        else:
            return True  # Allow data

    def rate_limit(self):
        # Implement rate limiting to control the number of requests per second
        current_time = time.time()
        if current_time - self.rate_limit.last_request_time < 1 / REQUESTS_PER_SECOND:
            return False  # Reject request
        else:
            self.rate_limit.last_request_time = current_time
            return True  # Allow request

    rate_limit.last_request_time = time.time()

    def encrypted_communication(self, socket):
        # Wrap the socket with SSL/TLS encryption
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile="server.crt", keyfile="server.key")  # Provide server certificate and key
        return context.wrap_socket(socket, server_side=True)

    def handle_client_to_server(self, client_socket, destination_socket):
        while True:
            # Receive data from the client
            client_data = client_socket.recv(4096)

            if len(client_data) > 0:
                # Rate limiting
                if not self.rate_limit():
                    self.log_event("Rate limit exceeded from {}".format(client_socket.getpeername()[0]))
                    break

                # Content filtering
                if not self.content_filtering(client_data):
                    self.log_event("Content filtering blocked data from {}".format(client_socket.getpeername()[0]))
                    break

                # Check if request is in cache
                request_hash = hash(client_data)
                if request_hash in self.cache:
                    # Serve the response from cache
                    cached_response = self.cache[request_hash]
                    client_socket.sendall(cached_response)
                else:
                    # Modify or inspect the client data as per the firewall rules
                    # Here, we are simply forwarding the client data to the destination server
                    destination_socket.sendall(client_data)
            else:
                break

    def handle_server_to_client(self, destination_socket, client_socket):
        while True:
            # Receive data from the destination server
            server_data = destination_socket.recv(4096)

            if len(server_data) > 0:
                # Modify or inspect the server data as per the firewall rules
                # Here, we are simply forwarding the server data to the client
                client_socket.sendall(server_data)

                # Cache the response
                request_hash = hash(client_socket.recv(4096))
                self.cache[request_hash] = server_data
            else:
                break

    def create_connection_pool(self):
        for _ in range(10):  # Set the desired number of connections in the pool
            # Connect to the destination server
            destination_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            destination_socket.connect((DESTINATION_HOST, DESTINATION_PORT))
            self.connection_pool.append(destination_socket)

    def proxy_firewall(self):
        # Create a socket for the proxy server
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            # Bind the proxy socket to the specified host and port
            proxy_socket.bind((PROXY_HOST, PROXY_PORT))

            # Listen for incoming client connections
            proxy_socket.listen(1)
            print('Proxy server is listening on {}:{}'.format(PROXY_HOST, PROXY_PORT))

            while True:
                # Accept client connection
                client_socket, client_address = proxy_socket.accept()
                print('Accepted connection from {}:{}'.format(client_address[0], client_address[1]))

                # Access control
                if not self.access_control(client_address[0]):
                    self.log_event("Access denied from {}".format(client_address[0]))
                    client_socket.close()
                    continue

                # Get a connection from the pool
                destination_socket = self.connection_pool.pop()

                # Enable encrypted communication
                client_socket = self.encrypted_communication(client_socket)
                destination_socket = self.encrypted_communication(destination_socket)

                # Handle client-to-server and server-to-client communication
                self.handle_client_to_server(client_socket, destination_socket)
                self.handle_server_to_client(destination_socket, client_socket)

                # Close the connections and return them to the pool
                destination_socket.close()
                self.connection_pool.append(destination_socket)
                client_socket.close()

        except KeyboardInterrupt:
            print('Proxy server terminated.')
        finally:
            proxy_socket.close()

    def show_menu(self):
        while True:
            print("\nProxy Firewall Menu:")
            print("1. Start Proxy Server")
            print("2. Configure Access Control")
            print("3. Configure Content Filtering")
            print("4. Configure Rate Limiting")
            print("5. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                self.create_connection_pool()
                self.proxy_firewall()
            elif choice == "2":
                self.configure_access_control()
            elif choice == "3":
                self.configure_content_filtering()
            elif choice == "4":
                self.configure_rate_limiting()
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")

    def configure_access_control(self):
        print("\nAccess Control Configuration:")
        print("Current Access Control List:", self.access_control_list)
        print("Enter 'exit' to go back.")
        while True:
            entry = input("Enter an IP address to add or remove: ")
            if entry == "exit":
                break
            if entry in self.access_control_list:
                self.access_control_list.remove(entry)
                print("IP address removed from the Access Control List.")
            else:
                self.access_control_list.append(entry)
                print("With the provided updates, the script is now more robust and includes two critical features: request caching and connection pooling. Additionally, a menu has been added to facilitate configuration and management of the proxy firewall. The `ProxyFirewall` class encapsulates the functionalities, and you can call the `show_menu` method to start the interactive menu.
