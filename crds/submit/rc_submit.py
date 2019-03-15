import yaml

from .submit import ReferenceSubmissionScript

class RedCatApiScript(ReferenceSubmissionScript):
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

    def get_extra_parameters(self):
        """Return the form dictionary mapping form variables to value strings for
        new variables being added by the streamlining project.
        """
        # ... get and populate required form dictionary,  careful about
        # conflicts with baseclass.   See baseclass self.connection for
        # doing any web i/o.
        
    def batch_submit_references(self):
        """Do a web re-post to the batch submit references web page."""
        return self._submission("/submission_form/redcat_submit/")

class RedCatSubmissionScript(RedCatApiScript):
    """This script extends the original CRDS command line submission
    system with extra meta-data previously captured by the submit_to_redcat
    script.
    """
    def add_args(self):
        super(ReferenceSubmissionScript, self).add_args()
        self.add_arg("--redcat-parameters", type="str",
                     help="Path to YAML file defining extra ReDCaT parameters.")
        
    def get_extra_parameters(self):
        """Return the form dictionary mapping form variables to value strings for
        new variables being added by the streamlining project.
        """
        with open(self.args.redcat_parameters) as f:
            return yaml.load(f)
        
def submit():
        # Deliver the files
    script = RedcatApiScript("crds.submit --files {} "
                             "--monitor-processing "
                             "--wait-for-completion "
                             "--wipe-existing-files "
                             "--log-time "
                             "--stats --creator '{} Team' "
                             "--description '{}'").format(
            submit_files, instrument, description)
    # script._extra_redcat_parameters = {}
    script()

    # What should return value be?
