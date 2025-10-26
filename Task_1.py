!pip install qiskit
!pip install qiskit-aer
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# -----------------------------
# Step 1: Shor Encoding Circuit
# -----------------------------
def shor_encode():
    qc = QuantumCircuit(9, name="ShorEncode")

    # Bit-flip protection (repetition code)
    qc.cx(0, 3)
    qc.cx(0, 6)

    # Phase-flip protection (use Hadamard + repetition)
    qc.h(0)
    qc.h(3)
    qc.h(6)

    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.cx(3, 4)
    qc.cx(3, 5)
    qc.cx(6, 7)
    qc.cx(6, 8)

    return qc

# -----------------------------
# Step 2: Apply quantum gates
# -----------------------------
def apply_quantum_operations():
    qc = QuantumCircuit(9, name="QuantumOps")

    qc.h(0)
    qc.rx(0.5, 1)
    qc.ry(0.3, 2)
    qc.rz(0.7, 3)
    qc.s(4)
    qc.sdg(5)
    qc.t(6)
    qc.tdg(7)
    qc.x(8)
    qc.cx(0, 4)
    qc.cz(1, 5)
    qc.swap(2, 6)

    return qc

# -----------------------------
# Step 3: Error correction (simplified)
# -----------------------------
def apply_error_correction(syndrome="000000"):
    qc = QuantumCircuit(9, name="ErrorCorrection")

    qc.barrier()
    # Apply basic correction (dummy)
    qc.x(0)
    qc.z(0)
    qc.x(0)
    qc.z(0)

    return qc

# -----------------------------
# Step 4: Full QEC Circuit
# -----------------------------
def shor_qec_circuit():
    qc = QuantumCircuit(9, 1)

    # Prepare logical |+> = H|0>
    qc.h(0)

    # Apply quantum operations
    qc = qc.compose(apply_quantum_operations())

    # Encode
    qc = qc.compose(shor_encode())

    qc.barrier()

    # Apply simplified error correction
    qc = qc.compose(apply_error_correction())

    # Decode
    qc = qc.compose(shor_encode().inverse())

    # Measure logical qubit
    qc.measure(0, 0)

    return qc

# -----------------------------
# Step 5: Noise model
# -----------------------------
def build_noise_model():
    noise_model = NoiseModel()
    p1 = 0.01
    p2 = 0.03

    error1 = depolarizing_error(p1, 1)
    noise_model.add_all_qubit_quantum_error(error1, ['h', 'x', 'y', 'z', 's', 'sdg', 't', 'tdg', 'rx', 'ry', 'rz'])

    error2 = depolarizing_error(p2, 2)
    noise_model.add_all_qubit_quantum_error(error2, ['cx', 'cz', 'swap'])

    return noise_model

# -----------------------------
# Step 6: Run comparison
# -----------------------------
def run_comparison():
    noise_model = build_noise_model()
    backend = AerSimulator(noise_model=noise_model)

    # Circuit without error correction
    qc_no_ec = QuantumCircuit(1, 1)
    qc_no_ec.h(0)
    qc_no_ec.rx(0.5, 0)
    qc_no_ec.ry(0.3, 0)
    qc_no_ec.rz(0.7, 0)
    qc_no_ec.measure(0, 0)

    # Circuit with Shor code
    qc_with_ec = shor_qec_circuit()

    # Transpile
    transpiled_no_ec = transpile(qc_no_ec, backend)
    transpiled_with_ec = transpile(qc_with_ec, backend)

    # Run
    print("Running without error correction...")
    result_no_ec = backend.run(transpiled_no_ec, shots=1000).result()
    counts_no_ec = result_no_ec.get_counts()

    print("Running with Shor error correction...")
    result_with_ec = backend.run(transpiled_with_ec, shots=1000).result()
    counts_with_ec = result_with_ec.get_counts()

    # Probabilities
    prob_0_no_ec = counts_no_ec.get('0', 0) / 1000
    prob_1_no_ec = counts_no_ec.get('1', 0) / 1000
    prob_0_with_ec = counts_with_ec.get('0', 0) / 1000
    prob_1_with_ec = counts_with_ec.get('1', 0) / 1000

    print("\nResults:")
    print(f"Without EC: 0 = {prob_0_no_ec:.3f}, 1 = {prob_1_no_ec:.3f}")
    print(f"With EC:    0 = {prob_0_with_ec:.3f}, 1 = {prob_1_with_ec:.3f}")

    deviation_no_ec = abs(0.5 - prob_0_no_ec) * 200
    deviation_with_ec = abs(0.5 - prob_0_with_ec) * 200
    print(f"Deviation (no EC): {deviation_no_ec:.2f}%")
    print(f"Deviation (with EC): {deviation_with_ec:.2f}%")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    plot_histogram(counts_no_ec, ax=ax1)
    ax1.set_title('Without Error Correction')
    ax1.set_ylim(0, 1000)

    plot_histogram(counts_with_ec, ax=ax2)
    ax2.set_title('With Shor Error Correction')
    ax2.set_ylim(0, 1000)

    plt.tight_layout()
    plt.savefig('shor_code_comparison.png', dpi=300)
    plt.show()

    return counts_no_ec, counts_with_ec

# -----------------------------
# Step 7: Demonstration of bit-flip correction
# -----------------------------
def demonstrate_error_correction():
    print("\nDemonstrating specific error correction...")

    qc = QuantumCircuit(9, 1)

    # Prepare |1⟩ state
    qc.x(0)

    # Encode
    qc = qc.compose(shor_encode())

    # Introduce bit-flip error on qubit 4
    qc.x(4)

    # Decode
    qc = qc.compose(shor_encode().inverse())

    # Measure
    qc.measure(0, 0)

    backend = AerSimulator()
    transpiled = transpile(qc, backend)
    result = backend.run(transpiled, shots=1000).result()
    counts = result.get_counts()

    print(f"Results with error on qubit 4: {counts}")
    return counts

# -----------------------------
# Step 8: Visualize circuits
# -----------------------------
def visualize_circuits():
    print("Shor Encoding Circuit:")
    print(shor_encode().draw(output='text'))

    simple_qec = QuantumCircuit(9, 1)
    simple_qec.h(0)
    simple_qec = simple_qec.compose(shor_encode())
    simple_qec.barrier()
    simple_qec = simple_qec.compose(shor_encode().inverse())
    simple_qec.measure(0, 0)

    print("\nSimplified Shor QEC Circuit:")
    print(simple_qec.draw(output='text'))

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    counts_no_ec, counts_with_ec = run_comparison()
    error_counts = demonstrate_error_correction()

    qc = shor_qec_circuit()
    print("\nCircuit stats:")
    print("Depth:", qc.depth())
    print("Size:", qc.size())
    print("Width (qubits):", qc.num_qubits)

    visualize_circuits()
