# KroneckerHull

 Represent a network as a 3D shape

 Mandatory arguments are mandatory for short options.

  -n, network name

  -f, input edge list file name.

  -s, sampling proportion step (percentage)

  -t, number of samples for each sampling proportion 

 example: python kron_hull.py -n as20graph -f as20graph.txt -s 20 -t 5

 output: 
         
         the directory <network name>/

         Kronecker hull <network name>/kronecker_hull.jpg

         boundary points <network name>/boundary.txt

         Kronecker points <network name>/kron_points.txt

         edgelist files of samples 

 environment & prerequisite:

 linux

 python 2.7, networkx, numpy, scipy

 kronfit: please refer to https://github.com/shengminjin/snap/tree/master/examples/kronfit

# Citation

       To cite this work please use:

       @inproceedings{jin2018representing,
       
         title={Representing Networks with 3D Shapes},
         
         author={Jin, Shengmin and Zafarani, Reza},
         
         booktitle={2018 IEEE International Conference on Data Mining (ICDM)},
         
         pages={177--186},
         
         year={2018},
         
         organization={IEEE}
         
       }
