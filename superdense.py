from matplotlib import pyplot as plt
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, Aer, IBMQ, transpile
from qiskit.providers.ibmq import least_busy
from qiskit.visualization import plot_histogram

qreg_charlie = QuantumRegister(2, 'teletom')
qreg_alice = QuantumRegister(1, 'alice')
qreg_bob = QuantumRegister(2, 'bob')
creg_bob = ClassicalRegister(2, 'received_message')
circuit = QuantumCircuit(qreg_charlie, qreg_alice, qreg_bob, creg_bob)

# create ERP pair
circuit.h(qreg_charlie[0]) 
circuit.cx(qreg_charlie[0], qreg_charlie[1])
circuit.barrier()

# send one qubit to alice 
circuit.swap(qreg_charlie[0], qreg_alice[0])

# send one qubit to bob 
circuit.swap(qreg_charlie[1], qreg_bob[0])
circuit.barrier()

# alice's message two bit integer to send to bob
alice_message = '10'

# alice encodes her bits
if alice_message == '00':
    # if message is 0 add identity gate
    circuit.id(qreg_alice[0])

elif alice_message == '01':
    # if message is 1 add x gate
    circuit.x(qreg_alice[0])

elif alice_message == '10':
    # if message is 2 add z gate
    circuit.z(qreg_alice[0])

elif alice_message == '11':
    # if message is 3 add z * x gates 
    circuit.z(qreg_alice[0])
    circuit.x(qreg_alice[0])

circuit.barrier()

# send encoded qubit to bob
circuit.swap(qreg_alice[0], qreg_bob[1])
circuit.barrier()

# bob decodes qubits
circuit.cx(qreg_bob[0], qreg_bob[1])
circuit.h(qreg_bob[0])
circuit.barrier()

# bob measures his qubits
circuit.measure(qreg_bob[0], creg_bob[0])
circuit.measure(qreg_bob[1], creg_bob[1])

circuit.draw('mpl')
plt.savefig("circuit.svg")
## simulate circuit
aer_sim = Aer.get_backend('aer_simulator')
result = aer_sim.run(circuit).result()
counts = result.get_counts(circuit)


## run circuit on actual quantum computer
IBMQ.load_account()

# get the least busy backend
provider = IBMQ.get_provider(hub='ibm-q')
backend = least_busy(provider.backends(filters=lambda x: x.configuration().n_qubits >= 5 and not x.configuration().simulator and x.status().operational))
print("Running on least busy backend:", backend)

# run circuit
transpiled_circuit = transpile(circuit, backend, optimization_level=3)
job = backend.run(transpiled_circuit)
result = job.result()
print(f"Alice's Message: {max(counts, key=counts.get)}")

plot_histogram(result.get_counts(circuit))
plt.show()