import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from yifanhu import yifanhu_layout as layout
import networkx as nx

# Create a random graph
G = nx.fast_gnp_random_graph(100, 0.1)

# Draw initial graph without layout
fig = plt.figure(figsize=(10, 5))

# Plot initial random layout in 3D
ax1 = fig.add_subplot(121, projection='3d')
pos_initial = nx.random_layout(G, dim=3)
xs, ys, zs = zip(*[pos_initial[n] for n in G.nodes])
ax1.scatter(xs, ys, zs, c='r', s=20)
for edge in G.edges:
    x = [pos_initial[edge[0]][0], pos_initial[edge[1]][0]]
    y = [pos_initial[edge[0]][1], pos_initial[edge[1]][1]]
    z = [pos_initial[edge[0]][2], pos_initial[edge[1]][2]]
    ax1.plot(x, y, z, color='b')
ax1.set_title("Graph with Random Layout")

# Save the initial layout plot
plt.savefig("graph_no_pos.png")

# Apply Yifan Hu layout
pos = layout(G, iterations=10000)
print(pos)

# Plot Yifan Hu layout in 3D
ax2 = fig.add_subplot(122, projection='3d')
xs, ys, zs = zip(*[pos[n] for n in G.nodes])
ax2.scatter(xs, ys, zs, c='r', s=20)
for edge in G.edges:
    x = [pos[edge[0]][0], pos[edge[1]][0]]
    y = [pos[edge[0]][1], pos[edge[1]][1]]
    z = [pos[edge[0]][2], pos[edge[1]][2]]
    ax2.plot(x, y, z, color='b')
ax2.set_title("Graph with Yifan Hu Layout")

# Save the Yifan Hu layout plot
plt.savefig("graph_pos.png")

# Show both plots
plt.show()

