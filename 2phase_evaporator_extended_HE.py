from tespy.connections import connection
from tespy.networks import network
from tespy.components import evaporator, heat_exchanger, pump, turbine, source, sink, cycle_closer, splitter, merge, condenser
from CoolProp.CoolProp import PropsSI
import numpy as np
from tespy.tools import logger
import logging
mypath = logger.define_logging(
log_path=True, log_version=True, timed_rotating={'backupCount': 4},
screen_level=logging.WARNING, screen_datefmt = "no_date")

fluids = ['water', 'Isopentane', 'Air']

nw = network(fluids=fluids)
nw.set_attr(p_unit='bar', T_unit='C', h_unit='kJ / kg')
# components
mass_flow_rate_air = 6142
T_air = -4.7
p_air = 0.61

# main components
evaporator = evaporator('evaporator')
pump_c = pump('condensate pump')
merge = merge('geo-fluid merge point')
preheater = heat_exchanger('preheater')
turbine = turbine('turbine')
ihe = heat_exchanger('internal heat exchanger')
condenser = condenser('condenser')
pump = pump('feeding pump')
# working fluid
source_wf = source('working fluid source')
sink_wf = sink('working fluid sink')
close_cycle = cycle_closer('cycle closer before turbine')
#brine
source_s = source('steam source')
source_b = source('brine source')
sink_s = sink('steam sink')
sink_b = sink('brine sink')
# cooling air
source_ca = source('cooling air source')
sink_ca = sink('cooling air sink')

# connections
# main cycle
preheater_wf_in = connection(source_wf, 'out1', preheater, 'in2')
preheater_evaporator = connection(preheater, 'out2', evaporator, 'in3')
evaporator_turbine = connection(evaporator, 'out3', turbine, 'in1')
turbine_ihe = connection(turbine, 'out1', ihe, 'in1')
ihe_condenser = connection(ihe, 'out1', condenser, 'in1')
condenser_pump = connection(condenser, 'out1', pump, 'in1')
pump_ihe = connection(pump, 'out1', ihe, 'in2')
ihe_wf_out = connection(ihe, 'out2', sink_wf, 'in1')

evaporator_steam_in = connection(source_s, 'out1', evaporator, 'in1')
evaporator_pump = connection(evaporator, 'out1', pump_c, 'in1')
pump_sink_s = connection(pump_c, 'out1', merge, 'in1')

evaporator_brine_in = connection(source_b, 'out1', evaporator, 'in2')
evaporator_sink_b = connection(evaporator, 'out2', merge, 'in2')

merge_preheater = connection(merge, 'out1', preheater, 'in1')
preheater_sink = connection(preheater, 'out1', sink_b, 'in1')

nw.add_conns(preheater_wf_in, preheater_evaporator, evaporator_turbine, turbine_ihe, ihe_condenser, condenser_pump, pump_ihe, ihe_wf_out)
nw.add_conns(evaporator_steam_in, evaporator_pump, pump_sink_s, evaporator_brine_in, evaporator_sink_b, merge_preheater, preheater_sink)

# cooling air
ca_in = connection(source_ca, 'out1', condenser, 'in2')
ca_out = connection(condenser, 'out2', sink_ca, 'in1')
nw.add_conns(ca_in, ca_out)

# parametrization of components
evaporator.set_attr(pr1=0.93181818, pr2=0.970588, pr3=1)
preheater.set_attr(pr1=0.949494, pr2=0.955752)
pump_c.set_attr(pr=2.4480712, eta_s=0.8)
turbine.set_attr(pr=0.098148148, eta_s=0.85, design=['eta_s', 'pr'])
pump.set_attr(pr=14.75, eta_s=0.9)
ihe.set_attr(pr1=0.849056603, pr2=0.957627118)
condenser.set_attr(pr1=0.8889, pr2=1)

# parametrization of connections
preheater_wf_in.set_attr(T=39.7, p=11.3, fluid={'water': 0, 'Isopentane': 1, 'Air': 0})

evaporator_steam_in.set_attr(T=146.6, m=20.4, p=4.34, state='g', fluid={'water': 1, 'Isopentane': 0, 'Air':0})

evaporator_brine_in.set_attr(T=146.6, m=190.8, fluid={'water': 1, 'Isopentane': 0, 'Air':0})
evaporator_sink_b.set_attr(T=118.6)
preheater_sink.set_attr(T=69.1)

# air cooling connections
ca_in.set_attr(T=T_air, p=p_air, m=mass_flow_rate_air, fluid={'water': 0, 'Isopentane': 0, 'Air': 1})
ca_out.set_attr(T=T_air + 15)

# solving
mode = 'design'
file = 'yangyi_evaporator_new'
# solve the network, print the results to prompt and save
nw.solve(mode=mode)
nw.print_results()
#nw.save(file)
