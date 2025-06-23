import argparse
import json
import os
import time
from datetime import datetime, timedelta, timezone
import whois
import math  # Add import for math module

# Version information
__version__ = "1.0.0"
__author__ = "an0 Technology"
__description__ = "CheckMK Domain Registration Checker for an0Eye service"

def parse_arguments():
    parser = argparse.ArgumentParser(
        description=f"{__description__} v{__version__}",
        epilog=f"Version {__version__} - {__author__}"
    )
    parser.add_argument("--domain", required=True, help="Domain to check")
    parser.add_argument("--warning-days", type=int, default=14, help="Days before expiration to trigger a warning")
    parser.add_argument("--check-interval", type=int, default=3600, help="Interval in seconds between checks")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser.parse_args()

def load_state(state_file):
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            return json.load(f)
    return {}

def save_state(state_file, state):
    with open(state_file, "w") as f:
        json.dump(state, f)

def check_domain(domain):
    try:
        domain_info = whois.whois(domain)
        expiration_date = domain_info.expiration_date
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
        if expiration_date and expiration_date.tzinfo is not None:
            expiration_date = expiration_date.astimezone(timezone.utc).replace(tzinfo=None)
        
        # Extract registrar information
        registrar = domain_info.registrar if hasattr(domain_info, 'registrar') and domain_info.registrar else "Unknown"
        
        return expiration_date, registrar
    except Exception as e:
        error_msg = str(e).lower()
        # Check if the error indicates an unregistered domain
        if any(phrase in error_msg for phrase in ["no match", "not found", "no data found", "status: available"]):
            return "UNREGISTERED", "N/A"
        print(f"Error checking domain: {e}")
        return None, None

def get_state_file_path(domain):
    base_dir = "/var/lib/check_mk_agent/DNSReg"
    os.makedirs(base_dir, exist_ok=True)
    sanitized_domain = domain.replace(".", "_")
    return os.path.join(base_dir, f"{sanitized_domain}_state.json")

def main():
    args = parse_arguments()

    state_file = get_state_file_path(args.domain)
    state = load_state(state_file)

    last_check = state.get("last_check")
    if last_check and time.time() - last_check < args.check_interval:
        cached_status = state.get("status")
        if cached_status:
            # Add version info to cached status if not present
            if "v" not in cached_status:
                cached_status += f" [v{__version__}]"
            print(cached_status)
        else:
            print(f"UNKNOWN - No cached status available [v{__version__}]")
        return

    result = check_domain(args.domain)
    if result[0] is None:
        print(f"UNKNOWN - Unable to retrieve domain information [v{__version__}]")
        return
    
    if result[0] == "UNREGISTERED":
        status = f"CRITICAL - Domain is unregistered. Registrar: N/A|days_to_expiration=-1;{args.warning_days};0;; [v{__version__}]"
        print(status)
        
        state["last_check"] = time.time()
        state["status"] = status
        state["registrar"] = "N/A"
        state["version"] = __version__
        save_state(state_file, state)
        return

    expiration_date, registrar = result

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    time_to_expiration = expiration_date - now
    days_to_expiration = time_to_expiration.total_seconds() / 86400  # Convert seconds to days

    rounded_days = round(days_to_expiration)
    
    # Generate CheckMK performance data
    perf_data = f"|days_to_expiration={days_to_expiration:.2f};{args.warning_days};0;;"

    if days_to_expiration < 0:
        status = f"CRITICAL - Domain is unregistered. Registrar: {registrar}{perf_data} [v{__version__}]"
    elif days_to_expiration <= args.warning_days:
        status = f"WARNING - Domain expires in {rounded_days} days. Registrar: {registrar}{perf_data} [v{__version__}]"
    else:
        status = f"OK - Domain is registered and expires in {rounded_days} days. Registrar: {registrar}{perf_data} [v{__version__}]"

    print(status)

    state["last_check"] = time.time()
    state["status"] = status
    state["registrar"] = registrar
    state["version"] = __version__
    save_state(state_file, state)

if __name__ == "__main__":
    main()