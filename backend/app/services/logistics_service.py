import math
from typing import List
from app.models.ship import Ship
from app.models.container import Container
from app.models.port import Port

class LogisticsService:
    @staticmethod
    def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
        """Cartesian distance formula sqrt((x2-x1)^2 + (y2-y1)^2)"""
        return round(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2), 2)

    @staticmethod
    def calculate_fuel_consumption(distance: float, containers: List[Container]) -> float:
        """
        Fuel formula based on distance, total cargo weight, and container types.
        Fuel = Distance * (1.0 + 0.0005 * total_cargo_weight + 0.10 * n_heavy + 0.15 * n_refrigerated + 0.20 * n_liquid)
        """
        total_cargo_weight = sum(c.weight for c in containers)
        n_heavy = sum(1 for c in containers if c.type == "Heavy")
        n_refrigerated = sum(1 for c in containers if c.type == "Refrigerated")
        n_liquid = sum(1 for c in containers if c.type == "Liquid")

        multiplier = (
            1.0 +
            (0.0005 * total_cargo_weight) +
            (0.10 * n_heavy) +
            (0.15 * n_refrigerated) +
            (0.20 * n_liquid)
        )
        return round(distance * multiplier, 2)

    @staticmethod
    def validate_ship_cargo(ship: Ship, candidate_container: Container = None, adding: bool = True):
        """
        Validates all SRS constraints for cargo on a ship:
        1. Maximum cargo weight limit
        2. Heavy container limit
        3. Refrigerated container limit
        4. Liquid container limit
        """
        current_containers = list(ship.containers)
        if candidate_container and adding:
            current_containers.append(candidate_container)
        elif candidate_container and not adding:
            current_containers = [c for c in current_containers if c.id != candidate_container.id]

        total_weight = sum(c.weight for c in current_containers)
        if total_weight > ship.max_weight:
            raise ValueError(f"Cargo weight ({total_weight} tons) exceeds ship maximum capacity ({ship.max_weight} tons).")

        heavy_count = sum(1 for c in current_containers if c.type == "Heavy")
        if heavy_count > ship.heavy_limit:
            raise ValueError(f"Heavy containers count ({heavy_count}) exceeds ship limit ({ship.heavy_limit}).")

        refrigerated_count = sum(1 for c in current_containers if c.type == "Refrigerated")
        if refrigerated_count > ship.refrigerated_limit:
            raise ValueError(f"Refrigerated containers count ({refrigerated_count}) exceeds ship limit ({ship.refrigerated_limit}).")

        liquid_count = sum(1 for c in current_containers if c.type == "Liquid")
        if liquid_count > ship.liquid_limit:
            raise ValueError(f"Liquid containers count ({liquid_count}) exceeds ship limit ({ship.liquid_limit}).")

        return True
