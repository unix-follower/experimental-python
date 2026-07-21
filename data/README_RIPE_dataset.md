# RIPE Atlas Traceroute Field Schema

Dataset downloaded from https://data-store.ripe.net/datasets/atlas-daily-dumps/

## Global Metadata Fields

* prb_id (Integer): Unique ID of the RIPE Atlas hardware/software probe that launched the test. Think of this as the origin network vantage point.
* src_addr (String): The source IP address (IPv4 or IPv6) of the probe interface.
* dst_addr (String): The destination IP address being targeted.
* dst_name (String): The target hostname or identifier (e.g., "cloudflare.com" or a root DNS string).
* af (Integer): Address Family. 4 means IPv4 network; 6 means IPv6 network.
* proto (String): The transport protocol used for path probing ("UDP" or "ICMP").

## The Hop Path Structural Data Array (result)

The result field is an array of objects representing each sequential step along the network path:

* hop (Integer): The current Time-To-Live (TTL) step counter (e.g., 1st router, 2nd router).
* result (Nested Array): By default, traceroute sends 3 packets per hop to verify stability. This sub-array contains the discrete performance responses for each packet:
* from (String): The actual IP address of the router responding at this specific hop.
   * rtt (Float): Round-Trip Time in milliseconds from the probe to this specific hop.
   * err (String, Optional): ICMP error tracking code (e.g., "H" for Host Unreachable, "N" for Network Unreachable). If a hop fails to reply entirely, the nested object contains a "x": "*" placeholder value (representing a timed-out hop).

## Node Mapping Matrix

| RIPE Atlas Data | Target Schema nodes Properties | Transformation Rule |
|---|---|---|
| src_addr, dst_addr, hop.result[].from | ip | Unique string collector across all files. Assigns next sequential integer id. |
| dst_name or from | label | Maps human-friendly network markers to endpoint nodes. |
| hop matching context | type | If it matches a src_addr or dst_addr record, type becomes "host". If it appears inside an intermediate path hop list, type becomes "router". |

## Edge Mapping Matrix

| RIPE Atlas Data | Target Schema edges Properties | Transformation Rule |
|---|---|---|
| hop[n] $\rightarrow$ hop[n+1] | source & target | Direct directional pointer linkage utilizing your custom sequential integer IDs. |
| hop.result[].rtt | cumulative_rtt_ms | Take the average or minimum of the 3 RTT float values present within the hop array. |
| Derived Math Calculation | link_rtt_ms | Calculate $\text{Avg RTT}_{\text{target}} - \text{Avg RTT}_{\text{source}}$. Clamp strictly to 0.0 if the value goes negative. |
| hop | ttl | Directly map the hop integer property. |
