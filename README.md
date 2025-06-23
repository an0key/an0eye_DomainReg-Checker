# an0eye_DomainReg-Checker

A domain registration monitoring script initially for an0 Technology's an0Eye service. This script provides CheckMK-compatible monitoring of domain expiration dates with performance data output.

## Overview

This tool monitors domain registration status and expiration dates, providing alerts when domains are approaching expiration. It's specifically designed to integrate with CheckMK/Nagios based systems.

## Features

- **Domain Expiration Monitoring**: Checks domain expiration dates using WHOIS queries
- **Registrar Information**: Retrieves and displays domain registrar details
- **CheckMK Integration**: Outputs performance data in CheckMK-compatible format
- **Caching**: Implements intelligent caching to reduce WHOIS query frequency
- **Configurable Thresholds**: Customizable warning periods before expiration
- **State Persistence**: Maintains state files for reliable monitoring

## Usage

```bash
python3 an0eye_DomainReg-Checker.py --domain example.com --warning-days 30 --check-interval 3600
```

### MRPE Configuration

To integrate with CheckMK using MRPE, add the following to your `mrpe.cfg` file:

```
Domain_example.com /usr/local/bin/python3 /opt/scripts/an0eye_DomainReg-Checker.py --domain example.com --warning-days 30 --check-interval 3600
```

For multiple domains, add separate entries:

```
Domain_example.com /usr/local/bin/python3 /opt/scripts/an0eye_DomainReg-Checker.py --domain example.com --warning-days 30 --check-interval 3600
Domain_mysite.org /usr/local/bin/python3 /opt/scripts/an0eye_DomainReg-Checker.py --domain mysite.org --warning-days 14 --check-interval 3600
```

### Parameters

- `--domain`: Domain name to monitor (required)
- `--warning-days`: Days before expiration to trigger warning (default: 14)
- `--check-interval`: Seconds between checks for caching (default: 3600)

### Output Format

The script outputs CheckMK-compatible status messages with performance data:

```
OK - Domain is registered and expires in 45 days. Registrar: Example Registrar|days_to_expiration=45.10;30;0;;
```

## Requirements

- Python 3.6+
- `whois` Python package
- Write access to `/var/lib/check_mk_agent/DNSReg/` for state files

## Installation

1. Install required Python packages:
   ```bash
   pip3 install python-whois
   ```

2. Ensure the script has write permissions to the state directory:
   ```bash
   sudo mkdir -p /var/lib/check_mk_agent/DNSReg/
   sudo chown check_mk_agent:check_mk_agent /var/lib/check_mk_agent/DNSReg/
   ```
