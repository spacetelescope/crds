import yaml

from .submit import ReferenceSubmissionScript


class RedCatSubmissionScript(ReferenceSubmissionScript):
    """This script extends the original CRDS command line submission
    system with extra meta-data previously captured by the submit_to_redcat
    script.
    """

    def get_submission_parameters(self):
        """Returns the combined form parameter dictionary as a CRDS Struct defining
        the mapping from all form variables to their string values.
        """
        self._extra_redcat_parameters = self.get_extra_parameters()
        parameters = super(RedCatSubmissionScript, self).get_submission_parameters()
        parameters.update(self._extra_redcat_parameters)
        return parameters

    def add_args(self):
        self.add_arg("--redcat-parameters", type="str",
                     help="Path to YAML file defining extra ReDCaT parameters.")

    def get_extra_parameters(self):
        """Return the form dictionary mapping form variables to value strings for
        new variables being added by the streamlining project.
        """
        with open(self.args.redcat_parameters) as f:
            return yaml.load(f)
