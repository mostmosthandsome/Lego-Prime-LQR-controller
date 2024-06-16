import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# from .fuzzy import FuzzyPIDController

from scipy.linalg import solve_continuous_are

class CartPoleSim():
    def __init__(self, 
                 state, 
                 length=1.0, 
                 cart_mass=1.0, 
                 pole_mass=0.1, 
                 damping=0.0, 
                 gravity=9.81, 
                 dt=0.01,
                 ctrl_dt=0.01):
        self._length = length
        self._cart_mass = cart_mass
        self._pole_mass = pole_mass
        self._damping = damping
        self._gravity = gravity

        self.state = state
        self.init_state = state
        self._dt = dt
        self._ctrl_dt = ctrl_dt

        # Initialize variables for animation
        self.fig, self.ax = plt.subplots()
        self.cart = plt.Rectangle((0, -0.05), 0.2, 0.1, fill=True, color='blue')
        self.pole, = self.ax.plot([], [], lw=2, color='black')
        self.ax.set_xlim(-5.0, 5.0)
        self.ax.set_ylim(-self._length - 0.1, self._length + 0.1)
        self.ax.set_aspect('equal')
        self.ax.grid()

        # Add cart and pole to the plot
        self.ax.add_patch(self.cart)
        self.pole, = self.ax.plot([], [], lw=2, color='black')

        # fuzzy PID controller design
        # self.fuzzy_pid_controller = FuzzyPIDController()

    async def _real_linearized_system(self):
        # x, x_dot, theta, theta_dot = self.state
        g = self._gravity
        m_c = self._cart_mass
        m_p = self._pole_mass
        l = self._length
        A = np.array([
            [0, 1],
            [(m_c + m_p) * g / (m_c * l), 0]
        ])
        B = np.array([
            [0],
            [-1 / (m_c * l)]
        ])
        return A, B

    def _linearized_system(self):
        x, x_dot, theta, theta_dot = self.state
        g = self._gravity
        m_c = self._cart_mass
        m_p = self._pole_mass
        l = self._length

        A = np.array([
            [0, 1, 0, 0],
            [0, -self._damping/m_c, -(m_p * g) / m_c, 0],
            [0, 0, 0, 1],
            [0, self._damping / (m_c * l), (m_c + m_p) * g / (m_c * l), 0]
        ])

        B = np.array([
            [0],
            [1 / m_c],
            [0],
            [-1 / (m_c * l)]
        ])

        return A, B
    
    def _linear_dynamics(self, t, state, F):
        A, B = self._linearized_system()
        return A @ state + np.squeeze(B * F)

    def _dynamics(self, t, state, F):
        x, x_dot, theta, theta_dot = state
        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)

        # Equations of motion
        total_mass = self._cart_mass + self._pole_mass
        pole_mass_length = self._pole_mass * self._length

        temp = (F + pole_mass_length * theta_dot**2 * sin_theta) / total_mass
        theta_acc = (self._gravity * sin_theta - cos_theta * temp) / (self._length * (4/3 - self._pole_mass * cos_theta**2 / total_mass))
        x_acc = temp - pole_mass_length * theta_acc * cos_theta / total_mass

        return [x_dot, x_acc, theta_dot, theta_acc]
    
    def step(self, F):
        for _ in range(int(self._ctrl_dt / self._dt)):
            self.state = solve_ivp(self._dynamics, [0, self._dt], self.state, args=(F,), t_eval=[0, self._dt]).y[:, -1]
            self.render()
        return self.state
    
    def render(self):
        x, _, theta, _ = self.state
        cart_x = x
        cart_y = 0
        pole_x = [cart_x, cart_x + self._length * np.sin(theta)]
        pole_y = [cart_y, self._length * np.cos(theta)]
        self.cart.set_xy([cart_x - 0.1, cart_y - 0.05])
        self.pole.set_data(pole_x, pole_y)
        plt.pause(self._dt)


# Example usage:
if __name__ == '__main__':
    initial_state = [0.0, 0.0, np.pi/4, 0.0]  # [x, x_dot, theta, theta_dot]
    cart_pole = CartPoleSim(initial_state, length=1.0, cart_mass=1.0, pole_mass=0.1, damping=0.0, gravity=9.81)

    for i in range(1000):
        # set sin wave as input
        F = np.sin(i/10)
        cart_pole.step(F)
    plt.show()