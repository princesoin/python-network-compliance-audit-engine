from check_modules.hardening_check import check_hardening

# Fortinet Platform Tests. 

def test_correct_hardening_fortinet():
    output = """SSH v2 is enabled on port 22
                SSH is enabled on the following 1 interfaces:
                        port1
                SSH hostkey RSA fingerprint = 

                FGT-ARM64-KVM-NM3Z4Y # get system status | grep -i fips
                FIPS-CC mode: enable
             """
    
    device_vars = {
        "hardening_configuration": {
            "sshd_status": "enabled",
            "fips_status": "enable",
        }
    }

    hardening_vars = device_vars.get('hardening_configuration', {})

    result = check_hardening(output, device_vars, "fortinet")

    assert result == []

def test_incorrect_hardening_fortinet():
    output = """SSH v2 is enabled on port 22
                SSH is enabled on the following 1 interfaces:
                        port1
                SSH hostkey RSA fingerprint = 

                FGT-ARM64-KVM-NM3Z4Y # get system status | grep -i fips
                FIPS-CC mode: disable
             """
    
    device_vars = {
        "hardening_configuration": {
            "sshd_status": "enabled",
            "fips_status": "enable",
        }
    }

    hardening_vars = device_vars.get('hardening_configuration', {})

    result = check_hardening(output, device_vars, "fortinet")

    assert result == ['Missing or Incorrect Hardening Setting: FIPS Status (Expected: enable)', 'Unexpected Setting Found active on device: FIPS Status=disable']

# Arista Platform Tests. 

def test_correct_hardening_arista():
    output = """User certificate authentication methods: none (neither trusted CA nor SSL profile configured)
                SSHD status for Default VRF: enabled
                SSH connection limit: 50
                SSH per host connection limit: 20
                FIPS status: enabled
             """
    
    device_vars = {
        "hardening_configuration": {
            "sshd_status": "enabled",
            "fips_status": "enabled",
        }
    }

    hardening_vars = device_vars.get('hardening_configuration', {})

    result = check_hardening(output, device_vars, "arista_eos")

    assert result == []

def test_incorrect_hardening_arista():
    output = """User certificate authentication methods: none (neither trusted CA nor SSL profile configured)
                SSHD status for Default VRF: enabled
                SSH connection limit: 50
                SSH per host connection limit: 20
                FIPS status: disabled
            """
    
    device_vars = {
        "hardening_configuration": {
            "sshd_status": "enabled",
            "fips_status": "enabled",
        }
    }

    hardening_vars = device_vars.get('hardening_configuration', {})

    result = check_hardening(output, device_vars, "arista_eos")

    assert result == ['Missing or Incorrect Hardening Setting: FIPS Status (Expected: enabled)', 'Unexpected Setting Found active on device: FIPS Status=disabled']

# Nokia Platform Tests. 

def test_correct_hardening_nokia():
    output = """ndk-admin-state
            admin-state enable
            oper-state up
        admin-state enable
        oper-state up
            admin-state disable
        admin-state enable
        oper-state up
            admin-state disable
        admin-state enable
        oper-state down
            admin-state disable
        admin-state enable
        oper-state up
            admin-state enable
        admin-state enable
        oper-state up
            admin-state enable
        admin-state enable
        admin-state enable
                admin-state enable
                oper-state up
                admin-state enable
                oper-state up
            admin-state disable
            oper-state down
        fips-140 {
            admin-state enable
            oper-state down
            oper-state inactive
        oper-state up
        admin-state enable
        oper-state up
            admin-state enable
            admin-state enable
            oper-state up
    ssh-server mgmt {
        admin-state enable
        oper-state up
    ssh-server mgmt-netconf {
        admin-state enable
        oper-state up
        admin-state enable
        admin-state enable
        oper-state up
        ssh-server mgmt-netconf
        admin-state enable
            admin-state enable
            oper-state up
            admin-state enable
            oper-state up
            admin-state enable
            oper-state up
            """
    
    device_vars = {
        "hardening_configuration": {
            "sshd_status": "enable",
            "fips_status": "enable",
        }
    }

    hardening_vars = device_vars.get('hardening_configuration', {})

    result = check_hardening(output, device_vars, "nokia_srl")

    assert result == []