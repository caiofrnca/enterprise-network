### Failure & Validation Tests

##### Objective
Validate network resilience, redundancy, and convergence behavior across the enterprise topology under failure conditions.

---

#### Test 1: Core to Distribution Link Failure

##### Scenario
Simulate failure between CORE1 (R1) and DIST1 (R3)

##### Action
Shutdown interface on R1:
```bash
interface e0/0  
shutdown  
```
##### Expected Behavior
- Traffic should reroute via CORE2 (R2)
- OSPF should reconverge and update routing tables

##### Observed Result
- OSPF adjacency recalculated
- Traffic successfully rerouted through alternate path
- Convergence time: ~3–5 seconds
- Minimal packet loss observed

##### Key Learning
OSPF provides dynamic rerouting, but convergence time can impact real-time applications.

---

#### Test 2: HSRP Failover (Gateway Redundancy)

##### Scenario
Simulate failure of active gateway router (R3)

##### Action
Shutdown interface on R3:
```bash
interface e0/1  
shutdown  
```
##### Expected Behavior
- R4 (standby) becomes active gateway
- Virtual IP (10.10.x.1) remains reachable

##### Observed Result
- HSRP failover occurred successfully
- Gateway switched to R4
- ~1–2 dropped pings during transition

##### Key Learning
HSRP ensures high availability at Layer 3 with minimal disruption.

---

#### Test 3: Access Layer Link Failure (LACP)

##### Scenario
Simulate failure of one link in LACP bundle between ACCESS switches

##### Action
Shutdown one interface in port-channel:
```bash
interface e3/0  
shutdown  
```
##### Expected Behavior
- Traffic continues over remaining link
- No major disruption

##### Observed Result
- LACP maintained connectivity
- No noticeable traffic interruption

##### Key Learning
LACP provides redundancy and load balancing at Layer 2.

---

#### Test 4: OSPF Neighbor Loss

##### Scenario
Break adjacency between distribution routers (R3 and R4)

##### Action
Shutdown link:
```bash
interface e0/1  
shutdown  
```
##### Expected Behavior
- OSPF neighbor goes down
- Routes recalculated

##### Observed Result
- OSPF adjacency lost and recalculated
- Alternate routing paths used

##### Key Learning
OSPF quickly adapts to topology changes but depends on timer configuration.

---

#### Test 5: Device Reachability Failure (Automation Validation)

##### Scenario
Simulate router being unreachable

##### Action
Shutdown management or disconnect router

##### Expected Behavior
- Netmiko script fails to connect
- Error handling triggered

##### Observed Result
- Script detected unreachable device
- Output flagged failure

##### Key Learning
Automation can be used for fast detection of network health issues.

---

### Future Improvements

- Implement BGP with dual ISP for external failover testing
- Add firewall NAT and security policies
- Introduce monitoring tools (e.g., Prometheus, SNMP polling)
- Improve automation with logging and alerting