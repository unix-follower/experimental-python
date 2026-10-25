import json
import sys

import networkx as nx
import pytest

from src.graph_theory.utils.ripe_parser import (
    NodeRegistry,
    _add_edges,
    _extract_router_hops,
    parse_to_networkx,
)

SAMPLE_NDJSON_LINE = json.dumps(
    {
        "fw": 5120,
        "mver": "2.6.4",
        "lts": 1957533,
        "endtime": 1781914563,
        "dst_name": "cloudflare.com",
        "ttr": 3.687453,
        "dst_addr": "104.16.132.229",
        "src_addr": "172.19.0.2",
        "proto": "ICMP",
        "af": 4,
        "size": 48,
        "paris_id": 5,
        "result": [
            {
                "hop": 1,
                "result": [
                    {"from": "172.19.0.1", "ttl": 64, "size": 76, "rtt": 0.435},
                    {"from": "172.19.0.1", "ttl": 64, "size": 76, "rtt": 0.707},
                ],
            },
            {
                "hop": 2,
                "result": [
                    {"from": "192.168.21.250", "ttl": 64, "size": 76, "rtt": 820.602}
                ],
            },
        ],
        "destination_ip_responded": False,
        "msm_id": 176906981,
        "prb_id": 1003959,
        "timestamp": 1781914556,
        "msm_name": "Traceroute",
        "from": "178.203.223.0",
        "type": "traceroute",
    }
)


# ---------------------------------------------------------------------------
# _extract_router_hops
# ---------------------------------------------------------------------------


class TestExtractRouterHops:
    def test_selects_lowest_rtt_response_per_hop(self):
        # given
        result = [
            {
                "hop": 1,
                "result": [
                    {"from": "10.0.0.1", "rtt": 5.0},
                    {"from": "10.0.0.1", "rtt": 2.5},
                ],
            }
        ]
        # when
        hops = _extract_router_hops(result)
        # then
        assert len(hops) == 1
        assert hops[0] == {
            "hop_ttl": 1,
            "ip": "10.0.0.1",
            "label": "10.0.0.1",
            "cumulative_rtt": 2.5,
        }

    def test_uses_host_label_when_present(self):
        # given
        result = [
            {
                "hop": 1,
                "result": [{"from": "10.0.0.1", "host": "router1.local", "rtt": 3.0}],
            }
        ]
        # when
        hops = _extract_router_hops(result)
        # then
        assert len(hops) == 1
        assert hops[0]["label"] == "router1.local"

    def test_skips_hops_with_no_valid_responses(self):
        # given
        result = [
            {"hop": 1, "result": [{"x": "*"}]},  # dropped packet, no "from"/"rtt"
            {"hop": 2, "result": [{"from": "10.0.0.2", "rtt": 4.0}]},
        ]
        # when
        hops = _extract_router_hops(result)
        # then
        assert len(hops) == 1
        assert hops[0]["hop_ttl"] == 2

    def test_empty_input_returns_empty_list(self):
        assert _extract_router_hops([]) == []

    def test_missing_result_key_treated_as_no_responses(self):
        # given
        result = [{"hop": 1}]
        # then
        assert _extract_router_hops(result) == []


# ---------------------------------------------------------------------------
# _create_edges
# ---------------------------------------------------------------------------


class TestCreateEdges:
    def _setup(self):
        graph = nx.DiGraph()
        registry = NodeRegistry(graph)
        src_id = registry.get_or_create_node(
            "192.168.1.1", label="src", node_type="host"
        )
        dst_id = registry.get_or_create_node("8.8.8.8", label="dst", node_type="host")
        return graph, registry, src_id, dst_id

    def test_builds_path_from_src_through_hops_to_dst(self):
        # given
        graph, registry, src_id, dst_id = self._setup()
        path_hops = [
            {"hop_ttl": 1, "ip": "10.0.0.1", "label": "r1", "cumulative_rtt": 10.0},
            {"hop_ttl": 2, "ip": "10.0.0.2", "label": "r2", "cumulative_rtt": 25.0},
        ]

        # when
        _add_edges(graph, src_id, dst_id, path_hops, registry.get_or_create_node)

        # then
        hop1_id = registry.ip_to_id["10.0.0.1"]
        hop2_id = registry.ip_to_id["10.0.0.2"]

        assert graph.number_of_edges() == 3
        assert graph[src_id][hop1_id]["cumulative_rtt_ms"] == 10.0
        assert graph[src_id][hop1_id]["link_rtt_ms"] == 10.0
        assert graph[hop1_id][hop2_id]["cumulative_rtt_ms"] == 25.0
        assert graph[hop1_id][hop2_id]["link_rtt_ms"] == 15.0
        # final hop -> destination
        assert graph[hop2_id][dst_id]["cumulative_rtt_ms"] == 25.0
        assert graph[hop2_id][dst_id]["link_rtt_ms"] == 0.0
        assert graph[hop2_id][dst_id]["ttl"] == 3

    def test_clamps_negative_link_rtt_to_zero(self):
        # given
        graph, registry, src_id, dst_id = self._setup()
        # Second hop reports a *lower* cumulative RTT than the first (noisy data)
        path_hops = [
            {"hop_ttl": 1, "ip": "10.0.0.1", "label": "r1", "cumulative_rtt": 50.0},
            {"hop_ttl": 2, "ip": "10.0.0.2", "label": "r2", "cumulative_rtt": 30.0},
        ]

        # when
        _add_edges(graph, src_id, dst_id, path_hops, registry.get_or_create_node)

        # then
        hop1_id = registry.ip_to_id["10.0.0.1"]
        hop2_id = registry.ip_to_id["10.0.0.2"]
        assert graph[hop1_id][hop2_id]["link_rtt_ms"] == 0.0

    def test_no_hops_produces_no_edges(self):
        # given
        graph, registry, src_id, dst_id = self._setup()
        # when
        _add_edges(graph, src_id, dst_id, [], registry.get_or_create_node)
        # then
        assert graph.number_of_edges() == 0

    def test_duplicate_edge_keeps_lower_cumulative_rtt(self):
        # given
        graph, registry, src_id, dst_id = self._setup()

        # when
        # First traceroute observes 20ms to the hop
        _add_edges(
            graph,
            src_id,
            dst_id,
            [{"hop_ttl": 1, "ip": "10.0.0.1", "label": "r1", "cumulative_rtt": 20.0}],
            registry.get_or_create_node,
        )
        # A later traceroute observes a *better* (lower) RTT to the same hop
        _add_edges(
            graph,
            src_id,
            dst_id,
            [{"hop_ttl": 1, "ip": "10.0.0.1", "label": "r1", "cumulative_rtt": 10.0}],
            registry.get_or_create_node,
        )

        # then
        hop1_id = registry.ip_to_id["10.0.0.1"]
        assert graph[src_id][hop1_id]["cumulative_rtt_ms"] == 10.0

        # when
        # A subsequent *worse* RTT should not overwrite the better one
        _add_edges(
            graph,
            src_id,
            dst_id,
            [{"hop_ttl": 1, "ip": "10.0.0.1", "label": "r1", "cumulative_rtt": 30.0}],
            registry.get_or_create_node,
        )
        # then
        assert graph[src_id][hop1_id]["cumulative_rtt_ms"] == 10.0

    def test_hop_to_dst_edge_is_only_created_once(self):
        # given
        # Documents current behavior: the last-hop -> destination edge is only
        # added the first time it's seen; later calls do not update its metrics
        # even if a better path is discovered.
        graph, registry, src_id, dst_id = self._setup()

        # when
        _add_edges(
            graph,
            src_id,
            dst_id,
            [{"hop_ttl": 1, "ip": "10.0.0.1", "label": "r1", "cumulative_rtt": 20.0}],
            registry.get_or_create_node,
        )
        _add_edges(
            graph,
            src_id,
            dst_id,
            [{"hop_ttl": 1, "ip": "10.0.0.1", "label": "r1", "cumulative_rtt": 5.0}],
            registry.get_or_create_node,
        )

        # then
        hop1_id = registry.ip_to_id["10.0.0.1"]
        # src -> hop edge was updated to the better RTT...
        assert graph[src_id][hop1_id]["cumulative_rtt_ms"] == 5.0
        # ...but the hop -> dst edge still reflects the first-seen RTT (20.0)
        assert graph[hop1_id][dst_id]["cumulative_rtt_ms"] == 20.0


# ---------------------------------------------------------------------------
# NodeRegistry
# ---------------------------------------------------------------------------


class TestNodeRegistry:
    def test_creates_new_node_with_expected_attributes(self):
        # given
        graph = nx.DiGraph()
        registry = NodeRegistry(graph)

        # when
        node_id = registry.get_or_create_node(
            "1.1.1.1", label="one", node_type="router"
        )

        # then
        assert node_id == 0
        assert graph.nodes[0] == {
            "ip": "1.1.1.1",
            "label": "one",
            "type": "router",
            "mac": None,
            "vendor": None,
        }

    def test_defaults_label_to_ip_when_not_provided(self):
        # given
        graph = nx.DiGraph()
        registry = NodeRegistry(graph)
        # when
        node_id = registry.get_or_create_node("1.1.1.1")
        # then
        assert graph.nodes[node_id]["label"] == "1.1.1.1"

    def test_returns_same_id_for_repeated_ip(self):
        # given
        graph = nx.DiGraph()
        registry = NodeRegistry(graph)
        # when
        id1 = registry.get_or_create_node("1.1.1.1")
        id2 = registry.get_or_create_node("1.1.1.1")
        # then
        assert id1 == id2
        assert graph.number_of_nodes() == 1

    def test_upgrades_label_only_if_current_label_is_still_the_ip(self):
        # given
        graph = nx.DiGraph()
        registry = NodeRegistry(graph)

        # when
        node_id = registry.get_or_create_node("2.2.2.2")  # label defaults to ip
        # then
        assert graph.nodes[node_id]["label"] == "2.2.2.2"

        # when
        registry.get_or_create_node("2.2.2.2", label="custom-name")
        # then
        assert graph.nodes[node_id]["label"] == "custom-name"

        # when
        # Once a real label is set, further generic labels don't override it
        registry.get_or_create_node("2.2.2.2", label="another-name")
        # then
        assert graph.nodes[node_id]["label"] == "custom-name"

    def test_upgrades_type_to_host(self):
        # given
        graph = nx.DiGraph()
        registry = NodeRegistry(graph)

        # when
        node_id = registry.get_or_create_node("3.3.3.3", node_type="router")
        # then
        assert graph.nodes[node_id]["type"] == "router"

        # when
        registry.get_or_create_node("3.3.3.3", node_type="host")
        # then
        assert graph.nodes[node_id]["type"] == "host"

    def test_type_does_not_downgrade_from_host(self):
        # given
        graph = nx.DiGraph()
        registry = NodeRegistry(graph)
        # when
        node_id = registry.get_or_create_node("4.4.4.4", node_type="host")
        registry.get_or_create_node("4.4.4.4", node_type="router")
        # then
        assert graph.nodes[node_id]["type"] == "host"


# ---------------------------------------------------------------------------
# parse_to_networkx (integration)
# ---------------------------------------------------------------------------


class TestParseToNetworkx:
    def test_parses_sample_line_into_expected_graph(self):
        # when
        graph = parse_to_networkx([SAMPLE_NDJSON_LINE])
        # then
        # src host, dst host, 2 routers = 4 nodes
        assert graph.number_of_nodes() == 4
        # src->hop1, hop1->hop2, hop2->dst = 3 edges
        assert graph.number_of_edges() == 3

        node_ips = {attrs["ip"] for _, attrs in graph.nodes(data=True)}
        assert node_ips == {
            "172.19.0.2",
            "104.16.132.229",
            "172.19.0.1",
            "192.168.21.250",
        }

        node_types = {attrs["ip"]: attrs["type"] for _, attrs in graph.nodes(data=True)}
        assert node_types["172.19.0.2"] == "host"
        assert node_types["104.16.132.229"] == "host"
        assert node_types["172.19.0.1"] == "router"
        assert node_types["192.168.21.250"] == "router"

    def test_first_hop_uses_minimum_rtt_of_duplicate_responses(self):
        # when
        graph = parse_to_networkx([SAMPLE_NDJSON_LINE])
        # then
        ip_to_id = {attrs["ip"]: n for n, attrs in graph.nodes(data=True)}
        src_id = ip_to_id["172.19.0.2"]
        hop1_id = ip_to_id["172.19.0.1"]
        # min(0.435, 0.707) == 0.435
        assert graph[src_id][hop1_id]["cumulative_rtt_ms"] == 0.435

    def test_skips_blank_lines(self):
        # when
        graph = parse_to_networkx(["", "   ", SAMPLE_NDJSON_LINE, ""])
        # then
        assert graph.number_of_nodes() == 4
        assert graph.number_of_edges() == 3

    def test_skips_invalid_json_lines_without_raising(self):
        # given
        lines = ["{not valid json", SAMPLE_NDJSON_LINE]
        # when
        graph = parse_to_networkx(lines)
        # then
        # the malformed line is skipped; the valid one is still parsed
        assert graph.number_of_nodes() == 4
        assert graph.number_of_edges() == 3

    def test_empty_input_produces_empty_graph(self):
        # when
        graph = parse_to_networkx([])
        # then
        assert graph.number_of_nodes() == 0
        assert graph.number_of_edges() == 0

    def test_multiple_lines_accumulate_into_shared_graph(self):
        # when
        graph = parse_to_networkx([SAMPLE_NDJSON_LINE, SAMPLE_NDJSON_LINE])
        # then
        # same src/dst/hops repeated -> nodes are deduplicated by IP
        assert graph.number_of_nodes() == 4
        assert graph.number_of_edges() == 3


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
