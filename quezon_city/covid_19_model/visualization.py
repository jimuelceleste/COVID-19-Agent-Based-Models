# visualization.py

from covid_19_model.agents import PersonAgent
from covid_19_model.space import DistrictAgent, QuezonCity
from mesa_geo.visualization.MapModule import MapModule
from mesa.visualization.modules import ChartModule, TextElement

class SEIRChart(ChartModule):
    """SEIR Chart"""

    def __init__(self, district_number, chart_width = 300, chart_height = 125):
        data_collector = "data_collector_" + str(district_number)
        series = [
            {"Label": "S", "Color": "Green"},
            {"Label": "E", "Color": "Yellow"},
            {"Label": "I", "Color": "Red"},
            {"Label": "R", "Color": "Grey"}]
        data_collector_name = "data_collector_" + str(district_number)
        super().__init__(series, chart_height, chart_width, data_collector_name)

class SEIRLabel(TextElement):
    """SEIR Label"""

    def __init__(self, district_number):
        super().__init__()
        self.district_number = district_number
        self.district = "district" + str(district_number)

    def render(self, model):
        max_exposed = int(model.max_summary.at["max_exposed", self.district])
        max_exposed_time = int(model.max_summary.at["max_exposed_time", self.district])
        max_infected = int(model.max_summary.at["max_infected", self.district])
        max_infected_time = int(model.max_summary.at["max_infected_time", self.district])

        params = (
            self.district_number,
            max_exposed,
            max_exposed_time,
            max_infected,
            max_infected_time)

        return "District %i | max(E) = %i, t = %i | max(I) = %i, t = %i" % params

class Covid19ModelVisualization:

    MODEL_NAME = "COVID-19 Agent-Based Model"
    MODEL_DESCRIPTION = """
    This model simulates COVID-19 transmission in the six districts
    of Quezon City, Metro Manila, Philippines.
    """
    CHART_WIDTH = 300
    CHART_HEIGHT = 125
    MAP_ZOOM = 12
    MAP_WIDTH = 600
    MAP_HEIGHT = 600

    def __init__(self):
        self.modules = [
            MapModule(
                portrayal_method = self.agent_portrayal,
                view = QuezonCity.MAP_COORDS,
                zoom = self.MAP_ZOOM,
                map_height = self.MAP_HEIGHT,
                map_width = self.MAP_WIDTH)
            ]

        for i in range(6):
            district = "District " + str(i + 1)
            district_number = i + 1
            self.modules.append(SEIRLabel(district_number))
            self.modules.append(SEIRChart(district_number))

    def get_modules(self):
        return self.modules

    def agent_portrayal(self, agent):
        """Portrayal method of agents"""

        portrayal = dict()

        if isinstance(agent, PersonAgent):
            portrayal["radius"] = "1"

            if agent.state == "S":
                portrayal["color"] = "Green"
            elif agent.state == "E":
                portrayal["color"] = "Orange"
            elif agent.state == "I":
                portrayal["color"] = "Red"
            elif agent.state == "R":
                portrayal["color"] = "Grey"

        elif isinstance(agent, DistrictAgent):
            portrayal["color"] = "Blue"

        return portrayal
