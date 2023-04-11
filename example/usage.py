import random
import sys
from itertools import product
from pathlib import Path
from typing import List

import routingblocks
import routingblocks_cvrp as cvrp
import vrplib


def read_instance(instance_name: str, basedir: Path = Path('instances/')):
    instance_file = basedir / instance_name
    if not instance_file.exists():
        basedir.mkdir(parents=True, exist_ok=True)
        # Download the CVRP problem instance if it does not exist
        vrplib.download_instance(instance_name, str(instance_file))

    # Load the CVRP problem instance
    return vrplib.read_instance(instance_file)


def create_cvrp_instance(instance):
    # Create CVRP vertices
    n = len(instance['demand'])
    vertices = [
        cvrp.create_cvrp_vertex(i, str(i), False, i == instance['depot'][0], cvrp.CVRPVertexData(instance['demand'][i]))
        for i in range(n)]
    # Create CVRP arcs
    arcs = [
        [cvrp.create_cvrp_arc(cvrp.CVRPArcData(instance['edge_weight'][i][j])) for j in range(n)] for i in range(n)
    ]

    return routingblocks.Instance(vertices, arcs, len(vertices))


def main(instance_name: str):
    instance = read_instance(instance_name)
    cpp_instance = create_cvrp_instance(instance)
    evaluation = cvrp.CVRPEvaluation(instance['capacity'])

    max_demand = instance['demand'].max()
    max_dist = instance['edge_weight'].max()

    # Set the penalty factor for load violations
    evaluation.overload_penalty_factor = max_dist / max_demand

    # Create a simple solution by applying local search to a random solution
    randgen = routingblocks.Random()
    random_solution = generate_random_solution(evaluation, cpp_instance, randgen)
    optimized_solution = optimize_solution(evaluation, cpp_instance, random_solution)
    print(optimized_solution)
    print("Cost:", optimized_solution.cost, optimized_solution.cost_components)


def optimize_solution(evaluation: routingblocks.Evaluation, instance: routingblocks.Instance,
                      solution: routingblocks.Solution):
    # Create a local search solver
    solver = routingblocks.LocalSearch(instance, evaluation, evaluation)
    # Create some operators
    # Create the arc set - by default all arcs are included
    full_arc_set = routingblocks.ArcSet(len(instance))
    operators = [
        routingblocks.SwapOperator_0_1(instance, full_arc_set),
        routingblocks.SwapOperator_1_1(instance, full_arc_set),
        routingblocks.InterRouteTwoOptOperator(instance, full_arc_set)
    ]
    # Optimize the solution (inplace)
    solver.optimize(solution, operators)
    return solution


def distribute_randomly(sequence, num_subsequences: int, randgen=random.Random()) -> List[List]:
    subsequences = [[] for _ in range(num_subsequences)]
    for item in sequence:
        subsequences[randgen.randint(0, len(subsequences) - 1)].append(item)
    return subsequences


def generate_random_solution(evaluation: routingblocks.Evaluation, instance: routingblocks.Instance,
                             random: routingblocks.Random):
    customers = [x.vertex_id for x in instance.customers]
    sol = routingblocks.Solution(evaluation, instance,
                                 [routingblocks.create_route(evaluation, instance, r) for r in
                                  distribute_randomly(customers, instance.fleet_size,
                                                      random)])
    return sol


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <instance_name>')
        sys.exit(1)
    main(sys.argv[1])
