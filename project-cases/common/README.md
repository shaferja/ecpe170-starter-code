# Shared Project Measurement Helpers

`measurement.py` provides the percentile, environment, and CSV helpers used by the case drivers. Preserve its percentile definition and evidence fields when comparing baseline and intervention runs. If you modify the helper, explain why and rerun the relevant correctness test.

`plotting.py` supports each case’s `plot_results.py` command. Install Matplotlib in your personal case virtual environment. Keep `common` beside the case folder. CSV input is one baseline session; repeated workload keys are rejected so separate runs are not silently merged. Graphs retain timing scopes, failed-request counts, and the separation of VM measurements from teaching traces.
