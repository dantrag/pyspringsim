import configparser
import collections

class CaseInsensitiveDict(collections.MutableMapping):
    """ Ordered case insensitive mutable mapping class. """
    def __init__(self, *args, **kwargs):
        self._d = collections.OrderedDict(*args, **kwargs)
        self._convert_keys()
    def _convert_keys(self):
        for k in list(self._d.keys()):
            v = self._d.pop(k)
            self._d.__setitem__(k, v)
    def __len__(self):
        return len(self._d)
    def __iter__(self):
        return iter(self._d)
    def __setitem__(self, k, v):
        self._d[k.lower()] = v
    def __getitem__(self, k):
        return self._d[k.lower()]
    def __delitem__(self, k):
        del self._d[k.lower()]

class SimulatorSettings:
    def __init__(self, filename = ""):
        self._particle_default_radius = 1.0
        self._molten_particle_default_radius = 2.0
        self._molten_particle_cooldown_time_ = 20

        self._spring_default_stiffness = 0.01
        self._spring_default_length = 5.5
        self._spring_connection_threshold = 1.0
        self._spring_disconnection_threshold = 1.3

        self._relaxation_iteration_limit = 2000
        self._relaxation_convergence_limit = 0.001

        self._heater_speed = 2.0
        self._heater_size = 20.0
 
        if filename != "":
            self.load_from_file(filename)

    @property
    def particle_default_radius(self):
        return self._particle_default_radius

    @particle_default_radius.setter
    def particle_default_radius(self, radius):
        self._particle_default_radius = radius

    @property
    def molten_particle_default_radius(self):
        return self._molten_particle_default_radius

    @molten_particle_default_radius.setter
    def molten_particle_default_radius(self, radius):
        self._molten_particle_default_radius = radius

    @property
    def molten_particle_cooldown_time(self):
        return self._molten_particle_cooldown_time

    @molten_particle_cooldown_time.setter
    def molten_particle_cooldown_time(self, time):
        self._molten_particle_cooldown_time = time

    @property
    def spring_default_stiffness(self):
        return self._spring_default_stiffness

    @spring_default_stiffness.setter
    def spring_default_stiffness(self, stiffness):
        self._spring_default_stiffness = stiffness

    @property
    def spring_default_length(self):
        return self._spring_default_length

    @spring_default_length.setter
    def spring_default_length(self, length):
        self._spring_default_length = length

    @property
    def spring_connection_threshold(self):
        return self._spring_connection_threshold

    @spring_connection_threshold.setter
    def spring_connection_threshold(self, threshold):
        self._spring_connection_threshold = threshold

    @property
    def spring_disconnection_threshold(self):
        return self._spring_disconnection_threshold

    @spring_disconnection_threshold.setter
    def spring_disconnection_threshold(self, threshold):
        self._spring_disconnection_threshold = threshold

    @property
    def relaxation_iteration_limit(self):
        return self._relaxation_iteration_limit

    @relaxation_iteration_limit.setter
    def relaxation_iteration_limit(self, iterations):
        self._relaxation_iteration_limit = iterations

    @property
    def relaxation_convergence_limit(self):
        return self._relaxation_convergence_limit

    @relaxation_convergence_limit.setter
    def relaxation_convergence_limit(self, convergence):
        self._relaxation_convergence_limit = convergence

    @property
    def heater_speed(self):
        return self._heater_speed

    @heater_speed.setter
    def heater_speed(self, speed):
        self._heater_speed = speed

    @property
    def heater_size(self):
        return self._heater_size

    @heater_size.setter
    def heater_size(self, size):
        self._heater_size = size
    
    def load_from_file(self, filename):
        config = configparser.ConfigParser(dict_type=CaseInsensitiveDict)
        try:
            config.read(filename)
            self.particle_default_radius = \
                float(config['particle']['defaultradius'])
            self.molten_particle_default_radius = \
                float(config['particle']['moltendefaultradius'])
            self.molten_particle_cooldown_time = \
                int(config['particle']['cooldowntime'])

            self.spring_default_stiffness = \
                float(config['spring']['defaultstiffness'])
            self.spring_default_length = \
                float(config['spring']['defaultlength'])
            self.spring_connection_threshold = \
                float(config['spring']['connectionthreshold'])
            self.spring_disconnection_threshold = \
                float(config['spring']['disconnectionthreshold'])

            self.relaxation_iteration_limit = \
                int(config['relaxation']['iterationlimit'])
            self.relaxation_convergence_limit = \
                float(config['relaxation']['convergencelimit'])

            self.heater_speed = \
                float(config['heater']['speed'])
            self.heater_size = \
                float(config['heater']['size'])
        except:
            print("Failed reading config file %s" % filename)

    def save_to_file(self, filename):
        config = configparser.ConfigParser()
        if True:
            config['particle'] = {}
            config['particle']['defaultradius'] = '%.2f' % self.particle_default_radius
            config['particle']['moltendefaultradius'] = '%.2f' % self.molten_particle_default_radius
            config['particle']['cooldowntime'] = str(self.molten_particle_cooldown_time)

            config['spring'] = {}
            config['spring']['defaultstiffness'] = '%.3f' % self.spring_default_stiffness
            config['spring']['defaultlength'] = '%.2f' % self.spring_default_length
            config['spring']['connectionthreshold'] = '%.2f' % self.spring_connection_threshold
            config['spring']['disconnectionthreshold'] = '%.2f' % self.spring_disconnection_threshold

            config['relaxation'] = {}
            config['relaxation']['iterationlimit'] = str(self.relaxation_iteration_limit)
            config['relaxation']['convergencelimit'] = '%.4f' % self.relaxation_convergence_limit

            config['heater'] = {}
            config['heater']['speed'] = '%.2f' % self.heater_speed
            config['heater']['size'] = '%.2f' % self.heater_size

            with open(filename, 'w') as config_file:
                config.write(config_file)
        else:
            print("Failed writing config file %s" % filename)
