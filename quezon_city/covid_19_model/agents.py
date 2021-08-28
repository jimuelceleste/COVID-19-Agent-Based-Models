# agents.py

from covid_19_model.enum.immunity import Immunity
from covid_19_model.enum.state import State
from covid_19_model.utils import coin_toss
from mesa_geo.geoagent import GeoAgent
from shapely.geometry import Point
import random

class PersonAgent(GeoAgent):
    """
    PersonAgent represents a person.

    Properties:
        unique_id: Agent's unique identification string
        model: Model which the agent belongs to
        shape: Agent's shapely.geometry shape
        district: Agent's home district
        state: Agents current state: S, E, I, or R
        age: Agent's age
        wearing_mask: True if agent is wearing a mask; else, False
        physical_distancing: True if agent is observing physical distance; else, False
        mobile_worker: True if agent is a mobile worker; else, False
    """

    def __init__(
        self,
        unique_id,
        model,
        shape,
        district,
        state,
        age,
        age_group,
        wearing_mask,
        physical_distancing,
        mobile_worker,
    ):
        """Initializes PersonAgent"""
        super().__init__(unique_id, model, shape)
        self.district = district
        self.state = state
        self.age = age
        self.age_group = age_group
        self.wearing_mask = wearing_mask
        self.physical_distancing = physical_distancing
        self.mobile_worker = mobile_worker
        self.days_infected = 0
        self.days_incubating = 0

    def step(self):
        """Advances agent by a step"""
        self.status()
        self.interact()
        self.move()

    def status(self):
        """Checks agent's status"""
        if self.state == State.EXPOSED:
            if coin_toss(self.model.incubation_rate.at[self.age_group, self.district]):
                self.transition(
                    district = self.district,
                    age_group = self.age_group,
                    prev_state = self.state,
                    next_state = State.INFECTED,
                    update_summary = True,
                    summary_key = "max_infected")
                self.model.total_summary.at["total_infected", self.district] += 1

        elif self.is_infected():
            self.days_infected += 1

            if self.days_infected < self.get_recovery_time():
                if coin_toss(self.model.mortality_rate.at[self.age_group, self.district]):
                    self.transition(
                        district = self.district,
                        age_group = self.age_group,
                        prev_state = self.state,
                        next_state = State.REMOVED)

                    self.model.total_summary.at["total_dead", self.district] += 1
                    self.model.dead.at[self.age_group, self.district] += 1

                    self.model.grid.remove_agent(self)
                    self.model.schedule.remove(self)
                    del self

            else:
                if coin_toss(self.model.recovery_rate.at[self.age_group, self.district]):
                    self.transition(
                        district = self.district,
                        age_group = self.age_group,
                        prev_state = self.state,
                        next_state = State.REMOVED)

                    self.model.total_summary.at["total_recovered", self.district] += 1
                    self.model.recovered.at[self.age_group, self.district] += 1

                    self.model.grid.remove_agent(self)
                    self.model.schedule.remove(self)
                    del self


    def get_recovery_time(self):
        return int(self.random.normalvariate(self.model.recovery_period,3))

    def interact(self):
        """Agent interacts with other agents"""
        if self.is_infected():
            neighbors = self.get_neighbors()
            for neighbor in neighbors:
                if (
                    isinstance(neighbor, PersonAgent)
                    and neighbor.is_susceptible()
                    and not neighbor.protected_by_wearing_mask_and_distancing()
                ):
                    if (
                        coin_toss(neighbor.model.transmission_rate.at[neighbor.age_group, neighbor.district])
                        or neighbor.has_low_immunity()
                    ):
                        neighbor.transition(
                            district = neighbor.district,
                            age_group = neighbor.age_group,
                            prev_state = neighbor.state,
                            next_state = State.EXPOSED,
                            update_summary = True,
                            summary_key = "max_exposed")
                        neighbor.model.total_summary.at["total_exposed", neighbor.district] += 1

    def move(self):
        """Agent moves in a random position"""
        if self.state != "R" and self.allowed_to_move():
            new_x = self.shape.x + self.random.randint(
                -self.mobility_range(),
                self.mobility_range())
            new_y = self.shape.y + self.random.randint(
                -self.mobility_range(),
                self.mobility_range())
            self.shape = Point(new_x, new_y)

    def allowed_to_move(self):
        """Checks if agent is allowed to go outside of residence"""
        return self.model.min_age_restriction <= self.age <= self.model.max_age_restriction

    def get_neighbors(self):
        """Returns agents nearby (distance = self.model.agent_exposure_distance)"""
        return self.model.grid.get_neighbors_within_distance(
            self,
            self.model.agent_exposure_distance)

    def mobility_range(self):
        if self.mobile_worker:
            return self.model.agent_mobility_range * 2
        return self.model.agent_mobility_range

    def protected_by_wearing_mask_and_distancing(self):
        probability_of_protection = (self.model.wearing_mask_percentage
        * self.model.wearing_mask_protection
        * self.model.physical_distancing_percentage
        * self.model.physical_distancing_protection)
        return coin_toss(probability_of_protection)

    def protected_by_physical_distancing(self):
        """Checks if agent is protected by social distancing"""
        if self.physical_distancing:
            return coin_toss(self.model.physical_distancing_protection)
        return False

    def protected_by_wearing_mask(self):
        probability_of_protection = self.model.wearing_mask_percentage * self.model.wearing_mask_protection
        return coin_toss(probability_of_protection)

    def set_state(self, state):
        """Set agent's state"""
        self.state = state

    def transition(self, district, age_group, prev_state, next_state, update_summary=False, summary_key=""):
        """Change's agent's state"""
        self.set_state(next_state)
        self.model.add_one(district, age_group, next_state)
        self.model.remove_one(district, age_group, prev_state)

        if update_summary:
            self.model.update_summary(district, summary_key, next_state)

    def has_low_immunity(self):
        return coin_toss(self.model.with_low_immunity_percentage)

    def is_senior_citizen(self):
        return self.age >= 60

    def is_susceptible(self):
        return self.state == State.SUSCEPTIBLE

    def is_infected(self):
        return self.state == State.INFECTED
