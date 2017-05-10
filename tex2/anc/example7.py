from __future__ import print_function, division

import numpy as np
from quspin.operators import ops_dict,hamiltonian,exp_op
from quspin.basis import spin_basis_1d
from quspin.tools.measurements import obs_vs_time
import matplotlib.pyplot as plt
import sys,os

# user defined generator
# generates stroboscopic dynamics 
def evolve_gen(psi0,U1,U2,U3,nT):
	yield psi0
	for i in range(nT):
		psi0 = U1.dot(psi0)
		psi0 = U2.dot(psi0)
		psi0 = U3.dot(psi0)
		yield psi0

# frequency and period for driving.
omega = 4
T = 2*np.pi/omega 
nT = 150 # number of periods to evolve to.
times = np.arange(0,nT+1,1)*T

L_1 = 18 # length of chain for spin 1/2
L_2 = 11 # length of chain for spin 1

basis_1 = spin_basis_1d(L_1,S="1/2",kblock=0,pblock=1,zblock=1) # spin 1/2 basis
basis_2 = spin_basis_1d(L_2,S="1"  ,kblock=0,pblock=1,zblock=1) # spin 1 basis
# print information about the basis
print("S = {S:3s}, L = {L:2d}, Size of H-space: {Ns:d}".format(S="1/2",L=L_1,Ns=basis_1.Ns))
print("S = {S:3s}, L = {L:2d}, Size of H-space: {Ns:d}".format(S="1"  ,L=L_2,Ns=basis_2.Ns))

# setting up coupling lists
Jzz_1 = [[-1.0,i,(i+1)%L_1] for i in range(L_1)]
hx_1  = [[-1.0,i] for i in range(L_1)]
Jzz_2 = [[-1.0,i,(i+1)%L_2] for i in range(L_2)]
hx_2  = [[-1.0,i] for i in range(L_2)]
# dictioanry to turn off checks
no_checks = dict(check_symm=False,check_herm=False)
# setting up hamiltonians
Hzz_1 = hamiltonian([["zz",Jzz_1]],[],basis=basis_1,dtype=np.float64)
Hx_1  = hamiltonian([["+",hx_1],["-",hx_1]],[],basis=basis_1,dtype=np.float64)
Hzz_2 = hamiltonian([["zz",Jzz_2]],[],basis=basis_2,dtype=np.float64,**no_checks)
Hx_2  = hamiltonian([["+",hx_2],["-",hx_2]],[],basis=basis_2,dtype=np.float64,**no_checks)
# calculating bandwidth for non-driven hamiltonian
[E_1_min],psi_1 = Hzz_1.eigsh(k=1,which="SA")
[E_2_min],psi_2 = Hzz_2.eigsh(k=1,which="SA")
# setting up initial states
psi0_1 = psi_1.ravel()
psi0_2 = psi_2.ravel()
# creating generators of time evolution
U1_1 = exp_op(omega*Hx_1,a=-1j*T/6)
U2_1 = exp_op(Hzz_1,a=-1j*3*T/6)
U3_1 = exp_op(-omega*Hx_1,a=-1j*2*T/6)
U1_2 = exp_op(omega*Hx_2,a=-1j*T/6)
U2_2 = exp_op(Hzz_2,a=-1j*3*T/6)
U3_2 = exp_op(-omega*Hx_2,a=-1j*2*T/6)
# get generator objects to get time dependent states
psi_1_t = evolve_gen(psi0_1,U1_1,U2_1,U3_1,nT)
psi_2_t = evolve_gen(psi0_2,U1_2,U2_2,U3_2,nT)
# measure energy as a function of time
Obs_1_t = obs_vs_time(psi_1_t,times,dict(E=Hzz_1),return_state=True)
Obs_2_t = obs_vs_time(psi_2_t,times,dict(E=Hzz_2),return_state=True)

sparse_args = dict(sparse=False,sparse_diag=False)
Sent_time_1 = basis_1.ent_entropy(Obs_1_t["psi_t"],sub_sys_A=range(L_1//2),**sparse_args)["Sent_A"]/(L_1//2)
Sent_time_2 = basis_2.ent_entropy(Obs_2_t["psi_t"],sub_sys_A=range(L_2//2),**sparse_args)["Sent_A"]/(L_2//2)


#plotting results
plt.plot(times/T,(Obs_1_t["E"]-E_1_min)/(-E_1_min),marker='.',markersize=5,label="$S=1/2$")
plt.plot(times/T,(Obs_2_t["E"]-E_2_min)/(-E_2_min),marker='.',markersize=5,label="$S=1$")
plt.grid()
plt.ylabel("$Q(t)$",fontsize=20)
plt.xlabel("$t/T$",fontsize=20)
plt.legend(loc=0,fontsize=16)
plt.savefig("example7_Q.pdf")
plt.figure()

plt.plot(times/T,Sent_time_1,marker='.',markersize=5,label="$S=1/2$")
plt.plot(times/T,Sent_time_2,marker='.',markersize=5,label="$S=1$")
plt.grid()
plt.ylabel("$S_{\mathrm{entanglement},L/2}(t)$",fontsize=20)
plt.xlabel("$t/T$",fontsize=20)
plt.legend(loc=0,fontsize=16)

plt.savefig("example7_S.pdf")
plt.show()

