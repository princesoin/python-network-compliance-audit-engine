#import pytest
#from check_modules.firmware_check import extract_firmware_arista
#from check_modules.firmware_check import extract_firmware_nokia
from check_modules.firmware_check import check_firmware

# Fortinet Platform Tests. 

def test_correct_firmware_fortinet():
    output = """FGT-ARM64-KVM-2CONNF # get system status | grep '^Version:'
                 Version: FortiGate-ARM64-KVM v8.0.1,build0245,260909 (GA.F)
            """
    
    device_vars = {
         "firmware_version" : ["v8.0.1,build0245,260909 "]
         }
    
    result = check_firmware(output, device_vars, "fortinet")

    assert result == []

def test_incorrect_firmware_fortinet():
    output = """FGT-ARM64-KVM-2CONNF # get system status | grep '^Version:'
                 Version: FortiGate-ARM64-KVM v8.0.1,build0245,2109 (GA.F)
            """
    
    device_vars = {
         "firmware_version" : ["v8.0.1,build0245,260909"]
         }
    
    result = check_firmware(output, device_vars, "fortinet")

    assert result == ['Missing firmware version v8.0.1,build0245,260909', 'Unexpected firmware version v8.0.1,build0245,2109']

# Arista Platform Tests. 

def test_correct_firmware_arista():
    output = """Arista cEOSLab
                Hardware version: 
                Serial number: SERIAL-REDACTED
                Hardware MAC address: 0000.0000.0000
                System MAC address: 0000.0000.0000
                Software image version: 4.35.2F-46221466.4352F (engineering build)
                Architecture: aarch64
                Internal build version: 4.35.2F-46221466.4352F
                Internal build ID: d12f384e-8f85-430b-b87c-032a589fcd98
                Image format version: 1.0
                Image optimization: None
            """
    device_vars = {
        "firmware_version": ["4.35.2F-46221466.4352F"]
        }
    result = check_firmware(output, device_vars, "arista_eos")
    
    assert result == []

def test_incorrect_firmware_arista():
    output = """Arista cEOSLab
                Hardware version: 
                Serial number: SERIAL-REDACTED
                Hardware MAC address: 0000.0000.0000
                System MAC address: 0000.0000.0000
                Software image version: 2.35.2-4266.4352F (engineering build)
                Architecture: aarch64
                Internal build version: 4.35.2F-46221466.4352F
                Internal build ID: d12f384e-8f85-430b-b87c-032a589fcd98
                Image format version: 1.0
                Image optimization: None
            """
    device_vars = {
        "firmware_version": ["4.35.2F-46221466.4352F"]
        }
    result = check_firmware(output, device_vars, "arista_eos")
    
    assert result == ['Missing firmware version 4.35.2F-46221466.4352F', 'Unexpected firmware version 2.35.2-4266.4352F']

# Nokia Platform Tests. 

def test_correct_firmware_nokia():
    output = """-----------------------------------------------------------------------------------
            Hostname             : srl1
            Chassis Type         : 7220 IXR-D2L
            Part Number          : Sim Part No.
            Serial Number        : SERIAL-REDACTED
            System HW MAC Address: 0000.0000.0000
            OS                   : SR Linux
            Software Version     : v26.7.2
            Build Number         : 519-g94fbd638fa8
            Architecture         : aarch64
            Last Booted          : 2026-10-18T10:26:31.503Z
            Total Memory         : 8195904 kB
            Free Memory          : 422264 kB
            -----------------------------------------------------------------------------------
            """
    device_vars = {
        "firmware_version": ["v26.7.2"]
        }
    result = check_firmware(output, device_vars, "nokia_srl")
    
    assert result == []

def test_incorrect_firmware_nokia():
    output = """-----------------------------------------------------------------------------------
            Hostname             : srl1
            Chassis Type         : 7220 IXR-D2L
            Part Number          : Sim Part No.
            Serial Number        : SERIAL-REDACTED
            System HW MAC Address: 0000.0000.0000
            OS                   : SR Linux
            Software Version     : v21.7.2
            Build Number         : 519-g94fbd638fa8
            Architecture         : aarch64
            Last Booted          : 2026-10-18T10:26:31.503Z
            Total Memory         : 8195904 kB
            Free Memory          : 422264 kB
            -----------------------------------------------------------------------------------
            """
    device_vars = {
        "firmware_version": ["v26.7.2"]
        }
    result = check_firmware(output, device_vars, "nokia_srl")
    
    assert result == ['Missing firmware version v26.7.2', 'Unexpected firmware version v21.7.2']
