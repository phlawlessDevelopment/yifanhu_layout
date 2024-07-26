import multiprocessing as mp
import networkx as nx
import pandas as pd
import subprocess

import pkg_resources
import tempfile
import os

separator = ';' if os.name == "nt" else ':'

classpath = (
    pkg_resources.resource_filename("forceatlas", "ext/yifanhu.jar") +
    separator +
    pkg_resources.resource_filename("forceatlas", "ext/gephi-toolkit-0.9.2-all.jar")
)

def temp_filename() -> str:
    return next(tempfile._get_candidate_names())

    
def yifanhu_layout(
    G,
    pos=None,
    iterations=50,
    convergance_threshold = 1.0e-4, 
    relative_stregth = 0.2, 
    quadtree_max_level = 10, 
    adaptive_cooling = True, 
    barnes_hut_theta = 1.2, 
    initial_step = 20.0, 
    step_ratio = 0.95, 
    optimal_distance = 100, 
    n_jobs=mp.cpu_count(),
    seed=None,
):
    """Position nodes using ForceAtlas2 force-directed algorithm.

    Parameters
    ----------
    G : NetworkX graph or list of nodes
        A position will be assigned to every node in G.

    pos : dict or None  optional (default=None)
        Initial positions for nodes as a dictionary with node as keys
        and values as a coordinate list or tuple.  If None, then use
        random initial positions.

    iterations : int  optional (default=50)
        Maximum number of iterations taken


    optimal_distance : float optional (default=100.0)
        The natural length of the springs. Bigger values mean nodes will be farther apart.

    step_ratio : float optional (default=0.95)
        The ratio used to update the step size across iterations.

    initial_step : float optional (default=20.0)
        The initial step size used in the integration phase. Set this value to a meaningful size compared to the optimal distance (10% is a good starting point).

    barnes_hut_theta : float optional (default=1.2)
        The theta parameter for Barnes-Hut opening criteria. Smaller values mean more accuracy.

   adaptive_cooling : bool optional (default=True)  
        Controls the use of adaptive cooling. It is used help the layout algoritm to avoid energy local minima.

    quad_tree_max_level : int optional (default=10)
        The maximum level to be used in the quadtree representation. Greater values mean more accuracy.

    relative_strength : float optional (default=0.2)
        The relative strength between electrical force (repulsion) and spring force (attraction).

    convergence_threshold : float optional (default=1.0e-4)
        Relative energy convergence threshold. Smaller values mean more accuracy.

      
    n_jobs : int  optional (defaults to all cores)
        Number of threads to use for parallel computation.
        If None, defaults to all cores as detected by
        multiprocessing.cpu_count().

    seed : int or None  optional (default=None)
        Seed for random number generation for initial node position.
        If int, `seed` is the seed used by the random number generator,
        if None, the random number generator is chosen randomly.

    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node

    Examples
    --------
    >>> import yifanhu as yifanhu
    >>> G = nx.path_graph(4)
    >>> pos = yifanhu.yifanhu_layout(G)
    """
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
                "-Xmx8g",
                "-cp",
                classpath,
                "Main",
                "--input",
                temp_graph_filename,
                "--output",
                output_filename,
                "--nthreads",
                str(n_jobs),
                "--iterations",
                str(iterations),
                "--converganceThreshold", 
                str(convergance_threshold), 
                "--relative_stregth",
                str(relative_stregth), 
                "--quadTreeMaxLevel",
                str(quadtree_max_level), 
                "---barnesHutTheta",
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
                row = {"id": mapping[label], "x": coords[0], "y": coords[1], "z":coords[2]}
                pos_list.append(row)
            pos_list = pd.DataFrame(pos_list)
            pos_list.to_csv(temp_pos_filename, sep='\t')
            command.extend(["--coords", temp_pos_filename])
            
        subprocess.check_call(command)
        
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
            
if __name__ == "__main__":
    import networkx as nx
    G = nx.path_graph(4)
    pos = yifanhu_layout(G)
