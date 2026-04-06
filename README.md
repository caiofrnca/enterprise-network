# Enterprise Network Simulation (EVE-NG)

## Objective
Simulate a multi-layer enterprise network with redundancy, routing protocols, and external connectivity to understand behavior during failure and convergence scenarios.

## Topology Overview
- Dual ISP connectivity
- Palo Alto firewall (zone-based)
- Core / Distribution / Access layers
- OSPF Area 0 internally
- HSRP for gateway redundancy
- LACP between access switches

## Key Technologies
BGP (planned), OSPF, HSRP, VLANs, LACP, NAT (future), firewall zones

## Scenarios Tested
- Link failure between Core and Distribution
- HSRP failover validation
- OSPF convergence behavior
- Access layer redundancy using LACP

## Tools
EVE-NG, Cisco IOS, Palo Alto VM, Wireshark, tcpdump
