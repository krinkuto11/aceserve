import socket
import struct
import os
import dns.resolver
import threading

FALLBACK_DNS = ['1.1.1.1', '8.8.8.8']

def dnsproxyd_listener(resolver):
    socket_path = '/dev/socket/dnsproxyd'
    os.makedirs(os.path.dirname(socket_path), exist_ok=True)

    if os.path.exists(socket_path):
        try:
            os.remove(socket_path)
        except OSError:
            pass

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server_sock:
            try:
                server_sock.bind(socket_path)
            except PermissionError as e:
                print(f'dnsproxyd: PermissionError binding to {socket_path}: {e}')
                return
            except OSError as e:
                print(f'dnsproxyd: OSError binding to {socket_path}: {e}')
                return

            server_sock.listen(1)

            while True:
                client_sock, _ = server_sock.accept()
                with client_sock:
                    query = client_sock.recv(1024)
                    domain = query.split()[1].decode('utf-8')

                    resolved = []
                    try:
                        resolved = resolver.resolve(domain)
                    except Exception:
                        pass

                    if not resolved:
                        fallback_resolver = dns.resolver.Resolver()
                        fallback_resolver.nameservers = FALLBACK_DNS
                        try:
                            resolved = fallback_resolver.resolve(domain)
                        except Exception:
                            pass

                    if resolved:
                        response = create_addrinfo_response(resolved[0].address)
                    else:
                        response = create_error_response()

                    client_sock.sendall(response)
    finally:
        if os.path.exists(socket_path):
            try:
                os.remove(socket_path)
            except OSError:
                pass

def create_addrinfo_response(ip):
    return struct.pack(
        '!4s I I I I I I I 4s I I I I',
        b"222",
        1, 0,
        2, 1, 6,
        16, 0x02000050, socket.inet_aton(ip),
        0, 0, 0, 0
    )

def create_error_response():
    return struct.pack(
        '!4s I I',
        b"401",
        4,
        0x7000000
    )

def dns_daemon(resolver):
    t = threading.Thread(target=dnsproxyd_listener,name="dnsproxyd",args=(resolver,))
    t.daemon = True
    t.start()
    return t

if __name__ == "__main__":
    t = dns_daemon(dns.resolver.Resolver())
    t.join()
