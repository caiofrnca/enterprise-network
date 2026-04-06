## Enterprise Network Lab (EVE-NG)

### Overview
This project simulates a multi-layer enterprise network using EVE-NG to model real-world network behavior, redundancy, and failure scenarios. The lab is designed to reflect concepts used in data center and backbone environments, including routing, high availability, and operational validation.

### Objectives
- Build a scalable network topology with Core, Distribution, and Access layers  
- Implement routing and redundancy protocols (OSPF, HSRP, LACP)  
- Simulate failure scenarios and observe convergence behavior  
- Validate network health using Python automation (Netmiko)  
- Develop a structured, reproducible lab environment  


### Topology
- Dual-core architecture (R1, R2)  
- Distribution layer with gateway redundancy (R3, R4)  
- Access layer with LACP uplinks  
- Palo Alto firewall for northbound connectivity  
- External ISP simulation (BGP-ready design)  

See: `topology/diagram.png`  


### Technologies Used
- Routing: OSPF (Area 0), BGP (core/edge design)  
- Redundancy: HSRP (Layer 3 gateway), LACP (Layer 2)  
- Segmentation: VLANs (Users, Servers, Mgmt)  
- Automation: Python (Netmiko)  
- Monitoring: Wireshark, tcpdump  
- Platform: EVE-NG (Cisco IOS, multi-vendor simulation)  


### Key Scenarios Tested

#### 1. Core Link Failure
- Simulated link failure between Core and Distribution  
- Observed OSPF reconvergence and traffic rerouting  

#### 2. HSRP Failover
- Simulated active gateway failure  
- Verified standby router takeover with minimal disruption  

#### 3. LACP Redundancy
- Disabled one link in port-channel  
- Verified continued connectivity over remaining link  

#### 4. Routing Validation via Automation
- Used Python script to validate:
  - OSPF neighbor status  
  - BGP session visibility  
  - Default route presence  
  - HSRP state  

See: `tests/failure-tests.md`  



### Automation (Netmiko)

A Python-based validation tool was developed to simulate operational network checks:

#### Features
- Connects to multiple devices (routers/switches)  
- Executes protocol and redundancy validation commands  
- Evaluates outputs (PASS / WARN / FAIL)  
- Generates per-device reports  

#### Example Checks
- `show ip ospf neighbor`  
- `show ip bgp summary`  
- `show standby brief`  
- `show etherchannel summary`  

Script: `automation/netmiko-checks.py`  
Output: `automation/outputs/`  



### Configuration Samples
Sanitized configurations are included to demonstrate implementation:

- Core Router (R1): OSPF, BGP, default routing  
- Distribution Router (R3): OSPF, HSRP, VLAN gateways  

See:  
- `configs/core/R1.cfg`  
- `configs/distribution/R3.cfg`  


### Repository Structure
topology/ → Network diagram and addressing
configs/ → Device configurations (sanitized)
routing/ → Protocol notes (OSPF, HSRP, BGP)
automation/ → Netmiko validation scripts
monitoring/ → Packet analysis and troubleshooting notes
tests/ → Failure scenarios and validation results
docs/ → Architecture and design notes

---

### Key Learnings
- OSPF convergence behavior impacts traffic during failures  
- HSRP provides reliable gateway redundancy with minimal downtime  
- LACP improves availability and load balancing at Layer 2  
- Automation reduces manual validation effort and improves consistency  
- Structured testing improves understanding of real-world network behavior  


### Future Improvements
- Implement full BGP dual-ISP failover testing  
- Add firewall NAT and security policies  
- Enhance automation with logging, alerts, and retry logic  
- Export validation results to CSV/JSON  
- Integrate monitoring tools (SNMP / Prometheus)  

---

### Portfolio
- GitHub: https://github.com/caiofrnca  
- Portfolio: https://caiofrnca.github.io