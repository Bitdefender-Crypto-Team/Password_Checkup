import socket
import tenseal as ts
import pickle

database = ['10100', '10110', '10111', '11', '101', '1000', '1010', '10000010', '1000110', '101111']
len_database = len(database)
new_database = [int(database[i], 2) for i in range(len_database)]

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind(('localhost', 4472))
serv.listen(3)

for i in range(3):
    conn, addr = serv.accept()
    L = conn.recv(10).decode().strip()
    L = int(L, 10)

    # Getting bytes of context and encrypted query
    final_data = b""
    while len(final_data) < L:
        data = conn.recv(4096)
        if not data: break
        final_data += data
    deserialized_message = pickle.loads(final_data)

    # Here we recover the context and ciphertext received from the client
    context = ts.context_from(deserialized_message[0])
    ciphertext = deserialized_message[1]
    ct = ts.bfv_vector_from(context, ciphertext)

    # Evaluate the database polynomial at the ciphertext received from the client
    response = ct - [new_database[0]]
    for i in range(1, len_database):
        factor = ct - [new_database[i]]
        response = response * factor

    # Prepare the answer to be sent to the client
    response_serialized = response.serialize()
    response_to_be_sent = pickle.dumps(response_serialized, protocol=None)
    conn.sendall(response_to_be_sent)

    # Close the connection
    conn.close()
    print("Client disconnected")