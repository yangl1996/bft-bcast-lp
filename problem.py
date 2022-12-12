import pulp as pl

# the first node is the leader
ingress = [10.0, 10.0, 10.0, 10.0]
egress = [10.0, 10.0, 10.0, 10.0]

if len(ingress) != len(egress):
    print("ingress and egress constraints do not match")
    exit(1)

N = len(ingress)

nodes = [i for i in range(N)]
dests = [i for i in range(N) if i != 0]

# rate on each edge in flows from leader to each follower
flowEdgeVars = pl.LpVariable.dicts("FlowEdge", (dests, nodes, nodes), lowBound=0)
# edge cap satisfying node cap
edgeCapVars = pl.LpVariable.dicts("EdgeCap", (nodes, nodes), lowBound=0)
# min over max flows from leader to each follower
minMaxFlowVar = pl.LpVariable("MinMaxFlow", lowBound=0)

prob = pl.LpProblem("BftBcast", pl.LpMinimize)

# objective
prob += (-minMaxFlowVar, "NCThroughput")

# no loopback
for d in dests:
    for n in nodes:
        prob += (flowEdgeVars[d][n][n] == 0, f"NoLoopbackFlow{d}Node{n}")
for n in nodes:
    prob += (edgeCapVars[n][n] == 0, f"NoLoopbackCapNode{n}")

# egress caps
for n in nodes:
    prob += (pl.lpSum([edgeCapVars[n][i] for i in nodes]) <= egress[n], f"EgressCapNode{n}")

# ingress caps
for n in nodes:
    prob += (pl.lpSum([edgeCapVars[i][n] for i in nodes]) <= ingress[n], f"IngressCapNode{n}")

# flow conservation
for d in dests:
    for n in nodes:
        if n != 0 and n != d:
            prob += (pl.lpSum([flowEdgeVars[d][n][i] for i in nodes]) - pl.lpSum([flowEdgeVars[d][i][n] for i in nodes]) == 0, f"FlowConservationFlow{d}Node{n}")

# edge capacity
for n in nodes:
    for m in nodes:
        for d in dests:
            prob += (edgeCapVars[n][m] - flowEdgeVars[d][n][m] >= 0, f"EdgeCapFlow{d}From{n}To{m}")

# definition of minMaxFlow
for d in dests:
    prob += (pl.lpSum([flowEdgeVars[d][0][i] for i in nodes]) - minMaxFlowVar >= 0, f"MinMaxNoGreaterThanFlow{d}")

prob.writeMPS("throughput.mps")
