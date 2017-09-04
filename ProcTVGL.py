
from SerialTVGL import SerialTVGL
import multiprocessing
import mp_workers_proc as mp
import numpy as np


class ProcTVGL(SerialTVGL):

    def __init__(self, filename, blocks=10,
                 lambd=30, beta=4, processes=2):
        super(ProcTVGL, self).__init__(filename, blocks,
                                       lambd, beta, processes)
        self.chunk = int(np.round(self.blocks/float(self.processes)))

    def theta_update(self):
        procs = []
        out_queue = multiprocessing.Queue()
        for i in range(self.processes):
            if i == self.processes - 1:
                p = multiprocessing.Process(
                    target=mp.theta_update,
                    args=((self.thetas[self.chunk * i:],
                           self.z0s[self.chunk * i:],
                           self.z1s[self.chunk * i:],
                           self.z2s[self.chunk * i:],
                           self.u0s[self.chunk * i:],
                           self.u1s[self.chunk * i:],
                           self.u2s[self.chunk * i:],
                           self.emp_cov_mat[self.chunk * i:],
                           self.nju,
                           range(self.chunk * i, self.blocks)),
                          out_queue))
            else:
                p = multiprocessing.Process(
                    target=mp.theta_update,
                    args=((self.thetas[self.chunk * i:self.chunk*(i+1)],
                           self.z0s[self.chunk * i:self.chunk*(i+1)],
                           self.z1s[self.chunk * i:self.chunk*(i+1)],
                           self.z2s[self.chunk * i:self.chunk*(i+1)],
                           self.u0s[self.chunk * i:self.chunk*(i+1)],
                           self.u1s[self.chunk * i:self.chunk*(i+1)],
                           self.u2s[self.chunk * i:self.chunk*(i+1)],
                           self.emp_cov_mat[self.chunk * i:self.chunk*(i+1)],
                           self.nju,
                           range(self.chunk * i, self.chunk*(i+1))),
                          out_queue))
            procs.append(p)
            p.start()
        results = {}
        for i in range(self.processes):
            results.update(out_queue.get())
        for i in results:
            self.thetas[i] = results[i]
        for p in procs:
            p.join()

#    def z_update(self):
#        """ z0-update """
#        inputs = [(self.thetas[i], self.u0s[i], self.lambd, self.rho)
#                  for i in range(self.blocks)]
#        pool = multiprocessing.Pool(self.processes)
#        self.z0s = pool.map(mp.z0_update, inputs)
#        pool.close()
#        """ z1-z2-update """
#        inputs = [(self.thetas[i], self.thetas[i-1],
#                   self.u1s[i], self.u1s[i-1], self.u2s[i],
#                   self.beta, self.rho)
#                  for i in range(1, self.blocks)]
#        pool = multiprocessing.Pool(self.processes)
#        zs = pool.map(mp.z1_z2_update, inputs)
#        pool.close()
#        for i in range(self.blocks - 1):
#            self.z1s[i] = zs[i][0]
#            self.z2s[i+1] = zs[i][1]
#
#    def u_update(self):
#        """ u0-update """
#        inputs = [(self.thetas[i], self.u0s[i], self.z0s[i])
#                  for i in range(self.blocks)]
#        pool = multiprocessing.Pool(self.processes)
#        self.u0s = pool.map(mp.u0_update, inputs)
#        pool.close()
#        """ u1-update """
#        inputs = [(self.thetas[i], self.u1s[i], self.z1s[i])
#                  for i in range(self.blocks - 1)]
#        pool = multiprocessing.Pool(self.processes)
#        u1s = pool.map(mp.u1_update, inputs)
#        self.u1s[0:self.blocks - 1] = u1s
#        pool.close()
#        """ u2-update """
#        inputs = [(self.thetas[i], self.u2s[i], self.z2s[i])
#                  for i in range(1, self.blocks)]
#        pool = multiprocessing.Pool(self.processes)
#        u2s = pool.map(mp.u2_update, inputs)
#        self.u2s[1:self.blocks] = u2s
#        pool.close()