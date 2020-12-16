import tenseal as ts
import socket
import pickle

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 4472))

# Setting the public and private contexts
private_context = ts.context(ts.SCHEME_TYPE.BFV, poly_modulus_degree = 2 ** 14, plain_modulus = 2 ** 16 + 1)
public_context = ts.context_from(private_context.serialize())
public_context.make_context_public()

# I create the query to be sent to the server
query = '1001000'
plain_query = [int(query, 2)]
enc_query = ts.bfv_vector(public_context, plain_query)

# I prepare the message that I want to send to the server
enc_query_serialized = enc_query.serialize()
context_serialized = public_context.serialize()
message_to_be_sent = [context_serialized, enc_query_serialized]
message_to_be_sent_serialized = pickle.dumps(message_to_be_sent, protocol=None)

# Here is the length of my message
L = len(message_to_be_sent_serialized)
sL = str(L) + ' ' * (10 - len(str(L))) #pad len to 10 bytes

# I first send the length of the message to the server
client.sendall((sL).encode())
print("Sending the context and ciphertext to the server....")
# Now I send the message to the server
client.sendall(message_to_be_sent_serialized)
print("Waiting for the servers's answer...")

# Here is the answer obtained from the server
answer= b""
while True:
    data = client.recv(4096)
    if not data: break
    answer += data

# Here is the decryption of the answer
deserialized_ciphertext = pickle.loads(answer)
verdict = ts.bfv_vector_from(private_context, deserialized_ciphertext).decrypt()
if (verdict == [0]):
    print("My password is in the database.")
else:
    print("My password is not in the database.")

print("Disconnecting...")
client.close()


