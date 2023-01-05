# the first node is the leader
ingress = [10.0, 100.0, 100.0, 100.0]
egress = [100.0, 200.0, 100.0, 10.0]
N = len(ingress)

def maxMin(credit, cap):
    n = len(cap)
    f = [0.0] * n
    while credit > 0.000001:
        ndist = 0
        for i in range(n):
            if cap[i] - f[i] > 0.000001:
                ndist += 1
        if ndist == 0:
            break
        dist = credit / ndist
        for i in range(n):
            if cap[i] - f[i] <= dist:
                credit -= (cap[i] - f[i])
                f[i] = cap[i]
            else:
                f[i] += dist
                credit -= dist
    return f

dt = maxMin(egress[0], ingress[1:])
dt = [0.0] + dt
fromLeader = [x for x in dt]
for i in range(1, N):
    ingress[i] -= dt[i]

for i in range(1, N):
    caps = []
    index = []
    for j in range(1, N):
        if i != j:
            caps.append(ingress[j])
            index.append(j)
    maxBcast = maxMin(egress[i], caps)
    for idx in range(len(index)):
        update = maxBcast[idx]
        if update > fromLeader[i]:
            update = fromLeader[i]
        ingress[index[idx]] -= update
        dt[index[idx]] += update

print(dt)
