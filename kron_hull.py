# kronfit for subgraphs

def getopts(argv):
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...
        if argv[0][0] == '-':  # Found a "-name value" pair.
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
    return opts

def kronfit(input_file, output_file):
    p = subprocess.Popen(['kronfit', 
                          '-i:' + input_file,
                          '-n0:2', '-gi:100',
                          '-o:' + output_file,], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
    

def sample(directory, p, i):
    random.shuffle(nodes)
    size = int(len(nodes) * float(p) / 100)
    sample = nodes[:size]
    sub_g = G.subgraph(sample)
    sub_g = sub_g.to_directed()  # Forgot to add
    nx.write_edgelist(sub_g, directory + str(p) + '/' 
                      + str(i) + '.edgelist', delimiter='\t', data=False)
    
def create_kronecker_hull(directory, points):
    hull = ConvexHull(points)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    vertX = points[hull.simplices, 0]
    vertY = points[hull.simplices, 1]
    vertZ = points[hull.simplices, 2]
    
    for s in hull.simplices:
        s = np.append(s, s[0])  # Here we cycle back to the first coordinate
        ax.plot(points[s, 0], points[s, 1], points[s, 2], "r-")

    ax.set_xlabel('a')
    ax.set_ylabel('b')
    ax.set_zlabel('d')

    plt.savefig(directory + 'kronecker_hull.jpg')
    
    vertX = vertX.reshape(vertX.shape[0]*vertX.shape[1], 1)
    vertY = vertY.reshape(vertY.shape[0]*vertY.shape[1], 1)
    vertZ = vertZ.reshape(vertZ.shape[0]*vertZ.shape[1], 1)
    vertices = np.concatenate((vertX, vertY), axis=1)
    vertices = np.concatenate((vertices, vertZ), axis=1)
    vertices = np.unique(vertices, axis=0)
    np.savetxt(directory + 'boundary.txt',vertices)


# myargs['-n'] network name
# myargs['-f'] edgelist file
# myargs['-s'] sampling step size
# myargs['-t'] number of samples for each sampling size

if __name__ == '__main__':
    from sys import argv
    import random, os, shutil, time
    import thread
    import math
    import subprocess
    import networkx as nx
    import re
    from scipy.spatial import ConvexHull
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    
    myargs = getopts(argv)
    print myargs
    
    network_name = myargs['-n']
    edgelist = myargs['-f']
    step = int(myargs['-s'])
    nos = int(myargs['-t'])
    
    directory = network_name + '/'
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)
    
    G = nx.read_edgelist(edgelist, delimiter='\t')
    nodes = list(G.nodes())
    
    nx.write_edgelist(G.to_directed(), directory + 'edgelist'
                       , delimiter='\t', data=False)
    
    full_input_file = directory + 'edgelist'
    full_output_file = directory + 'output.dat'
    kronfit(full_input_file, full_output_file)
    
    output = open(directory + 'kron_points.txt', 'w')
    kronecker_points = []
    
    for p in range(step, 100, step):
        os.mkdir(directory + str(p) + '/')
        for i in range(0, nos):
            sample(directory, p, i)
            input_file = directory + str(p) + '/' + str(i) + '.edgelist'
            output_file = directory + str(p) + '/' + str(i) + '_output.dat'
            kronfit(input_file, output_file)
    
    for p in range(step, 100, step):
        for i in range(0, nos):
            output_file = directory + str(p) + '/' + str(i) + '_output.dat'
            while(1):
                if not os.path.isfile(output_file):
                    print('Waiting for ' + output_file)
                    print('sleep 1 minute')
                    time.sleep(60)
                else:
                    break
                
            with open(output_file, 'r') as myfile:
                s = myfile.read()
                ret = re.findall(r'\[([^]]*)\]', s)
                split = ret[0].split(',')
                a = split[0]
                b = split[1].split(';')[0].strip()
                d = split[2].strip()
                output.write(str(a) + ',' + str(b) + ',' + str(d) + ',' + str(p) + '\n')
                kronecker_points.append([float(a), float(b), float(d)])
    
    
    while(1):
        if not os.path.isfile(full_output_file):
            print('Waiting for ' + full_output_file)
            print('sleep 1 minute')
            time.sleep(60)
        else:
            break
    with open(full_output_file, 'r') as myfile:
        s = myfile.read()
        ret = re.findall(r'\[([^]]*)\]', s)
        split = ret[0].split(',')
        a = split[0]
        b = split[1].split(';')[0].strip()
        d = split[2].strip()
        output.write(str(a) + ',' + str(b) + ',' + str(d) + ',' + str(100) + '\n') 
        kronecker_points.append([float(a), float(b), float(d)])

    output.close()
    
    kronecker_points = np.asarray(kronecker_points, dtype=np.float32)
    create_kronecker_hull(directory, kronecker_points)


