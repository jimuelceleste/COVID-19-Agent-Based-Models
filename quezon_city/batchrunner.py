from covid_19_model.model import Covid19Model
from covid_19_model.utils import parse_json
import pickle
from progress.spinner import Spinner
from progress.bar import Bar

def stopping_state(model):
    return model.get_SEIR("total")[1] <= 0 and model.get_SEIR("total")[2] <= 0

def batchrun(model, model_params, runs, max_iterations, stopping_state, experiment_id):
    for run in range(runs):
        print("Run %i of %i" % ((run + 1), runs))

        # Instantiates model
        model_instance = model(
            model_params["variable_params"],
            model_params["fixed_params"])

        # progress = Spinner("Running model ")
        progress = Bar("Running model", max = max_iterations)
        # while not stopping_state(model_instance):
        for i in range(max_iterations):
            model_instance.step()
            progress.next()
        progress.finish()

        # Save data
        output_data = {
            "district1": model_instance.data_collector_1.get_model_vars_dataframe(),
            "district2": model_instance.data_collector_2.get_model_vars_dataframe(),
            "district3": model_instance.data_collector_3.get_model_vars_dataframe(),
            "district4": model_instance.data_collector_4.get_model_vars_dataframe(),
            "district5": model_instance.data_collector_5.get_model_vars_dataframe(),
            "district6": model_instance.data_collector_6.get_model_vars_dataframe(),
            "steps": model_instance.steps,
            "max_summary": model_instance.max_summary,
            "total_summary": model_instance.total_summary,
            "dead": model_instance.dead,
            "recovered": model_instance.recovered,
        }
        output_filename = "output/exp_%i_SEIR_run_%i.pkl" % (experiment_id, run)
        with open(output_filename, "wb") as output_file:
            pickle.dump(output_data, output_file, -1) # -1 specifies highest binary protocol
            print("File saved: %s" % (output_filename))

        del output_data
        del model_instance

    print("Batch run finished.")

runs = 10
max_iterations = 150
# max_iterations = 250

fixed_params_file = "fixed_parameters_3.json"

model_params_0 = {
    "fixed_params": parse_json(fixed_params_file),
    "variable_params": parse_json("variable_parameters_0.json"),
}
model_params_1 = {
    "fixed_params": parse_json(fixed_params_file),
    "variable_params": parse_json("variable_parameters_1.json"),
}
model_params_2 = {
    "fixed_params": parse_json(fixed_params_file),
    "variable_params": parse_json("variable_parameters_2.json"),
}
model_params_3 = {
    "fixed_params": parse_json(fixed_params_file),
    "variable_params": parse_json("variable_parameters_3.json"),
}
model_params_4 = {
    "fixed_params": parse_json(fixed_params_file),
    "variable_params": parse_json("variable_parameters_4.json")
}
model_params_5 = {
    "fixed_params": parse_json(fixed_params_file),
    "variable_params": parse_json("variable_parameters_5.json")
}


# batchrun(
#     Covid19Model,
#     model_params_0,
#     runs,
#     max_iterations,
#     stopping_state,
#     experiment_id = 0)
# batchrun(
#     Covid19Model,
#     model_params_1,
#     runs,
#     max_iterations,
#     stopping_state,
#     experiment_id = 1)
# batchrun(
#     Covid19Model,
#     model_params_2,
#     runs,
#     max_iterations,
#     stopping_state,
#     experiment_id = 2)
batchrun(
    Covid19Model,
    model_params_3,
    runs,
    max_iterations,
    stopping_state,
    experiment_id = 3)
# batchrun(
#     Covid19Model,
#     model_params_4,
#     runs,
#     max_iterations,
#     stopping_state,
#     experiment_id = 4)
# batchrun(
#     Covid19Model,
#     model_params_5,
#     runs,
#     max_iterations,
#     stopping_state,
#     experiment_id = 5)