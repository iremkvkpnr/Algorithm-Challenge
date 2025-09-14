from ortools.constraint_solver import routing_enums_pb2, pywrapcp
import time
from typing import Dict, List, Optional

from ..schemas.request_models import VRPInput
from ..schemas.response_models import VRPOutput, Route, VRPMetadata
from ..exceptions import (
    VRPError, VRPSystemError,
    ErrorCode
)
from ..repositories.vrp_repository import VRPRepository
from ..validators.business_validator import BusinessValidator
from ..utils.logger import get_service_logger

logger = get_service_logger()


class VRPService:
    def __init__(self, time_limit: int = 30, solution_limit: int = 100, repository: Optional[VRPRepository] = None):
        self.time_limit = time_limit
        self.solution_limit = solution_limit
        self.repository = repository or VRPRepository()
        self.validator = BusinessValidator()

    def solve(self, data: VRPInput) -> VRPOutput:
        start = time.time()
        
        try:
            self.validator.validate_business_rules(data)
            
            demands = {j.location_index: (j.delivery[0] if j.delivery else 1) for j in data.jobs}
            services = {j.location_index: (j.service or 0) for j in data.jobs}

            manager, routing = self._create_model(data)

            # if any service times -> register time callback 
            time_cb = None
            if any(j.service for j in data.jobs):
                time_cb = self._add_time_dimension(manager, routing, data, services)

            if any(v.capacity for v in data.vehicles):
                self._add_capacity_dimension(manager, routing, data, demands)

            # time_cb (travel+service) if present
            if time_cb is not None:
                routing.SetArcCostEvaluatorOfAllVehicles(time_cb)
            else:
                self._set_distance_evaluator(manager, routing, data.matrix)

            params = self._search_parameters()
            solution = routing.SolveWithParameters(params)
            
            if not solution:
                raise VRPSystemError(
                    ErrorCode.NO_SOLUTION_FOUND,
                    f"OR-Tools solver could not find a solution for {len(data.vehicles)} vehicles and {len(data.jobs)} jobs"
                )

            routes = self._extract_routes(manager, routing, solution, data, demands, services)
            self._validate_routes(routes, data)

            solve_time = time.time() - start
            
            if solve_time > self.time_limit:
                logger.warning(f"Solver exceeded time limit: {solve_time:.2f}s > {self.time_limit}s")
                raise VRPSystemError(
                    ErrorCode.SYSTEM_ERROR,
                    f"Solver exceeded time limit: {solve_time:.2f}s > {self.time_limit}s"
                )

            total = sum(r.delivery_duration for r in routes.values())

            logger.info("Solved in %.2fs, total=%s", solve_time, total)
            
            result = self._convert_to_output_dto(routes, total, solve_time, solution.ObjectiveValue())
            

            if self.repository:
                try:
                    vehicle_ids = self.repository.save_vehicles(data.vehicles)
                    job_ids = self.repository.save_jobs(data.jobs)
                    solution_id = self.repository.save_solution(result, data, vehicle_ids, job_ids)
                    logger.info(f"Solution saved to MongoDB with id: {solution_id}")
                except Exception as e:
                    logger.warning(f"Failed to save solution to database: {str(e)}")
            
            return result
            
        except (VRPError, VRPSystemError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in VRP solver: {str(e)}", exc_info=True)
            raise VRPSystemError(
                ErrorCode.SOLVER_ERROR,
                f"Unexpected error in VRP solver: {str(e)}",
                details={
                    'exception_type': type(e).__name__,
                    'original_message': str(e)
                }
            )

    
    def _convert_to_output_dto(self, routes: Dict[str, Route], total: int, solve_time: float, objective_value: int) -> VRPOutput:
        metadata = VRPMetadata(
            solve_time_seconds=solve_time,
            algorithm="OR-Tools",
            objective_value=objective_value
        )
        
        return VRPOutput(
            total_delivery_duration=total,
            routes=routes,
            metadata=metadata
        )

    def _augment_matrix_with_sink(self, matrix: List[List[int]]):
        n = len(matrix)
        # new matrix with sink node
        new_matrix = []
        for row in matrix:
            new_matrix.append(row + [0])  
        new_matrix.append([0] * (n + 1)) 
        sink_index = n
        return new_matrix, sink_index

    def _create_model(self, data: VRPInput):
        n_loc = len(data.matrix)
        n_veh = len(data.vehicles)

        starts = [int(v.start_index) for v in data.vehicles]

        matrix, sink_index = self._augment_matrix_with_sink(data.matrix)

        ends = [int(sink_index)] * n_veh

        self._original_matrix = data.matrix
        self._matrix = matrix
        self._sink_index = sink_index

        mgr = pywrapcp.RoutingIndexManager(len(matrix), n_veh, starts, ends)
        routing = pywrapcp.RoutingModel(mgr)
        return mgr, routing

    def _set_distance_evaluator(self, manager, routing, matrix: List[List[int]]):
        def dist_cb(from_index, to_index):
            return self._matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]
        cb_idx = routing.RegisterTransitCallback(dist_cb)
        routing.SetArcCostEvaluatorOfAllVehicles(cb_idx)
        return cb_idx

    def _add_capacity_dimension(self, manager, routing, data: VRPInput, demands: Dict[int, int]):
        def demand_cb(index):
            node = manager.IndexToNode(index)

            if node == self._sink_index:
                return 0
            return demands.get(node, 0)
        demand_idx = routing.RegisterUnaryTransitCallback(demand_cb)
        total_demand = sum(demands.values()) or 1_000_000
        caps = [v.capacity[0] if v.capacity else total_demand for v in data.vehicles]
        routing.AddDimensionWithVehicleCapacity(demand_idx, 0, caps, True, "Capacity")

    def _add_time_dimension(self, manager, routing, data: VRPInput, services: Dict[int, int]):
        def time_cb(from_index, to_index):
            f = manager.IndexToNode(from_index)
            t = manager.IndexToNode(to_index)

            travel = self._matrix[f][t]

            service = 0 if t == self._sink_index else services.get(t, 0)
            return travel + service
        idx = routing.RegisterTransitCallback(time_cb)
        
        max_travel = max(
        sum(row) for row in self._original_matrix
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

    def _extract_routes(self, manager, routing, solution, data: VRPInput, demands: Dict[int, int], services: Dict[int, int]) -> Dict[str, Route]:
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
            end_index = start_index  # default to start if no moves

            index = routing.Start(v_idx)
            prev_node = manager.IndexToNode(index)

            if prev_node in loc_jobs:
                for j in loc_jobs[prev_node]:
                    jobs_seq.append(j.id)
                    capacity_used += demands.get(prev_node, 0)

            while not routing.IsEnd(index):
                from_node = manager.IndexToNode(index)
                next_index = solution.Value(routing.NextVar(index))
                to_node = manager.IndexToNode(next_index)

                if not routing.IsEnd(next_index) or to_node != self._sink_index:
                    if 0 <= from_node < len(data.matrix) and 0 <= to_node < len(data.matrix):
                        travel += data.matrix[from_node][to_node]

                if not routing.IsEnd(next_index) and to_node != self._sink_index and to_node in loc_jobs:
                    for j in loc_jobs[to_node]:
                        jobs_seq.append(j.id)
                        capacity_used += demands.get(to_node, 0)
                        service_sum += services.get(to_node, 0)

                # Update end location -> use the last  location before sink
                if not routing.IsEnd(next_index) and to_node != self._sink_index:
                    end_index = to_node
                elif routing.IsEnd(next_index) and to_node == self._sink_index:

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

    def _validate_routes(self, routes: Dict[str, Route], data: VRPInput):
        self.validator.validate_solution(routes, data)
