import pytest
from app.services.logistics_service import LogisticsService
from app.models.container import Container
from app.models.ship import Ship

def test_cartesian_distance():
    # Distance between (0,0) and (3,4) = 5.0
    dist = LogisticsService.calculate_distance(0.0, 0.0, 3.0, 4.0)
    assert dist == 5.0

def test_fuel_consumption_formula():
    c1 = Container(id=1, type="Basic", weight=20.0)
    c2 = Container(id=2, type="Heavy", weight=40.0)
    c3 = Container(id=3, type="Refrigerated", weight=30.0)
    c4 = Container(id=4, type="Liquid", weight=35.0)

    containers = [c1, c2, c3, c4]
    distance = 100.0

    # cargo weight = 125
    # multiplier = 1.0 + (0.0005 * 125) + (0.10 * 1) + (0.15 * 1) + (0.20 * 1)
    # multiplier = 1.0 + 0.0625 + 0.10 + 0.15 + 0.20 = 1.5125
    # fuel = 100 * 1.5125 = 151.25
    fuel = LogisticsService.calculate_fuel_consumption(distance, containers)
    assert fuel == 151.25

def test_ship_cargo_weight_limit_validation():
    ship = Ship(id=1, name="Test Ship", max_weight=50.0, heavy_limit=5, refrigerated_limit=5, liquid_limit=5)
    c1 = Container(id=10, type="Basic", weight=30.0)
    c2 = Container(id=11, type="Heavy", weight=30.0)

    ship.containers = [c1]
    
    # Adding c2 will make total weight 60.0 > max_weight 50.0 -> raise ValueError
    with pytest.raises(ValueError) as exc:
        LogisticsService.validate_ship_cargo(ship, c2, adding=True)
    assert "exceeds ship maximum capacity" in str(exc.value)
