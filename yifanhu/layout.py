import multiprocessing as mp
import networkx as nx
import pandas as pd
import subprocess
import pkg_resources
import tempfile
import os

separator = ';' if os.name == "nt" else ':'

classpath = (
    pkg_resources.resource_filename("yifanhu", "ext/yifanhu.jar") +
    separator +
    pkg_resources.resource_filename("yifanhu", "ext/gephi-toolkit-0.9.2-all.jar")
)

def temp_filename() -> str:
    return next(tempfile._get_candidate_names())

def yifanhu_layout(
    G,
    pos=None,
    iterations=50,
    convergence_threshold=1.0e-4,
    relative_strength=0.2,
    quadtree_max_level=10,
    adaptive_cooling=True,
    barnes_hut_theta=1.2,
    initial_step=20.0,
    step_ratio=0.95,
    optimal_distance=100,
    seed=None,
):
    try:
        if not isinstance(G, nx.Graph):
            empty_graph = nx.Graph()
            empty_graph.add_nodes_from(G)
            G = empty_graph

        mapping = {label: index for index, label in enumerate(G.nodes())}
        inverse_mapping = {index: label for label, index in mapping.items()}
        H = nx.relabel_nodes(G, mapping)

        temp_graph_filename = temp_filename() + ".net"
        nx.write_pajek(H, temp_graph_filename)

        output_filename = temp_filename() + ".coords"

        command = [
            "java",
            "-Djava.awt.headless=true",
            "-Xmx4g",
            "-cp",
            classpath,
            "Main",
            "--input",
            temp_graph_filename,
            "--output",
            output_filename,
            "--iterations",
            str(iterations),
            "--convergenceThreshold",
            str(convergence_threshold),
            "--relativeStrength",
            str(relative_strength),
            "--quadTreeMaxLevel",
            str(quadtree_max_level),
            "--barnesHutTheta",
            str(barnes_hut_theta),
            "--initialStep",
            str(initial_step),
            "--stepRatio",
            str(step_ratio),
            "--optimalDistance",
            str(optimal_distance),
            "--adaptiveCooling",
            str(adaptive_cooling),
        ]

        if seed is not None:
            command.extend(["--seed", str(seed)])

        if pos is not None:
            temp_pos_filename = temp_filename() + ".csv"
            pos_list = []
            for label, coords in pos.items():
                row = {"id": mapping[label], "x": coords[0], "y": coords[1], "z": coords[2]}
                pos_list.append(row)
            pos_list = pd.DataFrame(pos_list)
            pos_list.to_csv(temp_pos_filename, sep='\t')
            command.extend(["--coords", temp_pos_filename])

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Java process failed with return code {result.returncode}.\n"
                               f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}")

        coordinates = pd.read_csv(output_filename + ".txt", header=0, index_col=0, sep="\t").values

        if pos is not None:
            os.remove(temp_pos_filename)

        os.remove(temp_graph_filename)
        os.remove(output_filename + ".txt")

        if os.path.exists(output_filename + ".distances.txt"):
            os.remove(output_filename + ".distances.txt")

        pos = {inverse_mapping[i]: x for i, x in enumerate(coordinates)}

        return pos
    except Exception as e:
        raise e
    finally:
        for path in [temp_graph_filename, output_filename + ".txt", output_filename + ".distances.txt"]:
            if os.path.exists(path):
                os.remove(path)

        while True:
            try:
                os.remove(temp_pos_filename)
                break
            except KeyboardInterrupt:
                continue
            except:
                break

