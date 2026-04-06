from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)

from devices import DEVICES


VALIDATION_COMMANDS: Dict[str, List[str]] = {
    "R1": [
        "show ip bgp summary",
        "show ip ospf neighbor",
        "show ip route 0.0.0.0",
    ],
    "R2": [
        "show ip bgp summary",
        "show ip ospf neighbor",
        "show ip route 0.0.0.0",
    ],
    "R3": [
        "show standby brief",
        "show ip ospf neighbor",
    ],
    "R4": [
        "show standby brief",
        "show ip ospf neighbor",
    ],
    "AC-SW1": [
        "show etherchannel summary",
        "show interfaces trunk",
        "show cdp neighbors",
    ],
    "AC-SW2": [
        "show etherchannel summary",
        "show interfaces trunk",
        "show cdp neighbors",
    ],
    "ISP1": [
        "show ip bgp summary",
        "show ip bgp",
    ],
    "ISP2": [
        "show ip bgp summary",
        "show ip bgp",
    ],
}

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_filename(name: str) -> str:
    return name.lower().replace(" ", "_")


def evaluate_output(command: str, output: str) -> Tuple[str, str]:
    """
    Return a simple status and reason based on command output.
    Status values: PASS, WARN, FAIL
    """
    lower_output = output.lower()

    if "% invalid" in lower_output or "unknown command" in lower_output:
        return "FAIL", "Command not supported on device"

    if "show ip ospf neighbor" in command:
        if "full/" in lower_output or "\nfull" in lower_output:
            return "PASS", "OSPF neighbor adjacency detected"
        if "neighbor id" in lower_output:
            return "WARN", "OSPF output present, but FULL state not clearly detected"
        return "FAIL", "No OSPF neighbors detected"

    if "show ip bgp summary" in command:
        if "neighbor" in lower_output and ("established" in lower_output or any(char.isdigit() for char in output)):
            return "PASS", "BGP summary returned neighbor/session data"
        if "neighbor" in lower_output:
            return "WARN", "BGP summary returned, but session state unclear"
        return "FAIL", "No BGP neighbor data detected"

    if "show ip route 0.0.0.0" in command:
        if "0.0.0.0/0" in output or "* 0.0.0.0/0" in output or "gateway of last resort" in lower_output:
            return "PASS", "Default route present"
        return "WARN", "Default route not clearly present"

    if "show standby brief" in command:
        if "active" in lower_output or "standby" in lower_output:
            return "PASS", "HSRP state information detected"
        return "WARN", "HSRP output returned, but active/standby state unclear"

    if "show etherchannel summary" in command:
        if "(su)" in lower_output or "po" in lower_output:
            return "PASS", "EtherChannel appears operational"
        return "WARN", "EtherChannel output present, but state unclear"

    if "show interfaces trunk" in command:
        if "trunking" in lower_output or "vlans allowed" in lower_output:
            return "PASS", "Trunk interface information detected"
        return "WARN", "Trunk output returned, but status unclear"

    if "show cdp neighbors" in command:
        if "device id" in lower_output:
            return "PASS", "CDP neighbor information detected"
        return "WARN", "No CDP neighbors detected"

    if "show ip bgp" in command:
        if "network" in lower_output or "path" in lower_output:
            return "PASS", "BGP table output detected"
        return "WARN", "BGP table returned, but content unclear"

    return "WARN", "No rule defined for this command; output collected only"


def write_device_report(device_name: str, report_lines: List[str]) -> Path:
    file_name = f"{safe_filename(device_name)}_report.txt"
    report_path = OUTPUT_DIR / file_name
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    return report_path


def run_checks() -> None:
    overall_summary: List[Dict[str, str]] = []

    print(f"\n[{timestamp()}] Starting network validation checks\n")

    for device in DEVICES:
        device_name = device["name"]
        device_host = device["host"]

        print("=" * 100)
        print(f"[{timestamp()}] Connecting to {device_name} ({device_host})")
        print("=" * 100)

        commands = VALIDATION_COMMANDS.get(device_name, [])
        if not commands:
            print(f"[WARN] No commands defined for {device_name}\n")
            overall_summary.append(
                {
                    "device": device_name,
                    "host": device_host,
                    "status": "WARN",
                    "details": "No commands defined",
                }
            )
            continue

        device_report: List[str] = [
            "=" * 100,
            f"Device: {device_name}",
            f"Host: {device_host}",
            f"Run Time: {timestamp()}",
            "=" * 100,
        ]

        device_failed = False
        device_warn = False

        try:
            conn = ConnectHandler(
                device_type=device["device_type"],
                host=device["host"],
                username=device["username"],
                password=device["password"],
                fast_cli=False,
            )

            for command in commands:
                print(f"\n--- {device_name} | {command} ---")
                output = conn.send_command(command, read_timeout=30)
                status, reason = evaluate_output(command, output)

                print(output)
                print(f"[{status}] {reason}")

                device_report.extend(
                    [
                        "",
                        "-" * 100,
                        f"COMMAND: {command}",
                        f"STATUS : {status}",
                        f"DETAIL : {reason}",
                        "-" * 100,
                        output,
                    ]
                )

                if status == "FAIL":
                    device_failed = True
                elif status == "WARN":
                    device_warn = True

            conn.disconnect()

            report_path = write_device_report(device_name, device_report)

            if device_failed:
                final_status = "FAIL"
                final_details = "One or more command checks failed"
            elif device_warn:
                final_status = "WARN"
                final_details = "Checks completed with warnings"
            else:
                final_status = "PASS"
                final_details = "All checks passed"

            overall_summary.append(
                {
                    "device": device_name,
                    "host": device_host,
                    "status": final_status,
                    "details": final_details,
                }
            )

            print(f"\n[OK] Completed checks on {device_name}")
            print(f"[INFO] Report saved to: {report_path}\n")

        except NetmikoAuthenticationException:
            msg = f"Authentication failed for {device_name} ({device_host})"
            print(f"[ERROR] {msg}\n")
            overall_summary.append(
                {
                    "device": device_name,
                    "host": device_host,
                    "status": "FAIL",
                    "details": msg,
                }
            )

        except NetmikoTimeoutException:
            msg = f"Connection timed out for {device_name} ({device_host})"
            print(f"[ERROR] {msg}\n")
            overall_summary.append(
                {
                    "device": device_name,
                    "host": device_host,
                    "status": "FAIL",
                    "details": msg,
                }
            )

        except Exception as exc:
            msg = f"Unexpected issue on {device_name} ({device_host}): {exc}"
            print(f"[ERROR] {msg}\n")
            overall_summary.append(
                {
                    "device": device_name,
                    "host": device_host,
                    "status": "FAIL",
                    "details": msg,
                }
            )

    print("\n" + "=" * 100)
    print(f"[{timestamp()}] Validation Summary")
    print("=" * 100)

    pass_count = 0
    warn_count = 0
    fail_count = 0

    for result in overall_summary:
        print(
            f"{result['device']:10} | {result['host']:15} | "
            f"{result['status']:4} | {result['details']}"
        )

        if result["status"] == "PASS":
            pass_count += 1
        elif result["status"] == "WARN":
            warn_count += 1
        else:
            fail_count += 1

    print("-" * 100)
    print(f"PASS: {pass_count} | WARN: {warn_count} | FAIL: {fail_count}")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    run_checks()