from qiskit.quantum_info.operators import Operator
from qiskit import *
from qiskit.visualization import plot_histogram
from qiskit.circuit import Gate
import numpy as np
from qiskit.providers.fake_provider import FakeManilaV2
from qiskit.circuit.library import RYGate
import math

#BCM_3(0.2, 0.3, 0.4) => num_qubits = 6

#setting constants
alpha = 0.2
beta = 0.3
gamma = 0.4

theta_0  = 2*math.acos(gamma)
theta_1 = 2*math.acos(alpha - 1)
theta_2 = 2*math.acos(beta)

#contstructing R_Y(theta_0), R_Y(theta_1), R_Y(theta_2)
ccry_theta_0 = RYGate(theta_0).control(2, label=None)
ccry_theta_1 = RYGate(theta_1).control(2, label=None)
ccry_theta_2 = RYGate(theta_2).control(2, label=None)

#creating O_A (product of controlled rotations)
O_A = QuantumCircuit(3, name="O_A")
O_A.barrier()
#appending first controlled rotation
O_A.x(1)
O_A.x(2)
O_A.append(ccry_theta_0, [1,2,0])
O_A.x(1)
O_A.x(2)
O_A.barrier()
#appending second controlled rotation
O_A.x(1)
O_A.append(ccry_theta_1, [1,2,0])
O_A.x(1)
O_A.barrier()
#appending third controlled rotation
O_A.x(2)
O_A.append(ccry_theta_2, [1,2,0])
O_A.x(2)
O_A.barrier()

#creating double controlled Right-Shift, double controlled Left-Shift circuit
R_Shift = QuantumCircuit(3, name="R")
R_Shift.x(1)
R_Shift.x(2)
R_Shift.ccx(1,2,0)
R_Shift.x(1)
R_Shift.x(2)
R_Shift.x(2)
R_Shift.cx(2,1)
R_Shift.x(2)
R_Shift.x(2)
cc_R_Shift_gate = R_Shift.to_gate().control(2, label=None)

L_Shift = QuantumCircuit(3, name="L")
L_Shift.ccx(1,2,0)
L_Shift.cx(2,1)
L_Shift.x(2)
cc_L_Shift_gate = L_Shift.to_gate().control(2, label=None)

#creating O_C
O_C = QuantumCircuit(5, name="O_C")
O_C.x(0)
O_C.x(1)
O_C.append(cc_R_Shift_gate, [0,1,2,3,4])
O_C.x(0)
O_C.x(1)
O_C.barrier()
O_C.x(1)
O_C.append(cc_L_Shift_gate, [0,1,2,3,4])
O_C.x(1)



#creating BCM circuit
BCM = QuantumCircuit(6, 6)
BCM.reset(range(6))

#start put instructions here for encoding input vector |x>
#i.e. BCM.h(5)

#for x = (1/2 0 1/2 0 1/2 0 1/2 0)^T
BCM.h(3)
BCM.h(4)
#end

BCM.h(1)
BCM.h(2)
BCM.barrier()
BCM.append(O_A, [0,1,2])
BCM.barrier()
BCM.append(O_C, [1,2,3,4,5])
BCM.barrier()
BCM.h(1)
BCM.h(2)
BCM.barrier()
BCM.measure([i for i in range(6)], [i for i in range(6)])

#Test-bench:
outs = []
count = 0
backend = Aer.get_backend("aer_simulator") #accurate simualtor using no noise
bit_str_dict = {}
total_zeros = 0
iters = 1000
normalization_factor = math.sqrt(alpha**2 + (beta + gamma)**2) #changes for each test case |x>

for i in range(iters):
    job = backend.run(BCM.decompose(reps = 6), shots=1, memory=True)
    output = job.result().get_memory()[0][::-1] #need to reverse do to formatting (big-endian but needs to be little endian)
    if (output[0] == '0' and output[1] == '0' and output[2] == '0'):
      bit_str = output[3:]
      if (bit_str in bit_str_dict):
        bit_str_dict[bit_str] += 1
      else:
        bit_str_dict[bit_str] = 1
      total_zeros += 1
  
for key in bit_str_dict:
   print("coefficient of " + str(key) + ": " + str(normalization_factor*math.sqrt(bit_str_dict[key]/total_zeros)))
