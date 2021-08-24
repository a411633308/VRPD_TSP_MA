
from Classes.methods.SA_Controller import SA_Controller

if __name__ == '__main__':
    sa_controller = SA_Controller()
    sa_controller.sa_optimize_fn()
    # sa_controller.constr_energy_dro()
    # sa_controller.constr_connectivity()
    # sa_controller.initial_solution()
    # sa_controller.constr_con()
    # sa_controller.random_walk_dro()