# set_labels_gcp_fsoar

This repository contains the code needed to implement a Connector in FortiSOAR, which writes a label to a compute instance in GCP.  This is designed for use in an incident response playbook.  User input variables required are zone, instance name, label key and label value.  The idea is that policy framework in FortiGate is already configured such that labels matching the key:value pair will be blocked.  The previous play in the book may integrate with a SIEM, GCP SCC, or a 3rd party CSPM (like WIZ).  When an event is created, identifying a compromised instance, the zone and instance name variables can be passed to this connector.  In practice, it is probably more useful to modify the label key:value to a fixed value.  This can be done by modifying operations.py and changing as below:

current:
labels = {params.get('new_key'): params.get('new_value')}

new:
labels = {'fixed_key': 'fixed_value'}

You will also need to delete lines 50 through 67 from info.json