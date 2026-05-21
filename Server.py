"""
Server.py
=========
Voting server — listens on port 4001, authenticates voters via CSV,
records votes, and handles concurrent connections with threading locks.

Run standalone:  python Server.py
Or started by the Admin Dashboard via subprocess.
"""

import socket
import threading
import dframe as df
from threading import Thread

# ── thread lock to serialise database writes ─────────────────────────
lock = threading.Lock()


def client_thread(connection: socket.socket, address):
    """Handle one voter connection end-to-end."""
    try:
        # ── Step 1: send handshake ────────────────────────────────
        connection.send("Connection Established".encode())

        # ── Step 2: receive voter credentials ────────────────────
        data = connection.recv(1024)
        if not data:
            print(f"[{address}] No data received. Closing.")
            return

        log = data.decode().split(" ", 1)   # split on first space only

        try:
            voter_id = int(log[0])
            password = log[1] if len(log) > 1 else ""
        except (ValueError, IndexError):
            print(f"[{address}] Malformed credentials.")
            connection.send("InvalidVoter".encode())
            return

        # ── Step 3: authenticate ──────────────────────────────────
        if not df.verify(voter_id, password):
            print(f"[{address}] Invalid voter ID={voter_id}")
            connection.send("InvalidVoter".encode())
            return

        if not df.isEligible(voter_id):
            print(f"[{address}] Already voted: ID={voter_id}")
            connection.send("VoteCasted".encode())
            return

        print(f"[{address}] Authenticated voter ID={voter_id}")
        connection.send("Authenticate".encode())

        # ── Step 4: receive vote ──────────────────────────────────
        data = connection.recv(1024)
        if not data:
            print(f"[{address}] No vote received.")
            return

        vote = data.decode().strip()
        print(f"[{address}] Vote received: '{vote}' from ID={voter_id}  — processing…")

        with lock:
            success = df.vote_update(vote, voter_id)

        if success:
            print(f"[{address}] ✅  Vote recorded successfully for ID={voter_id}")
            connection.send("Successful".encode())
        else:
            print(f"[{address}] ❌  Vote update failed for ID={voter_id}")
            connection.send("Vote Update Failed".encode())

    except ConnectionResetError:
        print(f"[{address}] Connection reset by client.")
    except Exception as ex:
        print(f"[{address}] Unexpected error: {ex}")
        try:
            connection.send("ServerError".encode())
        except Exception:
            pass
    finally:
        try:
            connection.close()
        except Exception:
            pass


def voting_Server():
    """Start the voting server and accept connections indefinitely."""
    host = socket.gethostname()
    port = 4001

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((host, port))
    except OSError as e:
        print(f"[Server] Bind error: {e}")
        return

    server_socket.listen(10)
    print(f"[Server] 🚀  Listening on {host}:{port}")

    thread_count = 0

    while True:
        try:
            client, address = server_socket.accept()
            print(f"[Server] New connection from {address}")

            t = Thread(target=client_thread, args=(client, address), daemon=True)
            t.start()
            thread_count += 1
            print(f"[Server] Active threads: {thread_count}")

        except KeyboardInterrupt:
            print("\n[Server] Shutting down…")
            break
        except Exception as ex:
            print(f"[Server] Accept error: {ex}")

    server_socket.close()
    print("[Server] 🛑  Server stopped.")


if __name__ == "__main__":
    voting_Server()
