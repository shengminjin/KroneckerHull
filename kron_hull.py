'''
Reference implementation of Kronecker Hull. 
Author: Shengmin Jin
For more details, refer to the paper:
Representing Networks with 3D Shapes
Shengmin Jin and Reza Zafarani
IEEE International Conference on Data Mining (ICDM), 2018

Versions: 1.0    The Original Version
          1.1    Code Optimization
          1.2    Bug fix for python subprocess hang
          1.3    Bug fix for wrong output
          1.4    Improve parallel running
'''

from sys import argv
import random, os, shutil, time
import math
import subprocess
import networkx as nx
import re
from scipy.spatial import ConvexHull
import numpy as np
import matplotlib
import argparse
matplotlib.use('Agg')
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from tqdm import tqdm
from joblib import Parallel, delayed

# create subprocess for kronfit
def kronfit(kronfit_job):
    input_file_path = kronfit_job[0]
    output_file_path = kronfit_job[1]
    if not os.path.exists(output_file_path):
        cmd = 'kronfit', '-i:' + input_file_path, '-n0:2', '-gi:100', '-o:' + output_file_path
        subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()

# sample a subgraph
def sample(directory, p, i):
    random.shuffle(nodes)
    size = int(len(nodes) * float(p) / 100)
    sample = nodes[:size]
    sub_g = G.subgraph(sample)
    sub_g = sub_g.to_directed()  # Forgot to add
    nx.write_edgelist(sub_g, directory + str(p) + '/' 
                      + str(i) + '.edgelist', delimiter='\t', data=False)
    
# create a Kronecker hull
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


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description='Generating a 3D Network Shapes with a Kronecker Hull')

    parser.add_argument('-n', required=False,
                        default='as20graph',
                        help='Network name')

    parser.add_argument('-f', required=False,
                        default='as20graph.txt',
                        help='Input edge list file name.')

    parser.add_argument('-s', required=False,
                        default=20,
                        help='Sampling proportion step (percentage)')

    parser.add_argument('-t', required=False,
                        default=5,
                        help='Number of samples for each sampling proporation"')
    
#    network_name = myargs['-n']
#    edgelist = myargs['-f']
#    step = int(myargs['-s'])
#    nos = int(myargs['-t'])

    args = parser.parse_args()

    # print("Command: {}".format(args.command))
    print("Network name: {}".format(args.n))
    print("Input edge file: {}".format(args.f))
    print("Sampling proportion step: {}".format( args.s))
    print("Number of samples for each sampling proportion: {}\n\n".format(args.t))
    
    network_name = args.n
    edgelist = args.f
    step = int(args.s)
    nos = int(args.t)
    
    directory = network_name + '/'
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)

    G = nx.read_edgelist(edgelist, delimiter='\t')
    nodes = list(G.nodes())
    
    nx.write_edgelist(G.to_directed(), directory + 'edgelist'
                       , delimiter='\t', data=False)

    kronfit_jobs = []

    # kronfit the original graph
    full_input_file = directory + 'edgelist'
    full_output_file = directory + 'output.dat'
    kronfit_jobs.append((full_input_file, full_output_file))
    
    output = open(directory + 'kron_points.txt', 'w')
    output.write('a,b,d,sampling_proportion\n')
    
    # get sample graphs and Kronecker points of the samples
    for p in range(step, 100, step):
        print('Sampling ' + str(p) + '% subgraphs')
        processes = []
        os.mkdir(directory + str(p) + '/')
        for i in range(0, nos):
            sample(directory, p, i)
            input_file = directory + str(p) + '/' + str(i) + '.edgelist'
            output_file = directory + str(p) + '/' + str(i) + '_output.dat'
            kronfit_jobs.append((input_file, output_file))


    print("Running Kronfit for each graph")

    Parallel(n_jobs=int((len(os.sched_getaffinity(0))/2)))(
        delayed(kronfit)(kronfit_job)
        for kronfit_job in tqdm(kronfit_jobs))

    print("Kronfit Finished")

    kronecker_points = []
    for p in range(step, 100, step):
        # extract points from the output file of kronfit
        for i in range(0, nos):
            output_file = directory + str(p) + '/' + str(i) + '_output.dat'
            with open(output_file, 'r') as myfile:
                s = myfile.read()
                ret = re.findall(r'\[([^]]*)\]', s)
                split = ret[0].split(',')
                a = split[0]
                b = split[1].split(';')[0].strip()
                d = split[2].strip()
                output.write(str(a) + ',' + str(b) + ',' + str(d) + ',' + str(p) + '\n')
                kronecker_points.append([float(a), float(b), float(d)])
            
    # write all the Kronecker points to a file
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
    
    # create convex hull
    kronecker_points = np.asarray(kronecker_points, dtype=np.float32)
    create_kronecker_hull(directory, kronecker_points)


