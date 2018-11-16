 Represent a network as a 3D shape 
 Mandatory arguments are mandatory for short options.
  -n, network name 
  -f, edge list file name. 
  -s, sampling size step (percent)
  -t, number of samples for each sampling size

 example: python kron_hull.py -n roadtx -f roadtx.txt -s 20 -t 5
 
 output: the directory <network name>/
         Kronecker hull <network name>/kronecker_hull.jpg
         boundary points <network name>/boundary.txt
         Kronecker points <network name>/kron_points.txt
	 edgelist files of samples (can be deleted later, now for debug)
