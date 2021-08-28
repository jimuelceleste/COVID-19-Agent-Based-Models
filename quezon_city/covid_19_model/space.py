# space.py

from mesa_geo import GeoSpace, GeoAgent, AgentCreator
from shapely.geometry import Point
import random

class DistrictAgent(GeoAgent):
    """District GeoAgent"""
    def __init__(self, unique_id, model, shape):
        super().__init__(unique_id, model, shape)
        self.district = "district" + unique_id

    def __repr__(self):
        return "District " + str(self.unique_id)

class QuezonCity(GeoSpace):
    """Quezon City GeoSpace"""

    MAP_COORDS = [14.676208, 121.043861] # Quezon City
    quezon_city_districts_geojson = "covid_19_model/res/quezon_city_districts.geojson"
    quezon_city_geojson = "covid_19_model/res/quezon_city.geojson"

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.districts = self.instantiate_district_agents()

    def instantiate_district_agents(self):
        """Instantiates DistrictAgents"""
        # Instantiates an agent creator for DistrictAgent
        agent_creator = AgentCreator(
            DistrictAgent,
            {"model": self.model})

        # Instantiates DistrictAgents for the 6 districts
        district_agents = agent_creator.from_file(
            self.quezon_city_districts_geojson,
            unique_id = "DISTRICT")

        # Adds DistrictAgents to grid
        self.add_agents(district_agents)

        # Formats output as a dictionary
        return dict([("district" + str(i+1), district_agents[i]) for i in range(6)])

    def random_position(self, district):
        """
        Picks a random position inside the bounds of a given district.

        OPTIONAL: Refactor this code to implement an algorithm that has a
        better randomization strategy. (See: triangularization of polygons)
        """
        polygon = self.districts[district].shape
        x_min, y_min, x_max, y_max = polygon.bounds

        random_pos = ()
        flag = True
        while flag:
            # Picks a random point baed on polygon bounds
            random_pos = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))

            # Checks if random point is inside the polygon
            if polygon.contains(Point(random_pos[0], random_pos[1])):
                flag = False

        return random_pos

    def get_district(self, point, current_district):
        output = current_district

        for i in range(6):
            district = self.districts["district" + str(i + 1)]
            if district.shape.contains(point):
                output = "district" + district.unique_id
                break

        return output