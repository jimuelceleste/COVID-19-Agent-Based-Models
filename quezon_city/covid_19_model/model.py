# model.py

from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from covid_19_model.enum.immunity import Immunity
from covid_19_model.enum.state import State
from covid_19_model.agents import PersonAgent
from covid_19_model.space import QuezonCity
from covid_19_model.data_collectors import *
from covid_19_model.utils import coin_toss
from shapely.geometry import Point
import numpy as np
import pandas as pd
import random

class Covid19Model(Model):
    """Covid19 Agent-Based Model for Quezon City, Philippines"""

    def __init__(self, variable_params, fixed_params):
        """Initializes the model"""
        self.SEIR = self.initialize_SEIR_dictionary(variable_params)

        # Virus-Host Parameters
        self.transmission_rate = self.to_district_agegroup_matrix(fixed_params["transmission_rate"])
        self.incubation_rate = self.to_district_agegroup_matrix(fixed_params["incubation_rate"])
        self.mortality_rate = self.to_district_agegroup_matrix(fixed_params["mortality_rate"])
        self.recovery_rate = self.to_district_agegroup_matrix(fixed_params["recovery_rate"])
        self.recovery_period = fixed_params["recovery_period"]

        # Age-stratified infection expectation
        self.as_infection_expectation = fixed_params["as_infection_expectation"]
        self.incubation_rate = self.incubation_rate * self.as_infection_expectation

        # Behavioral- and disease-resistance factors
        self.wearing_mask_percentage = fixed_params["wearing_mask_percentage"]
        self.wearing_mask_protection = fixed_params["wearing_mask_protection"]
        self.physical_distancing_percentage = fixed_params["physical_distancing_percentage"]
        self.physical_distancing_protection = fixed_params["physical_distancing_protection"]
        self.with_low_immunity_percentage = fixed_params["with_low_immunity_percentage"]

        # Quarantine age-restriction policy
        self.min_age_restriction = fixed_params["min_age_restriction"]
        self.max_age_restriction = fixed_params["max_age_restriction"]

        # Agent movement configuration
        self.mobile_worker_percentage = fixed_params["mobile_worker_percentage"]
        self.agent_exposure_distance = fixed_params["agent_exposure_distance"]
        self.agent_mobility_range = fixed_params["agent_mobility_range"]

        # Instantiates scheduler and space for model
        self.schedule = RandomActivation(self)
        self.grid = QuezonCity(self)

        # Instantiates PersonAgents
        for compartment, state in (
            ("susceptible", State.SUSCEPTIBLE),
            ("exposed", State.EXPOSED),
            ("infected", State.INFECTED)
        ):
            self.instantiate_person_agents(
                variable_params[compartment],
                state,
                self.schedule,
                self.grid,
                self.wearing_mask_percentage,
                self.physical_distancing_percentage,
                self.mobile_worker_percentage)

        # Instantiates data collectors
        self.data_collector_1 = self.instantiate_data_collector("district1")
        self.data_collector_2 = self.instantiate_data_collector("district2")
        self.data_collector_3 = self.instantiate_data_collector("district3")
        self.data_collector_4 = self.instantiate_data_collector("district4")
        self.data_collector_5 = self.instantiate_data_collector("district5")
        self.data_collector_6 = self.instantiate_data_collector("district6")
        # self.data_collector_total = self.instantiate_data_collector("total")

        # Sets summary-related variables
        # self.summary = self.initialize_summary_dictionary()
        self.max_summary = self.initialize_max_summary()
        self.total_summary = self.initialize_total_summary()
        self.dead = self.district_agegroup_matrix()
        self.recovered = self.district_agegroup_matrix()
        self.steps = 0

        # Sets the running state of model to True
        self.running = True

    def district_agegroup_matrix(self, size=(9, 6)):
        districts = ["district%i" % (i+1) for i in range(6)]
        age_group = lambda group, size: "%i to %i" % (group * size, (group + 1) * size - 1)
        age_groups = [age_group(i, 10) for i in range(8)] + ["80+"]
        return pd.DataFrame(np.zeros(size), columns=districts, index=age_groups)

    def to_district_agegroup_matrix(self, data):
        districts = ["district%i" % (i+1) for i in range(6)]
        age_group = lambda group, size: "%i to %i" % (group * size, (group + 1) * size - 1)
        age_groups = [age_group(i, 10) for i in range(8)] + ["80+"]
        return pd.DataFrame(data, columns=districts, index=age_groups)

    def initialize_SEIR_dictionary(self, seir):
        """Initializes SEIR data holder"""
        districts = ["district%i" % (i+1) for i in range(6)]
        age_group = lambda group, size: "%i to %i" % (group * size, (group + 1) * size - 1)
        age_groups = [age_group(i, 10) for i in range(8)] + ["80+"]

        return {
            "S": pd.DataFrame(seir["susceptible"], columns=districts, index=age_groups),
            "E": pd.DataFrame(seir["exposed"], columns=districts, index=age_groups),
            "I": pd.DataFrame(seir["infected"], columns=districts, index=age_groups),
            "R": pd.DataFrame(seir["removed"], columns=districts, index=age_groups),
        }

    def initialize_max_summary(self):
        index = [
            "max_exposed",
            "max_exposed_time",
            "max_infected",
            "max_infected_time",
        ]
        districts = ["district%i" % (i+1) for i in range(6)]
        size = (len(index), len(districts))
        summary = pd.DataFrame(np.zeros(size), columns=districts, index=index)

        for district in districts:
            summary.at["max_exposed", district] = self.SEIR["E"].sum().sum()
            summary.at["max_exposed_time", district] = 0
            summary.at["max_infected", district] = self.SEIR["I"].sum().sum()
            summary.at["max_infected_time", district] = 0

        return summary

    def initialize_total_summary(self):
        index = [
            "total_exposed",
            "total_infected",
            "total_dead",
            "total_recovered",
        ]
        districts = ["district%i" % (i+1) for i in range(6)]
        size = (len(index), len(districts))

        return pd.DataFrame(np.zeros(size), columns=districts, index=index)

    def instantiate_data_collector(self, district):
        """Returns the datacollector for given district"""
        return DataCollector(
            model_reporters = {
                "S": get_susceptible_function(district),
                "E": get_exposed_function(district),
                "I": get_infected_function(district),
                "R": get_removed_function(district)
            })

    def instantiate_person_agents(
        self,
        population,
        state,
        schedule,
        grid,
        wearing_mask_percentage,
        physical_distancing_percentage,
        mobile_worker_percentage,
    ):
        """Instantiates PersonAgents"""

        # Nine age groups: 0-9, 10-19, ..., 80-89
        age_groups = [(i*10, i*10+9) for i in range(9)]
        age_group = lambda group, size: "%i to %i" % (group * size, (group + 1) * size - 1)
        age_groups_id = [age_group(i, 10) for i in range(8)] + ["80+"]

        for i, age_group_pop in enumerate(population):
            min_age, max_age = age_groups[i]

            for j, district_pop in enumerate(age_group_pop):
                district = "district" + str(j + 1)

                for k in range(int(district_pop)):
                    # Agent's properties
                    id = str(i) + str(j) + str(k) + state
                    age = random.randint(min_age, max_age)
                    wearing_mask = coin_toss(wearing_mask_percentage)
                    physical_distancing = coin_toss(physical_distancing_percentage)
                    mobile_worker = coin_toss(mobile_worker_percentage) if 18 <= age <= 60 else False

                    # Generates a random point for agent's position
                    pos_x, pos_y = self.grid.random_position(district)
                    shape = Point(pos_x, pos_y)

                    # Instantiates Agent
                    agent = PersonAgent(
                        unique_id = id,
                        model = self,
                        shape = shape,
                        district = district,
                        state = state,
                        age = age,
                        age_group = age_groups_id[i],
                        wearing_mask = wearing_mask,
                        physical_distancing = physical_distancing,
                        mobile_worker = mobile_worker)

                    # Adds agent to grid and scheduler
                    grid.add_agents(agent)
                    schedule.add(agent)

    def step(self):
        """Advances the model by one step"""
        # print(self.SEIR)
        self.steps += 1
        self.data_collector_1.collect(self)
        self.data_collector_2.collect(self)
        self.data_collector_3.collect(self)
        self.data_collector_4.collect(self)
        self.data_collector_5.collect(self)
        self.data_collector_6.collect(self)
        self.schedule.step()
        self.grid._recreate_rtree()

    def get_compartment(self, district, compartment):
        return self.SEIR[district][compartment]

    def get_SEIR(self, district):
        """Returns the SEIR value of the given district"""
        return [self.SEIR[district][compartment] for compartment in "SEIR"]

    def update_summary(self, district, max_state, state):
        """Updates summary variable"""
        if self.SEIR[state][district].sum() > self.max_summary.at[max_state, district]:
            self.max_summary.at[max_state, district] = self.SEIR[state][district].sum()
            self.max_summary.at["%s_time" % (max_state), district] = self.steps

    def compute_as_infection_probability(self, as_infection_expectation, incubation_rate):
        as_infection_probability = {}
        for key in incubation_rate:
            as_infection_expectation[key] = as_infection_expectation[key] * incubation_rate[key]
        return as_infection_expectation

    def compute_localized_immunity(
        self,
        district_poverty_score,
        natural_immunity,
        preexisting_conditions,
        exercise
    ):
        localized_immunity = {}
        immunity = natural_immunity * preexisting_conditions * exercise

        for key in district_poverty_score:
            localized_immunity[key] = district_poverty_score[key] * immunity

        return localized_immunity

    def add_one(self, district, age_group, compartment):
        """Adds one to the compartment"""
        self.SEIR[compartment].at[age_group, district] += 1

    def remove_one(self, district, age_group, compartment):
        self.SEIR[compartment].at[age_group, district] -= 1
