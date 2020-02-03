### written by Sebastian Foerster - https://github.com/Counterfeiter/, https://sebastianfoerster86.wordpress.com/
import requests

class CloudDNNC():
    # URL base with "http://"
    # warmstartsamples sends process information but controller has some sampling time zero output
    def __init__(self, url_base, warmstartsamples = 0):
        self.url_base = url_base

        self.warmstartsamples = warmstartsamples
        self.scaler_process_value = (0.0, 100.0)
        self.scaler_control_value = (0.0, 100.0)
        self.sessionid = ''

        try:
            r = requests.get(self.url_base + "/newsessionid").json()
            self.sessionid = r["sessionid"]
        except requests.exceptions.ConnectionError as e:
            print("Connecting Error - check server URL or internet connection - ", e)
        except requests.exceptions.Timeout as e:
            print("Timeout Error - Server load to high? - ", e)

    def __call__(self, setpoint, process_value, control_value = None):
        # silent saturation of values
        payload = {"sessionid":self.sessionid,
                    'setpoint': self._norm(setpoint, self.scaler_process_value),
                    'processvalue': self._norm(process_value, self.scaler_process_value),
                    }

        if(control_value):
            payload['controlvalue'] = self._norm(control_value, self.scaler_control_value)

        if(self.warmstartsamples > 0):
            self.warmstartsamples -= 1
            payload['controlvalue'] = 0.0

        try:
            r = requests.get(self.url_base + "/control", params=payload).json()
        except requests.exceptions.ConnectionError as e:
            print ("Connecting Error - check server URL or internet connection - ",e)
            return None
        except requests.exceptions.Timeout as e:
            print ("Timeout Error - Server load to high? - ",e)
            return None

        if ("error" in r):
            raise ValueError(r["error"])

        #denorm incomming data
        r["controlvalue"] = self._denorm(r["controlvalue"], self.scaler_control_value)
        r["processvalue"] = self._denorm(r["processvalue"], self.scaler_process_value)
        r["setpoint"] = self._denorm(r["setpoint"], self.scaler_process_value)

        if(self.warmstartsamples > 0):
            r["controlvalue"] = 0.0

        return r

    def _norm(self, value, range_in):
        norm = (value - range_in[0]) / (range_in[1] - range_in[0]) * 100.0
        return float(min(max(norm, 0.0), 100.0)) #clip - with norm
    def _denorm(self, value, range_in):
        denorm = (value / 100.0 * (range_in[1] - range_in[0]) + range_in[0])
        return float(min(max(denorm, range_in[0]), range_in[1])) #clip - with given ranges

    def setProcessValueRange(self, min_value, max_value):
        if (min_value >= max_value):
            raise ValueError("Min greater then max value")
        self.scaler_process_value = (min_value, max_value)

    def setControlValueRange(self, min_value, max_value):
        if (min_value >= max_value):
            raise ValueError("Min greater then max value")
        self.scaler_control_value = (min_value, max_value)

    def __del__(self):
        payload = {"sessionid":self.sessionid}
        try:
            requests.get(self.url_base + "/deletesessionid", params=payload)
        except requests.exceptions.RequestException:
            pass