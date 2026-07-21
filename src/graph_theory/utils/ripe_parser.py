import logging as log
from collections.abc import Callable
import json
import argparse
import networkx as nx
from src.config.log_settings import configure_logging
from src import constants


def _extract_router_hops(result: list[dict]):
    path_hops: list[dict] = []
    for hop_entry in result:
        hop_index = hop_entry.get("hop")
        hop_results = hop_entry.get("result", [])

        # Filter out dropped packet hops ("*") and collect valid responses
        valid_responses = [r for r in hop_results if "from" in r and "rtt" in r]
        if not valid_responses:
            continue  # Skip this hop index to automatically bridge gaps

        # Pick best response using minimum RTT (closest approximation of pure transmission speed)
        best_res = min(valid_responses, key=lambda x: x["rtt"])

        path_hops.append(
            {
                "hop_ttl": hop_index,
                "ip": best_res["from"],
                "label": best_res.get("host", best_res["from"]),
                "cumulative_rtt": best_res["rtt"],
            }
        )
    return path_hops


def _add_edges(
    graph: nx.DiGraph,
    src_id,
    dst_id,
    path_hops: list[dict],
    get_or_create_node: Callable[[str, str | None], int],
):
    # Connect source node directly to the first discovered hop
    previous_node_id = src_id
    previous_rtt = 0.0  # Safe baseline origin latency

    for hop in path_hops:
        current_node_id = get_or_create_node(
            hop["ip"], label=hop["label"], node_type="router"
        )

        # Compute link latency via relative subtraction
        cumulative_rtt = hop["cumulative_rtt"]
        link_rtt = cumulative_rtt - previous_rtt
        if link_rtt < 0:
            link_rtt = (
                0.00  # Strict clamp to preserve correctness for Dijkstra routines
            )

        # Add or update edge attributes (taking the best performance metrics on duplicate paths)
        if graph.has_edge(previous_node_id, current_node_id):
            existing_edge = graph[previous_node_id][current_node_id]
            if cumulative_rtt < existing_edge["cumulative_rtt_ms"]:
                graph[previous_node_id][current_node_id]["cumulative_rtt_ms"] = (
                    cumulative_rtt
                )
                graph[previous_node_id][current_node_id]["link_rtt_ms"] = link_rtt
        else:
            graph.add_edge(
                previous_node_id,
                current_node_id,
                cumulative_rtt_ms=cumulative_rtt,
                link_rtt_ms=link_rtt,
                ttl=hop["hop_ttl"],
            )

        previous_node_id = current_node_id
        previous_rtt = cumulative_rtt

    # Connect last discovered hop straight to final destination endpoint node
    if path_hops:
        # Recompute link latency for last link
        last_link_rtt = 0.0  # We don't have dst RTT if destination_ip_responded is false, fallback to 0
        if not graph.has_edge(previous_node_id, dst_id):
            graph.add_edge(
                previous_node_id,
                dst_id,
                cumulative_rtt_ms=previous_rtt,
                link_rtt_ms=last_link_rtt,
                ttl=path_hops[-1]["hop_ttl"] + 1,
            )


class NodeRegistry:
    def __init__(self, graph: nx.DiGraph):
        # Tracking maps for tracking unique IPs and assigning sequential integer IDs
        self.ip_to_id = {}
        self.next_node_id = 0
        self.graph = graph

    def get_or_create_node(self, ip: str, label: str | None = None, node_type="router"):
        if ip not in self.ip_to_id:
            node_id = self.next_node_id
            self.ip_to_id[ip] = node_id
            self.next_node_id += 1

            # Initialize node in NetworkX with standard streamlined schema
            self.graph.add_node(
                node_id, ip=ip, label=label or ip, type=node_type, mac=None, vendor=None
            )
        else:
            node_id = self.ip_to_id[ip]
            # Upgrade node label/type if more accurate info arrives from endpoints
            if label and self.graph.nodes[node_id]["label"] == ip:
                self.graph.nodes[node_id]["label"] = label
            if node_type == "host":
                self.graph.nodes[node_id]["type"] = "host"

        return node_id


def parse_to_networkx(traceroute_lines: list[str]):
    """
    Parses RIPE Atlas traceroute NDJSON lines into a NetworkX DiGraph
    using the optimized, portable integer-ID schema.
    """
    graph = nx.DiGraph()
    registry = NodeRegistry(graph)

    for index, line in enumerate(traceroute_lines):
        if not line.strip():
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            log.warning(f"Failed to decode JSON line at index {index}. Skipping")
            continue

        # 1. Register or update target/source endpoints
        src_id = registry.get_or_create_node(
            record["src_addr"], label=record.get("from"), node_type="host"
        )
        dst_id = registry.get_or_create_node(
            record["dst_addr"], label=record.get("dst_name"), node_type="host"
        )

        # 2. Extract and linearize valid router hops
        path_hops = _extract_router_hops(record.get("result", []))

        # 3. Create directional structural edges along the parsed path
        _add_edges(graph, src_id, dst_id, path_hops, registry.get_or_create_node)

    return graph


def main():
    configure_logging()

    parser = argparse.ArgumentParser(
        description="Parse RIPE Atlas traceroute NDJSON file."
    )
    parser.add_argument(
        "filename", type=str, help="The name of the file to process (required)"
    )
    args = parser.parse_args()

    with open(args.filename, "r", encoding=constants.UTF8) as file:
        traceroute_lines = file.read().splitlines()

    graph = parse_to_networkx(traceroute_lines)

    log.info(f"Total Vertices: {graph.number_of_nodes()}")
    log.info(f"Total Edges: {graph.number_of_edges()}\n")

    log.info("Inspecting Generated Vertices Payload:")
    for nid, attrs in graph.nodes(data=True):
        log.info(f" ID {nid}: {attrs}")

    log.info("\nInspecting Path Performance Edge Weights:")
    for src, dst, attrs in graph.edges(data=True):
        log.info(
            f" Link {src} -> {dst} | Link RTT: {attrs['link_rtt_ms']}ms | Cumulative RTT: {attrs['cumulative_rtt_ms']}ms"
        )


if __name__ == "__main__":
    main()
