# -*- coding: iso-8859-1 -*-
import time
import numpy as np

from mint.opt_objects import Target
import stats.stats as stats


class SLACTarget(Target):
    def __init__(self, mi=None, eid='GDET:FEE1:241:ENRCHSTBR'):
        """
        :param mi: Machine interface
        :param eid: ID
        """
        super(SLACTarget, self).__init__(eid=eid)

        self.mi = mi
        self.kill = False
        self.objective_acquisition = None
        self.objective_mean = None
        self.objective_stdev = None

        self.objective_acquisitions = []  # all the points
        self.objective_means = []
        self.std_dev = []
        self.charge = []
        self.current = []
        self.losses = []
        self.points = None

    def get_penalty(self):
        sase, std, charge, current, losses = self.get_value() 
        alarm = self.get_alarm()
        pen = 0.0
        if alarm > 1.0:
            return self.pen_max
        if alarm > 0.7:
            return alarm * 50.0
        pen += alarm
        pen -= sase
        self.penalties.append(pen)
        self.times.append(time.time())
        self.values.append(sase)  # statistic
        self.objective_acquisitions.append(self.objective_acquisition)  # array of points
        self.objective_means.append(self.objective_mean)
        self.std_dev.append(std)
        self.alarms.append(alarm)
        self.charge.append(charge)
        self.current.append(current)
        self.losses.append(losses)
        self.niter += 1
        return pen

    #def get_alarm(self):
        
        #"""
        ##Initialize PVs and setting used in the errorCheck method.
        #"""
        ##setup pvs to check
        #self.error_bcs      = "BCS:MCC0:1:BEAMPMSV"
        #self.error_mps      = "SIOC:SYS0:ML00:CALCOUT989"
        #self.error_guardian = "SIOC:SYS0:ML00:AO466"
        #self.error_und_tmit = "BPMS:UND1:3290:TMITTH"
        #self.error_dmp_tmit_hstbr = "BPMS:DMP1:693:TMITHSTBR"

        ##pv to bypass the error pause
        #self.error_bypass  = "SIOC:SYS0:ML00:CALCOUT990"
        #self.error_tripped = "SIOC:SYS0:ML00:CALCOUT991"

        ##set the unlatch pv to zero
        #epics.caput(self.error_bypass, 0)
        #epics.caput(self.error_tripped,0)
        
        
        #"""
        ##Method that check the state of BCS, MPS, Gaurdian, UND-TMIT and pauses GP if there is a problem.
        #"""
        #while 1:
            ##check for bad state
            #if epics.caget(self.error_bypass, use_monitor=True)     == 1:
                #out_msg="Bypass flag is TRUE"
            #elif epics.caget(self.error_bcs, use_monitor=True)      != 1:
                #out_msg="BCS tripped"
            #elif epics.caget(self.error_mps, use_monitor=True)      != 0:
                #out_msg="MPS tripped"
            #elif epics.caget(self.error_guardian, use_monitor=True) != 0:
                #out_msg="Gaurdian tripped"
            #elif epics.caget(self.error_und_tmit, use_monitor=True) < 5.0e7:
                #out_msg="UND Tmit Low"
            #else:
                #out_msg='Everything Okay'

            ##exit if the stop button is set
            ##if not self.mi.getter.caget("SIOC:SYS0:ML03:AO702"):
            #if not epics.caget("SIOC:SYS0:ML03:AO702", use_monitor=True):
                #break

            ##set the error check message
            #epics.caput ("SIOC:SYS0:ML00:CA000",out_msg)
            #print out_msg

            ##break out if error check is bypassed
            #if (out_msg=="Bypass flag is TRUE"):
                #break

            ##break out if everything is okay
            #if (out_msg=="Everything Okay"):
                #epics.caput(self.error_tripped,0)
                #break
                ##return
            #else:
                #epics.caput(self.error_tripped,1)
            #time.sleep(0.1)

    def get_value(self):
        """
        Returns data for the ojective function (sase) from the selected detector PV.

        At lcls the repetition is  120Hz and the readout buf size is 2800.
        The last 120 entries correspond to pulse energies over past 1 second.

        Returns:
                Float of SASE or other detecor measurement
        """
        #datain = []
        #for i in range(self.nreadings):
        #    datain.extend(self.mi.get_value(self.eid))
        #    time.sleep(self.interval)
        if self.points is None:
            self.points = 120
        print("Get Value of : ", self.points, " points.")

        try:
            rate = self.mi.get_beamrate()
            nap_time = self.points/(rate*1.0)
        except Exception as ex:
            nap_time = 1
            print("Something went wrong with the beam rate calculation. Let's sleep 1 second.")
            print("Exception was: ", ex)

        time.sleep(nap_time)

        datain = self.mi.get_value(self.eid)

        if self.stats is None:
            self.stats = stats.StatNone

        try:
            data = datain[-int(self.points):]
            self.objective_acquisition = data
            self.objective_mean = np.mean(self.objective_acquisition)
            self.objective_stdev = np.std(self.objective_acquisition)
            self.statistic = self.stats.compute(data)
        except:  # if average fails use the scalar input
            print("Detector is not a waveform PV, using scalar value")
            self.objective_acquisition = datain
            self.objective_mean = datain
            self.objective_stdev = -1
            self.statistic = datain

        print(self.stats.display_name, ' of ', self.objective_acquisition.size, ' points is ', self.statistic,
              ' and standard deviation is ', self.objective_stdev)

        charge, current = self.mi.get_charge_current()
        losses = self.mi.get_losses()
        return self.statistic, self.objective_stdev, charge, current, losses

    def clean(self):
        Target.clean(self)
        self.objective_acquisitions = []  # all the points
        self.objective_means = []
        self.std_dev = []
        self.charge = []
        self.current = []
        self.losses = []
