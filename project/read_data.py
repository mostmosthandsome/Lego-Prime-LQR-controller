import numpy as np

degree = np.load("degree.npy")
angular = np.load("angular.npy")
speed = np.load("speed.npy")
control = np.load("control.npy")
print(degree)
print(angular)
for i in control:
    print(i)