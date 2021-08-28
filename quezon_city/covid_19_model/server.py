# server.py

from mesa_geo.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from covid_19_model.visualization import Covid19ModelVisualization
from covid_19_model.space import QuezonCity
from covid_19_model.model import Covid19Model
from covid_19_model.utils import parse_json

# Visualization
model_visualization = Covid19ModelVisualization()
visualization_elements = model_visualization.get_modules()
model_name = model_visualization.MODEL_NAME
model_description = model_visualization.MODEL_DESCRIPTION

# Model inputs
model_params = {
    "model_desc": UserSettableParameter('static_text', value = model_description),
    "variable_params": parse_json("variable_parameters.json"),
    "fixed_params": parse_json("fixed_parameters.json"),
}

# Instantiates ModularServer
server = ModularServer(
    model_cls = Covid19Model,
    visualization_elements = visualization_elements,
    name = model_name,
    model_params = model_params)

# Sets the server port
server.port = 8521
