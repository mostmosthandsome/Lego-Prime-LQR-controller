import numpy as np
from scipy.linalg import solve_continuous_are

import casadi as ca
class D:
    async def print_hello(self):
        print("hello")
class LQR():
    def __init__(self, env):
        self.env = env

    async def _lqr_controller(self, Q, R, x_eq):
        A, B = self.env._linearized_system()

        # Solve the continuous-time Algebraic Riccati Equation (ARE)
        P = solve_continuous_are(A, B, Q, R)

        # Compute the LQR gain matrix K
        K = np.linalg.inv(R) @ B.T @ P

        # Compute the control input u = -K(x - x_eq)
        F = -K @ (self.env.state - x_eq)
        if isinstance(F, np.ndarray):
            F = F[0]
        return F
    
    async def _real_lqr_controller(self, Q, R, x_eq, degree, d_degree):
        theta = degree * np.pi / 180
        d_theta = d_degree * np.pi / 180
        A, B = await self.env._real_linearized_system()
        # Solve the continuous-time Algebraic Riccati Equation (ARE)
        P = solve_continuous_are(A, B, Q, R)

        # Compute the LQR gain matrix K
        K = np.linalg.inv(R) @ B.T @ P

        # Compute the control input u = -K(x - x_eq)
        F = -K @ ([theta, d_theta] - x_eq)
        if isinstance(F, np.ndarray):
            F = F[0]
        return F / (self.env._cart_mass + self.env._pole_mass)
        
    
class MPC():
    def __init__(self, env):
        self.env = env
    
    def _mpc_controller(self, Q, R, x_eq, horizon):
        x = ca.MX.sym('x', 4, horizon+1)
        u = ca.MX.sym('u', 1, horizon)

        cost = 0
        for k in range(horizon):
            cost += ca.mtimes([x[:, k].T, Q, x[:, k]]) + ca.mtimes([u[:, k].T, R, u[:, k]])

        constraints = []
        A, B = self.env._linearized_system()
        Ad = np.eye(4) + A * self.env._dt
        Bd = B.reshape(4, 1) * self.env._dt
        for k in range(horizon):
            x_next = Ad @ x[:, k] + Bd * u[:, k]
            constraints.append(x[:, k+1] == x_next)

        constraints += [x[:, 0] == self.env.init_state]

        opti = ca.Opti()
        opti.minimize(cost)
        opti.subject_to(constraints)

        solver_opts = {'ipopt': {'print_level': 0}}
        opti.solver('ipopt', solver_opts)

        x_opt = np.zeros((4, horizon+1))
        u_opt = np.zeros((1, horizon))

        for t in range(horizon):
            sol = opti.solve()
            x_opt[:, t+1] = sol.value(x[:, t+1])
            u_opt[:, t] = sol.value(u[:, t])
        
        return u_opt[:, 0]
    