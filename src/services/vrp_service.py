from ortools.constraint_solver import routing_enums_pb2, pywrapcp
import time
from typing import Dict, List

from ..schemas.input import VRPInputDTO
from ..schemas.output import VRPOutputDTO, RouteDTO, VRPMetadataDTO
from ..models.domain import VRPProblem, VRPSolution, Vehicle, Job, Route
from ..exceptions import VRPSolverError, VRPTimeoutError
from ..utils.logger import get_service_logger

logger = get_service_logger()


class VRPService:
    def __init__(self, time_limit: int = 30, solution_limit: int = 100):
        self.time_limit = time_limit
        self.solution_limit = solution_limit

    def solve(self, data: VRPInputDTO) -> VRPOutputDTO:
        start = time.time()
        
        try:
            problem = self._convert_to_domain(data)
            
            demands = {j.location_index: (j.delivery[0] if j.delivery else 1) for j in problem.jobs}
            services = {j.location_index: (j.service or 0) for j in problem.jobs}

            manager, routing = self._create_model(problem)

            # if any service times -> register time callback 
            time_cb = None
            if any(j.service for j in problem.jobs):
                time_cb = self._add_time_dimension(manager, routing, problem, services)

            if any(v.capacity for v in problem.vehicles):
                self._add_capacity_dimension(manager, routing, problem, demands)

            # time_cb (travel+service) if present
            if time_cb is not None:
                routing.SetArcCostEvaluatorOfAllVehicles(time_cb)
            else:
                self._set_distance_evaluator(manager, routing, problem.matrix)

            params = self._search_parameters()
            solution = routing.SolveWithParameters(params)
            
            if not solution:
                raise VRPSolverError("No solution found by OR-Tools solver")

            routes = self._extract_routes(manager, routing, solution, problem, demands, services)
            self._validate_routes(routes, problem)

            solve_time = time.time() - start
            
            if solve_time > self.time_limit:
                logger.warning(f"Solver exceeded time limit: {solve_time:.2f}s > {self.time_limit}s")

            total = sum(r.delivery_duration for r in routes.values())

            logger.info("Solved in %.2fs, total=%s", solve_time, total)
            
            return self._convert_to_output_dto(routes, total, solve_time, solution.ObjectiveValue())
            
        except VRPSolverError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in VRP solver: {str(e)}")
            raise VRPSolverError(f"Solver failed: {str(e)}")

    def _convert_to_domain(self, data: VRPInputDTO) -> VRPProblem:
        vehicles = [Vehicle(id=v.id, start_index=v.start_index, capacity=v.capacity) for v in data.vehicles]
        jobs = [Job(id=j.id, location_index=j.location_index, delivery=j.delivery, service=j.service) for j in data.jobs]
        return VRPProblem(vehicles=vehicles, jobs=jobs, matrix=data.matrix)
    
    def _convert_to_output_dto(self, routes: Dict[str, Route], total: int, solve_time: float, objective_value: int) -> VRPOutputDTO:
        route_dtos = {}
        for vehicle_id, route in routes.items():
            route_dtos[vehicle_id] = RouteDTO(
                jobs=route.jobs,
                delivery_duration=route.delivery_duration,
                capacity_used=route.capacity_used,
                total_service_time=route.total_service_time,
                total_distance=route.total_distance,
                start_location=route.start_location,
                end_location=route.end_location
            )
        
        metadata = VRPMetadataDTO(
            solve_time_seconds=solve_time,
            algorithm="OR-Tools",
            objective_value=objective_value
        )
        
        return VRPOutputDTO(
            total_delivery_duration=total,
            routes=route_dtos,
            metadata=metadata
        )

    def _create_model(self, data: VRPProblem):
        n_loc = len(data.matrix)
        n_veh = len(data.vehicles)
        starts = [v.start_index for v in data.vehicles]
        ends = starts[:]  # vehicles end at start 
        mgr = pywrapcp.RoutingIndexManager(n_loc, n_veh, starts, ends)
        routing = pywrapcp.RoutingModel(mgr)
        return mgr, routing

    def _set_distance_evaluator(self, manager, routing, matrix: List[List[int]]):
        def dist_cb(from_index, to_index):
            return matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]
        cb_idx = routing.RegisterTransitCallback(dist_cb)
        routing.SetArcCostEvaluatorOfAllVehicles(cb_idx)
        return cb_idx

    def _add_capacity_dimension(self, manager, routing, data: VRPProblem, demands: Dict[int, int]):
        def demand_cb(index):
            node = manager.IndexToNode(index)
            return demands.get(node, 0)
        demand_idx = routing.RegisterUnaryTransitCallback(demand_cb)
        total_demand = sum(demands.values()) or 1_000_000
        caps = [v.capacity[0] if v.capacity else total_demand for v in data.vehicles]
        routing.AddDimensionWithVehicleCapacity(demand_idx, 0, caps, True, "Capacity")

    def _add_time_dimension(self, manager, routing, data: VRPProblem, services: Dict[int, int]):
        def time_cb(from_index, to_index):
            f = manager.IndexToNode(from_index)
            t = manager.IndexToNode(to_index)
            travel = data.matrix[f][t]
            service = services.get(t, 0)
            return travel + service
        idx = routing.RegisterTransitCallback(time_cb)
        
        # Max routing calculate 
        max_travel = max(
        sum(row) for row in data.matrix
        )  
        max_service = sum(services.values())  
        horizon_max = max_travel + max_service
        slack_max = int(horizon_max * 0.1)  # %10 slack
        routing.AddDimension(idx,slack_max, horizon_max, False, "Time")
        return idx

    def _search_parameters(self):
        params = pywrapcp.DefaultRoutingSearchParameters()
        params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        params.time_limit.FromSeconds(self.time_limit)
        params.solution_limit = self.solution_limit
        return params

    def _extract_routes(self, manager, routing, solution, data: VRPProblem, demands: Dict[int, int], services: Dict[int, int]) -> Dict[str, Route]:
        loc_jobs: Dict[int, List] = {}
        for job in data.jobs:
            loc_jobs.setdefault(job.location_index, []).append(job)

        out: Dict[str, Route] = {}
        for v_idx, vehicle in enumerate(data.vehicles):
            jobs_seq: List[int] = []
            travel = 0
            service_sum = 0
            capacity_used = 0
            start_index = vehicle.start_index
            end_index = start_index

            index = routing.Start(v_idx)

            start_node = manager.IndexToNode(index)
            if start_node in loc_jobs:
                for j in loc_jobs[start_node]:
                    jobs_seq.append(j.id)
                    capacity_used += demands.get(start_node, 0)

            while not routing.IsEnd(index):
                from_node = manager.IndexToNode(index)
                next_index = solution.Value(routing.NextVar(index))
                to_node = manager.IndexToNode(next_index)

                if 0 <= from_node < len(data.matrix) and 0 <= to_node < len(data.matrix):
                    travel += data.matrix[from_node][to_node]

                if not routing.IsEnd(next_index) and to_node in loc_jobs:
                    for j in loc_jobs[to_node]:
                        jobs_seq.append(j.id)
                        capacity_used += demands.get(to_node, 0)
                        service_sum += services.get(to_node, 0)

                if routing.IsEnd(next_index):
                    end_index = from_node

                index = next_index

            out[str(vehicle.id)] = Route(
                jobs=jobs_seq,
                delivery_duration=travel + service_sum,
                capacity_used=capacity_used,
                total_service_time=service_sum,
                total_distance=travel,
                start_location=start_index,
                end_location=end_index
            )
        return out

    def _validate_routes(self, routes: Dict[str, Route], data: VRPProblem):
        assigned = [j for r in routes.values() for j in r.jobs]
        if set(assigned) != set(job.id for job in data.jobs):
            missing = set(job.id for job in data.jobs) - set(assigned)
            raise Exception(f"Job assignment mismatch. Missing: {missing}")

        for v in data.vehicles:
            if v.capacity:
                r = routes.get(str(v.id))
                if r:
                    capacity_used = sum(job.delivery[0] if job.delivery else 0 for job in data.jobs if job.id in r.jobs)
                    if capacity_used > v.capacity[0]:
                        raise Exception(f"Vehicle {v.id} capacity exceeded: {capacity_used} > {v.capacity[0]}")
