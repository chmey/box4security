from flask import redirect, Blueprint, render_template, url_for, request
from flask.helpers import flash
from wtforms_alchemy import ModelForm
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField
from source.extensions import db, ma


class WizardMiddleware():
    """BOX4security Wizard Middleware."""
    # Ordered list of steps
    steps = ['wizard.index', 'wizard.networks', 'wizard.box4s', 'wizard.systems', 'wizard.smtp', 'wizard.verify']

    def __init__(self, app):
        self.app = app
        self.url = '/wizard/'

    def __call__(self, environ, start_response):
        """Function is the main function called at each request to the middleware.
        The wizard middleware only applies if isShowWizard() returns true and
        the requested path is not an /api/ path or the wizard path itself.
        If it applies: redirect to self.url ('/wizard').
        If it does not apply, do nothing and pass the request to next middleware.
        """
        reqPath = environ.get('PATH_INFO')
        if self.isShowWizard() and not reqPath.startswith('/api/') and not reqPath.startswith(self.url):
            # If true, redirect to the wizard base URL (self.url) with status code 307
            status = "307 Temporary Redirect"
            headers = [('Location', self.url), ('Content-Length', '0')]
            start_response(status, headers)
            return [b'']
        # if the Wizard shall not be shown, cleanly exit the middleware without doing anything and continue the application flow.
        return self.app(environ, start_response)

    def isShowWizard(self):
        """Evaluate whether the Wizard shall be displayed."""
        return True

    @staticmethod
    def getMaxStep():
        """Return the maximum advanced step as endpoint string.

        For example:
        Returns 'wizard.systems' if the user has recently completed the box4s step but not yet the systems step.
        """
        if System.query.filter(~System.types.any(name='BOX4security')).count():
            # Systems apart from BOX4s exist, next step is smtp
            return 'wizard.smtp'
        elif System.query.filter(System.types.any(name='BOX4security')).count():
            # BOX4security is defined, next step systems
            return 'wizard.systems'
        elif Network.query.count():
            # Network is defined, next step BOX4s
            return 'wizard.box4s'
        else:
            # Nothing yet defined, max step is networks
            return 'wizard.networks'

    @staticmethod
    def compareSteps(ep1, ep2):
        """Compare two step endpoints.
        Return 0 if ep1 and ep2 are the same step.
        Return -1 if ep1 is an earlier step than ep2.
        Return 1 if ep2 is an earlier step than ep1.
        """
        if ep1 == ep2:
            return 0
        elif WizardMiddleware.steps.index(ep1) < WizardMiddleware.steps.index(ep2):
            return -1
        else:
            return 1


wizard = Blueprint('wizard', __name__, template_folder='templates/wizard')


@wizard.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@wizard.route('/networks', methods=['GET', 'POST'])
def networks():
    if request.method == 'POST':
        return redirect(url_for('wizard.box4s'))
    else:
        formNetwork = NetworkForm(request.form)
        formNetwork.types.choices = [(t.id, t.name) for t in SystemType.query.order_by('id')]
        return render_template('networks.html', formNetwork=formNetwork)


@wizard.route('/box4s', methods=['GET', 'POST'])
def box4s():
    endpoint = WizardMiddleware.getMaxStep()
    if WizardMiddleware.compareSteps('wizard.box4s', endpoint) < 1:
        return render_template('box4s.html')
    else:
        flash('Bevor Sie fortfahren können, müssen Sie zunächst die vorherigen Schritte abschließen.', 'error')
        return redirect(url_for(endpoint))


@wizard.route('/systems', methods=['GET', 'POST'])
def systems():
    endpoint = WizardMiddleware.getMaxStep()
    if WizardMiddleware.compareSteps('wizard.systems', endpoint) < 1:
        return render_template('systems.html')
    else:
        flash('Bevor Sie fortfahren können, müssen Sie zunächst die vorherigen Schritte abschließen.', 'error')
        return redirect(url_for(endpoint))


@wizard.route('/mail', methods=['GET', 'POST'])
def smtp():
    endpoint = WizardMiddleware.getMaxStep()
    if WizardMiddleware.compareSteps('wizard.smtp', endpoint) < 1:
        return render_template('mail.html')
    else:
        flash('Bevor Sie fortfahren können, müssen Sie zunächst die vorherigen Schritte abschließen.', 'error')
        return redirect(url_for(endpoint))


@wizard.route('/verify', methods=['GET', 'POST'])
def verify():
    endpoint = WizardMiddleware.getMaxStep()
    if WizardMiddleware.compareSteps('wizard.verify', endpoint) < 1:
        return render_template('verify.html')
    else:
        flash('Bevor Sie fortfahren können, müssen Sie zunächst die vorherigen Schritte abschließen.', 'error')
        return redirect(url_for(endpoint))


class Network(db.Model):
    """Network model class.

    Explanation of non-trivial fields:
    scan_category: Scan Category as defined before:
        1: No restrictions
        2: Scans only at weekend or non-busy times
        3: Scans only when admins and 4s are available
    scan_weekday: lower cased weekday for scans
    scan_time: start time for the scan on `scan_weekday`
    types: List of associated NetworkTypes
    """
    __tablename__ = 'network'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))  # Network Name
    ip_address = db.Column(db.String(24), nullable=False)  # Network Address
    cidr = db.Column(db.Integer(), nullable=False)  # CIDR-Number
    vlan = db.Column(db.String(50))  # VLAN Tag
    types = db.relationship('NetworkType', secondary='network_networktype')
    scancategory_id = db.Column(db.Integer, db.ForeignKey('scancategory.id'))
    scan_weekday = db.Column(db.String(24))  # lower case
    scan_time = db.Column(db.Time())  # Start time for scan

    def __repr__(self):
        """Print Network in human readable form."""
        return '{} ({}): {}/{}'.format(self.name, self.id, self.ip_address, self.cidr)


class ScanCategory(db.Model):
    """Model class for Vulnerability Scan Categories."""
    __tablename__ = 'scancategory'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())
    networks = db.relationship('Network', backref='scan_category')

    def __repr__(self):
        """Print ScanCategory in human readable form."""
        return '{} ({})'.format(self.name, self.id)


class NetworkType(db.Model):
    """Model class for Network Types."""
    __tablename__ = 'networktype'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))  # Network Type Name

    def __repr__(self):
        """Print NetworkType in human readable form."""
        return '{} ({})'.format(self.name, self.id)


class NetworkNetworkType(db.Model):
    """Association table for Network Types and Networks."""
    __tablename__ = 'network_networktype'
    id = db.Column(db.Integer(), primary_key=True)
    network_id = db.Column(db.Integer(), db.ForeignKey('network.id', ondelete='CASCADE'))
    networktype_id = db.Column(db.Integer(), db.ForeignKey('networktype.id', ondelete='CASCADE'))


class System(db.Model):
    """System model class.

    Explanation of non-trivial fields:
    scan_enabled: True if vulnerability scans should be enabled for the system, else False
    ids_enabled: True if IDS should be enabled for the system, else False
    types: List of associated SystemTypes
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    ip_address = db.Column(db.String(24))  # System IP Address
    types = db.relationship('SystemType', secondary='system_systemtype')
    location = db.Column(db.String(255))  # System Location
    scan_enabled = db.Column(db.Boolean(), default=True)  # Scans active
    ids_enabled = db.Column(db.Boolean(), default=True)  # IDS enabled


class SystemType(db.Model):
    """Model class for System Types."""
    __tablename__ = 'systemtype'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))  # System Type Name

    def __repr__(self):
        """Print SystemType in human readable form."""
        return '{} ({})'.format(self.name, self.id)


class SystemSystemType(db.Model):
    """Association table for System Types and Systems."""
    __tablename__ = 'system_systemtype'
    id = db.Column(db.Integer(), primary_key=True)
    system_id = db.Column(db.Integer(), db.ForeignKey('system.id', ondelete='CASCADE'))
    systemtype_id = db.Column(db.Integer(), db.ForeignKey('systemtype.id', ondelete='CASCADE'))


class NetworkForm(ModelForm, FlaskForm):
    """Form for Network model."""
    class Meta:
        model = Network
    types = SelectMultipleField(
        'Netz-Typ',
        coerce=int
    )


class NetworkTypeForm(ModelForm, FlaskForm):
    """Form for NetworkType model."""
    class Meta:
        model = NetworkType


class SystemForm(ModelForm, FlaskForm):
    """Form for NetworkType model."""
    class Meta:
        model = System


class SystemTypeForm(ModelForm, FlaskForm):
    """Form for SystemType model."""
    class Meta:
        model = SystemType
