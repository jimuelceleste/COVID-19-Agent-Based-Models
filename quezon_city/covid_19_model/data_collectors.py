# data_collectors.py

"""
Collection of functions that return configured data collector methods.
Each of the data collectors return one of the four types of data: S, E, I, or R.
"""

def get_susceptible_function(district):
    def get_susceptible(model):
        """Returns the number of susceptible in a district."""
        return int(model.SEIR["S"][district].sum())
    return get_susceptible

def get_exposed_function(district):
    def get_exposed(model):
        """Returns the number of exposed in a district"""
        return int(model.SEIR["E"][district].sum())
    return get_exposed

def get_infected_function(district):
    def get_infected(model):
        """Returns the number of infected in a district"""
        return int(model.SEIR["I"][district].sum())
    return get_infected

def get_removed_function(district):
    def get_removed(model):
        """Returns the number of removed in a district"""
        return int(model.SEIR["R"][district].sum())
    return get_removed

def get_max_infected_function(district):
    def get_max_infected(model):
        return int(model.max_summary.at["max_infected", district])
    return get_max_infected

def get_max_exposed_function(district):
    def get_max_exposed(model):
        return int(model.max_summary.at["max_exposed", district])
    return get_max_exposed
