import logging
from syspce_input import Input
from syspce_message import *
import threading

import volatility.conf as conf
import volatility.registry as registry
import volatility.utils as utils
import volatility.plugins.taskmods as taskmods
import volatility.commands as commands
import volatility.addrspace as addrspace

log = logging.getLogger('sysmoncorrelator')

class InputVolatility(Input):

	def __init__(self, data_buffer_in,
				 data_condition_in, src, 
				 filepath, profile):

		Input.__init__(self, data_buffer_in,
					   data_condition_in,
					   src)


		self.config = conf.ConfObject()
		self.config.PROFILE = profile
		self.config.LOCATION = filepath

		registry.PluginImporter()
		registry.register_global_options(self.config, commands.Command)
		registry.register_global_options(self.config, addrspace.BaseAddressSpace)

		self.name = 'Input Volatility'
		self.module_id = Module.INPUT_VOLATILITY



	def do_action(self):

		self.vprocess = []
		# Getting process information 
		p = taskmods.PSList(self.config)
		self.p1 = {}
		
		## PSLIST
		for process in p.calculate():
			## Mapping to event id sysmon 1
			self.p1['CommandLine'] = str(process.Peb.ProcessParameters.CommandLine)
			self.p1['CurrentDirectory'] = str(process.Peb.ProcessParameters.CurrentDirectory.DosPath)
			self.p1['Image'] = str(process.Peb.ProcessParameters.ImagePathName)
			self.p1['IdEvent'] = 1
			self.p1['UtcTime'] = str(process.CreateTime)
			self.p1['ProcessId'] = str(int(process.UniqueProcessId))
			self.p1['ParentProcessId'] = str(int(process.InheritedFromUniqueProcessId))
			self.p1['TerminalSessionId'] = str(int(process.SessionId))
			## Extra 
			self.p1['ExistTime'] = str(process.ExitTime)
			self.p1['BeingDebugged'] = str(process.Peb.BeingDebugged)
			self.p1['IsWow64'] = str(process.IsWow64)
			self.p1['NumHandles'] = str(int(process.ObjectTable.HandleCount))
			self.p1['NumThreads'] = str(int(process.ActiveThreads))
			self.p1['DllPath'] = str(int(process.ActiveThreads))

			self.vprocess.append(self.p1)
			self.p1 = {}

		for p in self.vprocess:
			for x in self.vprocess:
				if p['ParentProcessId'] == x['ProcessId']:
					p['ParentImage'] = x['Image']
					p['ParentCommandLine'] = x['CommandLine']
		
		
		events_list = self.vprocess
		
		self.send_message(events_list)
		
		self.terminate()