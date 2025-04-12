# coding: utf-8

# =========================================================================
# echo_example.py
#
# Copyright (c) the Contributors as noted in the AUTHORS file.
# This file is part of Ingescape, see https://github.com/zeromq/ingescape.
# 
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# =========================================================================


import ingescape as igs
import sys


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Echo(metaclass=Singleton):
    def __init__(self):
        # inputs
        # outputs
        self.status_o = "Started"
        self.briefing_package_o = None

    @property
    def status_o(self):
        return self.status_o

    @status_o.setter
    def status_o(self, value):
        self._status_o = value
        if self._status_o is not None:
            igs.output_set_string("status", self._status_o)

    @property
    def briefing_package_o(self):
        return self.briefing_package_o
    
    @briefing_package_o.setter
    def briefing_package_o(self, value):
        self._briefing_package_o = value
        if self._briefing_package_o is not None:
            igs.output_set_data("briefingPackage", self._briefing_package_o)
    # services
    def receive_values(self, sender_agent_name, sender_agent_uuid, boolV, integer, double, string, data, token, my_data):
        igs.info(f"Service receive_values called by {sender_agent_name} ({sender_agent_uuid}) with argument_list {boolV, integer, double, string, data} and token '{token}''")

    def send_values(self, sender_agent_name, sender_agent_uuid, token, my_data):
        print(f"Service send_values called by {sender_agent_name} ({sender_agent_uuid}), token '{token}' sending values : {self.on_off_o, self.integerO, self.doubleO, self.stringO, self.dataO}")
        igs.info(sender_agent_uuid, "receive_values", (self.on_off_o, self.integerO, self.doubleO, self.stringO, self.dataO), token)