from numpy import *
import numpy as np
from numpy import math

import os
from .PDB_loader import *

'''
Contents
--------
    I. cndo_to_dnainfo
    II. writePDBresidue
        1. Single-model PDB with alphanumeric chains
        2. Multi-model PDB file with chains = 'A'
        3. Single-model PDB with chains = 'A' and iterative segid
    III. Matrix transformation functions
    IV. Large number encoding functions
        1. base36encode
        2. hybrid36encode
    V. pdbgen Function
-------
    
'''

# I. cndo_to_dnainfo
# This function converts a .cndo data structure to a useable input
# for the main pdbgen function

def cndo_to_dnainfo(filename, inputdir):

    f = open(inputdir + '/' + filename + '.cndo', 'r')

    # Initialize variables to list
    dnaTop = []
    dNode = []
    triad = []
    id_nt = []

    # Read in the data structure
    for line in f:

        if 'dnaTop' in line:

            line = next(f)
            while line.strip() != '':
                linestr = line.strip()
                dnaTop.append(linestr.split(','))
                line = next(f)

        elif 'dNode' in line:

            line = next(f)
            while line.strip() != '':
                linestr = line.strip()
                dNode.append(linestr.split(','))
                line = next(f)

        elif 'triad' in line:

            line = next(f)
            while line.strip() != '':
                linestr = line.strip()
                triad.append(linestr.split(','))
                line = next(f)

        elif 'id_nt' in line:

            line = next(f)
            while line.strip() != '':
                linestr = line.strip()
                id_nt.append(linestr.split(','))
                # End of file requires this try-except break
                try:
                    line = next(f)
                except:
                    break

        else:
            pass

    return dnaTop, dNode, triad, id_nt

# 1.1. dnaInfo.dnaTop contains the sequential topology
# {dnaTop, id, up, down, across, seq}

# 1.2. dnaInfo.dnaGeom.dNode contains the centroid of each node (bp)
# {dNode, e0(1), e0(2), e0(3)}

# 1.3. dnaInfo.dnaGeom.triad contains the coordinate system of each node (bp)
# {triad, e1(1), e1(2), e1(3), e2(1), e2(2), e2(3), e3(1), e3(2), e3(3)}

# 1.4. dnaInfo.dnaGeom.id_nt contains the basepairing info
# {id_nt, id1, id2}

# The object dnaInfo.dnaTop is ordered by chain, starting with the scaffold
# strand. From this we can sequentially build our PDB file, after a routing
# procedure.

# Function for writing a PDB file atom-by-atom
# Requires current chain, resnum, restype

# II. writePDBresidue

def writePDBresidue(filename, chain, chainnum, resnum, atomnum, mmatomnum, restype, refatoms, basecrds, pN, fpdb, fmm, fseg):

    segatomnum = atomnum

    # This function will append coordinates to a PDB file residue by residue
    # 1. Single-model PDB with alphanumeric chains

#    pdbOut=filename+'.pdb'
#    fOut=str(os.path.join(pN, pdbOut))
#    f = open(fOut, 'a')

    # Check that file lengths are consistent
    if len(refatoms) != len(basecrds[:,0]):
        print('...Error: Base coord data is inconsistent. Aborting...\n')
    else:
        pass

    element = ' '
    # Please see official PDB file format documentation for more information
    # www.wwpdb.org/documentation/file-format
    #
    for i in range(len(refatoms)):
        # Data type: Record Name: Cols 1 - 6
        fpdb.write('{0:<6s}'.format('ATOM'))
        # Data type: Atom serial number: Cols 7 - 11
        if atomnum < 100000:
            fpdb.write('{0:>5d}'.format(int(atomnum)))
        else:
            hybatomnum = hybrid36encode(atomnum,5)
            fpdb.write('{0:>5s}'.format(str(hybatomnum)))
            #f.write('*****')
        fpdb.write(' ') # <-- One blank space
        # Data type: Atom name: Cols 13 - 16
        # This one is complicated and depends on size of string
        if len(str(refatoms[i])) == 1:
            fpdb.write(' ' + '{0:>1s}'.format(str(refatoms[i])) + '  ')
            element = str(refatoms[i])
        elif len(str(refatoms[i])) == 2:
            fpdb.write(' ' + '{0:>2s}'.format(str(refatoms[i])) + ' ')
            element = str(refatoms[i])[0]
        elif len(str(refatoms[i])) == 3:
            fpdb.write(' ' + '{0:>3s}'.format(str(refatoms[i])))
            element = str(refatoms[i])[0]
        elif len(str(refatoms[i])) == 4:
            fpdb.write('{0:>4s}'.format(str(refatoms[i])))
            element = str(refatoms[i])[1]
        # Data type: Alternate location indicator: Col 17 <-- This is typically empty
        fpdb.write(' ')
        # Data type: Residue name: Cols 18 - 20
        fpdb.write('{0:>3s}'.format(str(restype)))
        # Data type: Chain identifier: Col 22 <-- Insert extra column 21
        fpdb.write('{0:>2s}'.format(str(chain)))
        # Data type: Residue sequence number: Cols 23 - 26
        if resnum < 10000:
            fpdb.write('{0:>4d}'.format(int(resnum)))
        else:
            hybresnum = hybrid36encode(resnum, 4)
            fpdb.write('{0:>4s}'.format(str(hybresnum)))
            #f.write('****')
        fpdb.write('    ') # <-- Four blank spaces
        # Data type: X coordinates: Cols 31 - 38 (8.3)
        fpdb.write('{0:>8.3f}'.format(float(basecrds[i,0])))
        # Data type: Y coordinates: Cols 39 - 46 (8.3)
        fpdb.write('{0:>8.3f}'.format(float(basecrds[i,1])))
        # Data type: Z coordinates: Cols 47 - 54 (8.3)
        fpdb.write('{0:>8.3f}'.format(float(basecrds[i,2])))
        # Data type: Occupancy: Cols 55 - 60 (6.2)
        fpdb.write('{0:>6.2f}'.format(float(1.0)))
        # Data type: Temperature factor: Cols 61 - 66 (6.2)
        fpdb.write('{0:>6.2f}'.format(float(0.0)))
        fpdb.write('          ') # <-- Ten blank spaces
        # Data type: Element symbol: Cols 77 - 78
        fpdb.write('{0:>2s}'.format(str(element)))
        # Data type: Charge: Cols 79 - 80 <-- Currently leaving this blank
        fpdb.write('  \n') # <-- Move to next line

        # Iterate atom number
        atomnum += 1

    
    # 2. Multi-model PDB with chains = 'A'
#    pdbOut=filename+'-multimodel.pdb'
#    fOut=str(os.path.join(pN, pdbOut))
#    fmm = open(fOut, 'a')

    element = ' '
    # Please see official PDB file format documentation for more information
    # www.wwpdb.org/documentation/file-format
    #
    for i in range(len(refatoms)):
        # Data type: Record Name: Cols 1 - 6
        fmm.write('{0:<6s}'.format('ATOM'))
        # Data type: Atom serial number: Cols 7 - 11
        if mmatomnum < 100000:
            fmm.write('{0:>5d}'.format(int(mmatomnum)))
        else:
            mmhybatomnum = hybrid36encode(mmatomnum, 5)
            fmm.write('{0:>5s}'.format(str(mmhybatomnum)))
            #f.write('*****')
        fmm.write(' ') # <-- One blank space
        # Data type: Atom name: Cols 13 - 16
        # This one is complicated and depends on size of string
        if len(str(refatoms[i])) == 1:
            fmm.write(' ' + '{0:>1s}'.format(str(refatoms[i])) + '  ')
            element = str(refatoms[i])
        elif len(str(refatoms[i])) == 2:
            fmm.write(' ' + '{0:>2s}'.format(str(refatoms[i])) + ' ')
            element = str(refatoms[i])[0]
        elif len(str(refatoms[i])) == 3:
            fmm.write(' ' + '{0:>3s}'.format(str(refatoms[i])))
            element = str(refatoms[i])[0]
        elif len(str(refatoms[i])) == 4:
            fmm.write('{0:>4s}'.format(str(refatoms[i])))
            element = str(refatoms[i])[1]
        # Data type: Alternate location indicator: Col 17 <-- This is typically empty
        fmm.write(' ')
        # Data type: Residue name: Cols 18 - 20
        fmm.write('{0:>3s}'.format(str(restype)))
        # Data type: Chain identifier: Col 22 <-- Insert extra column 21
        # For multi-model PDB, this is always 'A'
        fmm.write('{0:>2s}'.format(str('A')))
        # Data type: Residue sequence number: Cols 23 - 26
        if resnum < 10000:
            fmm.write('{0:>4d}'.format(int(resnum)))
        else:
            hybresnum = hybrid36encode(resnum,4)
            fmm.write('{0:>4s}'.format(str(hybresnum)))
            #fmm.write('****')
        fmm.write('    ') # <-- Four blank spaces
        # Data type: X coordinates: Cols 31 - 38 (8.3)
        fmm.write('{0:>8.3f}'.format(float(basecrds[i,0])))
        # Data type: Y coordinates: Cols 39 - 46 (8.3)
        fmm.write('{0:>8.3f}'.format(float(basecrds[i,1])))
        # Data type: Z coordinates: Cols 47 - 54 (8.3)
        fmm.write('{0:>8.3f}'.format(float(basecrds[i,2])))
        # Data type: Occupancy: Cols 55 - 60 (6.2)
        fmm.write('{0:>6.2f}'.format(float(1.0)))
        # Data type: Temperature factor: Cols 61 - 66 (6.2)
        fmm.write('{0:>6.2f}'.format(float(0.0)))
        fmm.write('          ') # <-- Ten blank spaces
        # Data type: Element symbol: Cols 77 - 78
        fmm.write('{0:>2s}'.format(str(element)))
        # Data type: Charge: Cols 79 - 80 <-- Currently leaving this blank
        fmm.write('  \n') # <-- Move to next line

        # Iterate atom number
        mmatomnum += 1


    # 3. Single-model PDB with chains = 'A' and iterative segid
#    pdbOut=filename+'-chseg.pdb'
#    fOut=str(os.path.join(pN, pdbOut))
#    fseg = open(fOut, 'a')

    element = ' '
    # Please see official PDB file format documentation for more information
    # www.wwpdb.org/documentation/file-format
    #
    for i in range(len(refatoms)):
        # Data type: Record Name: Cols 1 - 6
        fseg.write('{0:<6s}'.format('ATOM'))
        # Data type: Atom serial number: Cols 7 - 11
        if segatomnum < 100000:
            fseg.write('{0:>5d}'.format(int(segatomnum)))
        else:
            hybatomnum = hybrid36encode(segatomnum, 5)
            fseg.write('{0:>5s}'.format(str(hybatomnum)))
            #f.write('*****')
        fseg.write(' ') # <-- One blank space
        # Data type: Atom name: Cols 13 - 16
        # This one is complicated and depends on size of string
        if len(str(refatoms[i])) == 1:
            fseg.write(' ' + '{0:>1s}'.format(str(refatoms[i])) + '  ')
            element = str(refatoms[i])
        elif len(str(refatoms[i])) == 2:
            fseg.write(' ' + '{0:>2s}'.format(str(refatoms[i])) + ' ')
            element = str(refatoms[i])[0]
        elif len(str(refatoms[i])) == 3:
            fseg.write(' ' + '{0:>3s}'.format(str(refatoms[i])))
            element = str(refatoms[i])[0]
        elif len(str(refatoms[i])) == 4:
            fseg.write('{0:>4s}'.format(str(refatoms[i])))
            element = str(refatoms[i])[1]
        # Data type: Alternate location indicator: Col 17 <-- This is typically empty
        fseg.write(' ')
        # Data type: Residue name: Cols 18 - 20
        fseg.write('{0:>3s}'.format(str(restype)))
        # Data type: Chain identifier: Col 22 <-- Insert extra column 21
        # Use chain 'A' here
        fseg.write('{0:>2s}'.format(str('A')))
        # Data type: Residue sequence number: Cols 23 - 26
        if resnum < 10000:
            fseg.write('{0:>4d}'.format(int(resnum)))
        else:
            hybresnum = hybrid36encode(resnum, 4)
            fseg.write('{0:>4s}'.format(str(hybresnum)))
            #fseg.write('****')
        fseg.write('    ') # <-- Four blank spaces
        # Data type: X coordinates: Cols 31 - 38 (8.3)
        fseg.write('{0:>8.3f}'.format(float(basecrds[i,0])))
        # Data type: Y coordinates: Cols 39 - 46 (8.3)
        fseg.write('{0:>8.3f}'.format(float(basecrds[i,1])))
        # Data type: Z coordinates: Cols 47 - 54 (8.3)
        fseg.write('{0:>8.3f}'.format(float(basecrds[i,2])))
        # Data type: Occupancy: Cols 55 - 60 (6.2)
        fseg.write('{0:>6.2f}'.format(float(1.0)))
        # Data type: Temperature factor: Cols 61 - 66 (6.2)
        fseg.write('{0:>6.2f}'.format(float(0.0)))
        fseg.write('      ') # <-- Six blank spaces
        # Write SEGID here <-- This is a NAMD hack
        fseg.write('{0:>4d}'.format(chainnum+1))
        # Data type: Element symbol: Cols 77 - 78
        fseg.write('{0:>2s}'.format(str(element)))
        # Data type: Charge: Cols 79 - 80 <-- Currently leaving this blank
        fseg.write('  \n') # <-- Move to next line

        # Iterate atom number
        segatomnum += 1


    # 4. mmCIF atomic format for large structures
    #f = open('./' + filename + '.cif', 'a')

    #print 'Segment ' + str(chainnum + 1) + ', Residue ' + str(resnum) + ' printing coordinates...'

    element = ' '
    # Please see official PDB file format documentation for more information
    # www.wwpdb.org/documentation/file-format
    #
    #for i in range(len(refatoms)):

    return atomnum, mmatomnum

# III. Matrix transformation functions

# Procedure same as in ProDy
def getTransMat(mob, tar):

    mob_com = mob.mean(0)
    tar_com = tar.mean(0)
    #print mob_com
    #print tar_com
    mob = mob - mob_com
    tar = tar - tar_com
    matrix = np.dot(mob.T, tar)

    U, s, Vh = linalg.svd(matrix)
    Id = np.array([[1, 0, 0],
                   [0, 1, 0],
                   [0, 0, np.sign(linalg.det(matrix))]])
    rotation = np.dot(Vh.T, np.dot(Id, U.T))

    transmat = np.eye(4)
    transmat[:3,:3] = rotation
    transmat[:3, 3] = tar_com - mob_com

    return transmat

# Procedure same as in ProDy
def applyTransMat(transmat, coords):

    return np.dot(coords, transmat[:3,:3].T) + transmat[:3, 3]

# Translate coords
def translate(mob,trans):

    npts = mob.shape[0]

    for i in range(npts):

        mob[i,:] = mob[i,:] + trans

    return mob

# Convert Euler rotation to Axis-Angle
def eultoaxisangle(mat):

    [[m00, m10, m20],\
     [m01, m11, m21],\
     [m02, m12, m22]] = mat

    angle = math.degrees(math.acos((m00 + m11 + m22 - 1)/2))

    xtemp = (m21 - m12) / math.sqrt(pow(m21 - m12,2) + pow(m02 - m20,2) + pow(m10 - m01,2))
    ytemp = (m02 - m20) / math.sqrt(pow(m21 - m12,2) + pow(m02 - m20,2) + pow(m10 - m01,2))
    ztemp = (m10 - m01) / math.sqrt(pow(m21 - m12,2) + pow(m02 - m20,2) + pow(m10 - m01,2))

    axis = np.array([xtemp, ytemp, ztemp])

    return angle, axis

# Convert Axis-Angle to Euler rotation
def axisangletoeul(angle, axis):

    c = math.cos(math.radians(angle))
    s = math.sin(math.radians(angle))
    t = 1.0 - c
    x, y, z = axis

    mat = [[t*x*x + c, t*x*y - z*s, t*x*z + y*s],\
           [t*x*y + z*s, t*y*y + c, t*y*z - x*s],\
           [t*x*z - y*s, t*y*z + x*s, t*z*z + c]]

    return mat

# IV. Functions for encoding large numbers

# 1. Function to encode a decimal using base36 notation
def base36encode(number):

    # 36-character alphabet for base-36 notation
    alphab36 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', \
                'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', \
                'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    base36 = ''

    while number:
        number, i  = divmod(number, 36)
        base36 = alphab36[i] + base36

    return base36

# 2. Function to encode a decimal using hybrid36 notation
def hybrid36encode(number,digits):

    # 52-character alphabet for first digit of hybrid36 notation
    alphahyb36 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', \
                  'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', \
                  'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', \
                  'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', \
                  'w', 'x', 'y', 'z']

    div, rem = divmod(number, 36 ** (digits - 1))
    b36rem = base36encode(rem)
    hybrem = alphahyb36[div]
    # Need to check length of b36rem string
    hyb36str = str(hybrem) + str(b36rem)

    return hyb36str

# V. PDBGen Function Definition
def pdbgen(filename, hF, pN):

    # Open PDBGen logging file
    dnaTop, dNode, triad, id_nt = cndo_to_dnainfo(filename, pN)
    # Specify A- or B-type Helix
    if hF==True:
        abtype='A'
        natype=['RNA','DNA'] # [scaffold type, staple type]
        # note: defaulting to RNA scaffold and DNA staples when A-form helix is specified
    elif hF==False:
        abtype='B'
        natype=['DNA','DNA'] # [scaffold type, staple type]

    # Initialize PDB Generation Values
    atomnum = 1
    mmatomnum = 1
    resnum = 1
    chainnum = 0
    chlist = 'A'
    cc = 0
    bdna = c_bdna()
    adna = c_adna()
    arna = c_arna()

    # Chain list consists of 63 alphanumeric characters used sequentially to number
    # PDB chains.
    chainlist = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', \
             'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', \
             'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', \
             'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', \
             '4', '5', '6', '7', '8', '9']

    # First need to re-order the dnaInfo.dnaTop structure as it is not in the order
    # needed to build a pdb file. Loop through data structure and save to routeTemp.
    # The dnaInfo.dnaTop structure is ordered so that the scaffold strand is first.
    # Next, the staple strands are not always contiguous, so they need to be reordered.

    # First convert to list for easier processing
    unrouteTemp = np.asarray(dnaTop)
    numbases = len(unrouteTemp[:,0])
    routeTemp = np.zeros((numbases,5),dtype=object)
    visited = np.zeros(numbases,dtype=int)
    routeindex = 0

    # Loop through all of the bases
    for ii in range(numbases):

        # Base-pairing info for base
        base = unrouteTemp[ii,1:]
        baseid = int(unrouteTemp[ii,1])
        baseup = int(unrouteTemp[ii,2])
        basedown = int(unrouteTemp[ii,3])
        baseacross = int(unrouteTemp[ii,4])
        baseseq = str(unrouteTemp[ii,5])

        # Check if base is a terminal 5' end and not visited yet
        if baseup == -1 and visited[ii] == 0:
            # Append base to route
            routeTemp[routeindex,:] = base
            routeindex += 1
            visited[ii] = 1
            # Set initial length of strand
            strlen = 1
            while basedown != -1:
                nextbaseid = basedown
                # Check if next base is correct one
                # Fails if ii == numbases - 1
                if ii + strlen < numbases - 1:
                    tempnextbaseid = int(unrouteTemp[ii+strlen,1])
                    if nextbaseid == tempnextbaseid:
                        # Base-pairing info for base
                        base = unrouteTemp[ii+strlen,1:]
                        baseid = int(unrouteTemp[ii+strlen,1])
                        baseup = int(unrouteTemp[ii+strlen,2])
                        basedown = int(unrouteTemp[ii+strlen,3])
                        baseacross = int(unrouteTemp[ii+strlen,4])
                        baseseq = str(unrouteTemp[ii+strlen,5])
                    else:
                        # First try unrouteTemp[basedown-1]
                        tempnextbaseid = int(unrouteTemp[basedown-1,1])
                        if nextbaseid == tempnextbaseid:
                            base = unrouteTemp[basedown-1,1:]
                            baseid = int(unrouteTemp[basedown-1,1])
                            baseup = int(unrouteTemp[basedown-1,2])
                            basedown = int(unrouteTemp[basedown-1,3])
                            baseacross = int(unrouteTemp[basedown-1,4])
                            baseseq = str(unrouteTemp[basedown-1,5])
                        else:
                            # If all else fails!
                            # Loop through to find next base in sequence
                            for jj in range(numbases):
                                # Base-pairing info for base
                                base = unrouteTemp[jj,1:]
                                baseid = int(unrouteTemp[jj,1])
                                baseup = int(unrouteTemp[jj,2])
                                basedown = int(unrouteTemp[jj,3])
                                baseacross = int(unrouteTemp[jj,4])
                                baseseq = str(unrouteTemp[jj,5])
                                if baseid == nextbaseid:
                                    break
                                else:
                                    continue
                else:
                    # Loop through to find next base in sequence
                    for jj in range(numbases):
                        # Base-pairing info for base
                        base = unrouteTemp[jj,1:]
                        baseid = int(unrouteTemp[jj,1])
                        baseup = int(unrouteTemp[jj,2])
                        basedown = int(unrouteTemp[jj,3])
                        baseacross = int(unrouteTemp[jj,4])
                        baseseq = str(unrouteTemp[jj,5])
                        if baseid == nextbaseid:
                            break
                        else:
                            continue
                routeTemp[routeindex,:] = base
                routeindex += 1
                strlen += 1
            else:
                # Base is a terminal 3' end
                # Continue the loop
                if basedown == -1:
                    continue
                else:
                    print('...Error in routing info...\n');
                    break
            #while basedown != -1:
            #    nextbaseid = basedown
            #    # Find next base in sequence
            #    for jj in range(numbases):
            #        # Base-pairing info for base
            #        base = unrouteTemp[jj,1:]
            #        baseid = int(unrouteTemp[jj,1])
            #        baseup = int(unrouteTemp[jj,2])
            #        basedown = int(unrouteTemp[jj,3])
            #        baseacross = int(unrouteTemp[jj,4])
            #        baseseq = str(unrouteTemp[jj,5])
            #        if baseid == nextbaseid:
            #            break
            #        else:
            #            continue
            #    routeTemp[routeindex,:] = base
            #    routeindex += 1
            #else:
            #    # Base is a terminal 3' end
            #    # Continue the loop
            #    if basedown == -1:
            #        continue
            #    else:
            #        print('...Error in routing info...\n')
            #        break
            #
    
    # Open PDB files for appending
    fpdb_name = filename + '.pdb'
    fpdbOut = str(os.path.join(pN, fpdb_name))
    fpdb = open(fpdbOut, 'a')
    
    fmm_name = filename + '-multimodel.pdb'
    fmmOut = str(os.path.join(pN,fmm_name))
    fmm = open(fmmOut, 'a')
    
    fseg_name = filename + '-segid.pdb'
    fsegOut = str(os.path.join(pN, fseg_name))
    fseg = open(fsegOut, 'a')
    
    ssfirst = 0 # ID of first nucleotide in ss region
    sslast = 0 # ID of last nucleotide in ss region
    sslength = 0 # Length of ss region
    ssbases = []

    # Go through each base in routed structure
    # Create array for dNode, triad
    dNode = np.asarray(dNode)
    triad = np.asarray(triad)

    for ii in range(numbases):

        # Get base-pairing info
        base = routeTemp[ii,:]
        baseid = int(routeTemp[ii,0])
        baseup = int(routeTemp[ii,1])
        basedown = int(routeTemp[ii,2])
        baseacross = int(routeTemp[ii,3])
        baseseq = str(routeTemp[ii,4])
        # print ii, baseid, baseup, basedown, baseacross, baseseq

        # Tag for type of base strand
        type = 0 # scaf = 1, stap = 2, ssdna = 3

        # Check if the base is 5'-end
        if baseup == -1:
            # Multi-model PDB starts new model here
            fmm.write('MODEL' + '{0:>9s}'.format(str(chainnum + 1)) + '\n')

        #print sslength, sslast, baseid

        # Check if in an ssDNA region
        if sslength > 0:
            if baseid != sslast:
                continue
            elif baseid == sslast:
                ssfirst = 0
                sslast = 0
                sslength = 0
                ssbases = []
                continue
        else:
            pass

        # First Check if base is unpaired
        if baseacross == -1:
            type = 3
            pass
        else:
            # Otherwise, Extract basepairid
            for j, bp in enumerate(id_nt):
                # Scaffold strand
                if baseid == int(bp[1]):
                    bpid = int(j)
                    type = 1
                    break
                # Staple strand
                elif baseid == int(bp[2]):
                    bpid = int(j)
                    type = 2
                    break

        #print type

        # Only basepaired sequences have coordinates
        if type == 1 or type == 2:
            # Extract Centroid of Base
            xx0, yy0, zz0 = float(dNode[bpid,1]), float(dNode[bpid,2]), float(dNode[bpid,3])
            #print xx0, yy0, zz0

            # Extract Coordinate System of Base
            xx1, xx2, xx3 = float(triad[bpid,1]), float(triad[bpid,2]), float(triad[bpid,3]) # X-axis
            yy1, yy2, yy3 = float(triad[bpid,4]), float(triad[bpid,5]), float(triad[bpid,6]) # Y-axis
            zz1, zz2, zz3 = float(triad[bpid,7]), float(triad[bpid,8]), float(triad[bpid,9]) # Z-axis

            #print xx1, xx2, xx3
            #print yy1, yy2, yy3
            #print zz1, zz2, zz3

            # Get transformation matrix for origin to base coordinate system
            # Start by using available ProDy functions
            # Should re-write later!!

            xyzorigin = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])

            xyzbase = np.array([[xx0, yy0, zz0],
                                [xx0 + xx1, yy0 + xx2, zz0 + xx3],
                                [xx0 + yy1, yy0 + yy2, zz0 + yy3],
                                [xx0 + zz1, yy0 + zz2, zz0 + zz3]])

            #print xyzorigin, xyzbase

            transformMat = getTransMat(xyzorigin, xyzbase)

        # For unpaired sequences, need to calculate the reference frame
        elif type == 3:

            # Whole ss region will be calculated within this statement
            ssfirst = baseid
            upbase = baseup
            sslast = baseid
            ssbases.append(base)
            sslength = 1
            # Now find last unpaired nucleotide
            while baseacross == -1:
                ii += 1
                # Get base-pairing info
                base = routeTemp[ii,:]
                baseid = int(routeTemp[ii,0])
                baseup = int(routeTemp[ii,1])
                basedown = int(routeTemp[ii,2])
                baseacross = int(routeTemp[ii,3])
                baseseq = str(routeTemp[ii,4])
                if baseacross == -1:
                    sslast = baseid
                    ssbases.append(base)
                    downbase = basedown
                    sslength += 1
                    continue
                else:
                    break

            # Print ssDNA characteristics

            # Extract coordinates of upstream base
            for j, bp in enumerate(id_nt):
                # Scaffold strand
                if upbase == int(bp[1]):
                    bpidup = int(j)
                    typeup = 1
                    break
                # Staple strand
                elif upbase == int(bp[2]):
                    bpidup = int(j)
                    typeup = 2
                    break

            # Extract Centroid of Upstream Base
            xx0up, yy0up, zz0up = float(dNode[bpidup,1]), float(dNode[bpidup,2]), float(dNode[bpidup,3])

            #print xx0up, yy0up, zz0up

            # Extract Coordinate System of Upstream Base
            xx1up, xx2up, xx3up = float(triad[bpidup,1]), float(triad[bpidup,2]), float(triad[bpidup,3]) # X-axis
            yy1up, yy2up, yy3up = float(triad[bpidup,4]), float(triad[bpidup,5]), float(triad[bpidup,6]) # Y-axis
            zz1up, zz2up, zz3up = float(triad[bpidup,7]), float(triad[bpidup,8]), float(triad[bpidup,9]) # Z-axis

            xyzbase0 = np.array([[xx0up, yy0up, zz0up],
                                 [xx0up + xx1up, yy0up + xx2up, zz0up + xx3up],
                                 [xx0up + yy1up, yy0up + yy2up, zz0up + yy3up],
                                 [xx0up + zz1up, yy0up + zz2up, zz0up + zz3up]])

            # Extract coordinates of downstream base
            for j, bp in enumerate(id_nt):
                # Scaffold strand
                if downbase == int(bp[1]):
                    bpiddo = int(j)
                    typedo = 1
                    break
                # Staple strand
                elif downbase == int(bp[2]):
                    bpiddo = int(j)
                    typedo = 2
                    break

            # Extract Centroid of Downstream Base
            xx0do, yy0do, zz0do = float(dNode[bpiddo,1]), float(dNode[bpiddo,2]), float(dNode[bpiddo,3])

            # Extract Coordinate System of Downstream Base
            xx1do, xx2do, xx3do = float(triad[bpiddo,1]), float(triad[bpiddo,2]), float(triad[bpiddo,3]) # X-axis
            yy1do, yy2do, yy3do = float(triad[bpiddo,4]), float(triad[bpiddo,5]), float(triad[bpiddo,6]) # Y-axis
            zz1do, zz2do, zz3do = float(triad[bpiddo,7]), float(triad[bpiddo,8]), float(triad[bpiddo,9]) # Z-axis

            xyzbase3 = np.array([[xx0do, yy0do, zz0do],
                                 [xx0do + xx1do, yy0do + xx2do, zz0do + xx3do],
                                 [xx0do + yy1do, yy0do + yy2do, zz0do + yy3do],
                                 [xx0do + zz1do, yy0do + zz2do, zz0do + zz3do]])

            # Compute distance between upstream and downstream bases
            dist12 = sqrt(pow(float(xx0do)-float(xx0up), 2) + \
                      pow(float(yy0do)-float(yy0up), 2) + \
                      pow(float(zz0do)-float(zz0up), 2))

            # Debugging - ssDNA region distance
            #print 'ssDNA Region Dist = ', str(dist12)

            # Check that up- and downstream bases are same type
            if typeup == typedo:
                pass
            elif typeup != typedo:
                print('...Error: up- and down-stream bases in ssDNA region are differing types...\n');
                break

            # Need two additional points for ss bulge region
            # Check: make this work for additional types of ss regions
            #
            # Diagram shows a typical 'staple' ss bulge region
            #
            #       d1 ------ d2
            #       |         |
            #       |         ^
            #       |         |
            #   <--(d0)       (d3)-->
            #       |
            #       v
            #
            # Point 0 is upstream base centroid
            d0 = np.array([xx0up, yy0up, zz0up])
            # Point 3 is downstream base centroid
            d3 = np.array([xx0do, yy0do, zz0do])

            # Distance to extend d0 - d1 and d3 - d2 axes
            # To test later - Used a 5 Ang distance for points d1 and d2. Is this dependent on ssDNA length?
            dext = 5 # Angstroms

            # Point 1 is along Upstream Z-axis
            # Scaffold
            if typeup == 1:
                d1 = np.array([dext*zz1up, dext*zz2up, dext*zz3up])
            # Staple
            elif typeup == 2:
                d1 = np.array([-dext*zz1up, -dext*zz2up, -dext*zz3up])
            else:
                print('...Error: Upstream base does not have a base type...\n');
                break
            # Point 2 is along Downstream Z-axis
            # Scaffold
            if typeup == 1:
                d2 = np.array([(xx0do - dext*zz1do) - xx0up, (yy0do - dext*zz2do) - yy0up, (zz0do - dext*zz3do) - zz0up])
            # Staple
            elif typeup == 2:
                d2 = np.array([(xx0do + dext*zz1do) - xx0up, (yy0do + dext*zz2do) - yy0up, (zz0do + dext*zz3do) - zz0up])
            else:
                print('...Error: Upstream base does not have a base type...\n');
                break

            # Move upstream and downstream bases to {0,0,0}
            xyzbase30 = np.array([[0, 0, 0],
                                  [xx1do, xx2do, xx3do],
                                  [yy1do, yy2do, yy3do],
                                  [zz1do, zz2do, zz3do]])

            xyzbase00 = np.array([[0, 0, 0],
                                  [xx1up, xx2up, xx3up],
                                  [yy1up, yy2up, yy3up],
                                  [zz1up, zz2up, zz3up]])

            # Total rotation matrix between base0 and base3 at origin
            Rtot = getTransMat(xyzbase30, xyzbase00)

            # Extract rotation matrix from transformation matrix
            #Rrotate = Rtot.getRotation()
            Rrotate = Rtot[:3,:3]
            #print Rrotate

            # Convert to axis-angle representation
            angle, axis = eultoaxisangle(Rrotate)
            #print angle, axis

            # Loop through ssDNA bases
            for jj in range(sslength):

                # Get ss base information
                base = ssbases[jj]
                baseid = int(base[0])
                baseup = int(base[1])
                basedown = int(base[2])
                baseacross = int(base[3])
                baseseq = str(base[4])

                # Now pull reference base information
                refcrds = []
                refatoms = []
                restype = ''
                if typeup == 1 and abtype == 'B' and natype[typeup-1] == 'DNA': # Scaffold strand
                    if baseseq == 'A':
                        refcrds = bdna.Ascaf[:,3:6]
                        refatoms = bdna.Ascaf[:,0]
                        restype = 'ADE'
                    elif baseseq == 'C':
                        refcrds = bdna.Cscaf[:,3:6]
                        refatoms = bdna.Cscaf[:,0]
                        restype = 'CYT'
                    elif baseseq == 'G':
                        refcrds = bdna.Gscaf[:,3:6]
                        refatoms = bdna.Gscaf[:,0]
                        restype = 'GUA'
                    elif baseseq == 'T':
                        refcrds = bdna.Tscaf[:,3:6]
                        refatoms = bdna.Tscaf[:,0]
                        restype = 'THY'
                    else:
                        print('...Error: No base sequence for scaffold strand...\n');
                elif typeup == 2 and abtype == 'B' and natype[typeup-1] == 'DNA': # Staple strand
                    if baseseq == 'A':
                        refcrds = bdna.Astap[:,3:6]
                        refatoms = bdna.Astap[:,0]
                        restype = 'ADE'
                    elif baseseq == 'C':
                        refcrds = bdna.Cstap[:,3:6]
                        refatoms = bdna.Cstap[:,0]
                        restype = 'CYT'
                    elif baseseq == 'G':
                        refcrds = bdna.Gstap[:,3:6]
                        refatoms = bdna.Gstap[:,0]
                        restype = 'GUA'
                    elif baseseq == 'T':
                        refcrds = bdna.Tstap[:,3:6]
                        refatoms = bdna.Tstap[:,0]
                        restype = 'THY'
                    else:
                        print('...Error: No base sequence for staple strand...\n');
                elif typeup == 1 and abtype == 'A' and natype[typeup-1] == 'DNA': # Scaffold strand
                    if baseseq == 'A':
                        refcrds = adna.Ascaf[:,3:6]
                        refatoms = adna.Ascaf[:,0]
                        restype = 'ADE'
                    elif baseseq == 'C':
                        refcrds = adna.Cscaf[:,3:6]
                        refatoms = adna.Cscaf[:,0]
                        restype = 'CYT'
                    elif baseseq == 'G':
                        refcrds = adna.Gscaf[:,3:6]
                        refatoms = adna.Gscaf[:,0]
                        restype = 'GUA'
                    elif baseseq == 'T':
                        refcrds = adna.Tscaf[:,3:6]
                        refatoms = adna.Tscaf[:,0]
                        restype = 'THY'
                    else:
                        print('...Error: No base sequence for scaffold strand...\n');
                elif typeup == 2 and abtype == 'A' and natype[typeup-1] == 'DNA': # Staple strand
                    if baseseq == 'A':
                        refcrds = adna.Astap[:,3:6]
                        refatoms = adna.Astap[:,0]
                        restype = 'ADE'
                    elif baseseq == 'C':
                        refcrds = adna.Cstap[:,3:6]
                        refatoms = adna.Cstap[:,0]
                        restype = 'CYT'
                    elif baseseq == 'G':
                        refcrds = adna.Gstap[:,3:6]
                        refatoms = adna.Gstap[:,0]
                        restype = 'GUA'
                    elif baseseq == 'T':
                        refcrds = adna.Tstap[:,3:6]
                        refatoms = adna.Tstap[:,0]
                        restype = 'THY'
                    else:
                        print('...Error: No base sequence for staple strand...\n')
                elif typeup == 1 and abtype == 'A' and natype[typeup-1] == 'RNA': # Scaffold strand
                    if baseseq == 'A':
                        refcrds = arna.Ascaf[:,3:6]
                        refatoms = arna.Ascaf[:,0]
                        restype = 'ADE'
                    elif baseseq == 'C':
                        refcrds = arna.Cscaf[:,3:6]
                        refatoms = arna.Cscaf[:,0]
                        restype = 'CYT'
                    elif baseseq == 'G':
                        refcrds = arna.Gscaf[:,3:6]
                        refatoms = arna.Gscaf[:,0]
                        restype = 'GUA'
                    elif baseseq == 'U':
                        refcrds = arna.Uscaf[:,3:6]
                        refatoms = arna.Uscaf[:,0]
                        restype = 'URA'
                    elif baseseq == 'T':
                        refcrds = arna.Uscaf[:,3:6]
                        refatoms = arna.Uscaf[:,0]
                        restype = 'URA'
                    else:
                        print('...Error: No base sequence for scaffold strand...\n')
                elif typeup == 2 and abtype == 'A' and natype[typeup-1] == 'RNA': # Staple strand
                    if baseseq == 'A':
                        refcrds = arna.Astap[:,3:6]
                        refatoms = arna.Astap[:,0]
                        restype = 'ADE'
                    elif baseseq == 'C':
                        refcrds = arna.Cstap[:,3:6]
                        refatoms = arna.Cstap[:,0]
                        restype = 'CYT'
                    elif baseseq == 'G':
                        refcrds = arna.Gstap[:,3:6]
                        refatoms = arna.Gstap[:,0]
                        restype = 'GUA'
                    elif baseseq == 'U':
                        refcrds = arna.Ustap[:,3:6]
                        refatoms = arna.Ustap[:,0]
                        restype = 'URA'
                    elif baseseq == 'T':
                        refcrds = arna.Ustap[:,3:6]
                        refatoms = arna.Ustap[:,0]
                        restype = 'URA'
                else:
                    print('...Error: No base sequence available in database...\n')
                    continue

                # First move to upstream base position
                xyzorigin = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])

                # Transform upstream base to XYZ origin
                transformMat = getTransMat(xyzorigin, xyzbase00)

                upbasecrds = applyTransMat(transformMat, refcrds)

                # Reset temporary rotation matrix to total rotation matrix
                Rtemp = Rtot

                iangle = angle * (jj+1) / (sslength+1)
                #print iangle

                # Test - Use cubic Bezier function to interpolate curve
                # d0 - upstream base, d3 - downstream base
                #
                # B(t) = (1 - t)^3 * d0 +
                #        3(1 - t)^2 * t * d1 +
                #        3(1 - t) * t^2 * d2 +
                #        t^3 * d3

                # Fraction along Bezier curve
                t = (float(jj) + 1) / (float(sslength) + 1)

                # Use d0 (upstream base) as reference point for Bezier interpolation
                d0 = np.array([0.0, 0.0, 0.0])
                d3 = np.array([xx0do - xx0up, yy0do - yy0up, zz0do - zz0up])

                #print d0, d1, d2, d3

                # Bezier contributions
                B3 = (1 - t)**3 * d0
                B2 = 3 * (1 - t)**2 * t * d1
                B1 = 3 * (1 - t) * t**2 * d2
                B0 = t**3 * d3
                #print B3, B2, B1, B0

                # Total Bezier function for ssDNA region
                Bt = B3 + B2 + B1 + B0
                #print Bt

                # Set interpolated vector to Bezier sum
                ivec = Bt

                # Switch back to Euler rotation matrix
                Rrotiter = np.array(axisangletoeul(iangle,axis))

                Rtemp[:3,:3] = Rrotiter
                Rtemp[:3,3] = ivec
                #print Rtemp

                # Additional step if calculating A-form structure
                if abtype == 'A':

                    # Two local parameters change to go from the B- to A- coordinate frame:
                    # x-displacement = -4.81 Angstroms
                    # inclination = 19.8 degrees

                    # Set intrinsic parameters for rotation
                    alpha = [14.7] # rotation angle around x-axis (degrees)
                    beta = [0.0] # rotation angle around y-axis (degrees)
                    gamma = [0.0] # rotation angle around z-axis (degrees)

                    xdisp = [-4.17] # Angstrom
                    ydisp = [0.0] # Angstrom
                    zdisp = [0.0] # Angstrom

                    alpharad = radians(alpha)
                    betarad = radians(beta)
                    gammarad = radians(gamma)

                    # Set intrinsic rotation matrix for B- to A- coordinate transformation
                    R = zeros((4,4),dtype=float)
                    R[0,0] = cos(betarad) * cos(gammarad)
                    R[0,1] = -cos(betarad) * sin(gammarad)
                    R[0,2] = sin(betarad)
                    R[1,0] = cos(alpharad) * sin(gammarad) + cos(gammarad) * sin(alpharad) * sin(betarad)
                    R[1,1] = cos(alpharad) * cos(gammarad) - sin(alpharad) * sin(betarad) * sin(gammarad)
                    R[1,2] = -cos(betarad) * sin(alpharad)
                    R[2,0] = sin(alpharad) * sin(gammarad) - cos(alpharad) * cos(gammarad) * sin(betarad)
                    R[2,1] = cos(gammarad) * sin(alpharad) + cos(alpharad) * sin(betarad) * sin(gammarad)
                    R[2,2] = cos(alpharad) * cos(betarad)
                    R[0,3] = xdisp[0]
                    R[1,3] = ydisp[0]
                    R[2,3] = zdisp[0]
                    R[3,3] = 1

                    batransform = R

                    # Apply B to A-form transform matrix
                    basecrds = applyTransMat(batransform, upbasecrds)

                    # Transform A-form base to Bezier position
                    basecrds = applyTransMat(Rtemp, basecrds)

                else:
                    # Transform B-form base to Bezier position
                    basecrds = applyTransMat(Rtemp, upbasecrds)

                # Move base back to upbase coordinates
                basecrds = translate(basecrds,np.array([xx0up, yy0up, zz0up]))

                # Write out PDB file sequentially
                # Pass {filename, chain, residue number, atom number, residue type,
                # atom types, base coords} to PDB writer
                atomnum, mmatomnum = writePDBresidue(filename, chlist, chainnum, resnum, atomnum, \
                                          mmatomnum, restype, refatoms, basecrds, pN, fpdb, fmm, fseg)

                # Iterate residue indexing
                resnum += 1

        # Now pull reference base information
        refcrds = []
        refatoms = []
        restype = ''
        #print type, baseseq
        if type == 1 and abtype == 'B' and natype[type-1] == 'DNA': # Scaffold strand
            if baseseq == 'A':
                refcrds = bdna.Ascaf[:,3:6]
                refatoms = bdna.Ascaf[:,0]
                restype = 'ADE'
            elif baseseq == 'C':
                refcrds = bdna.Cscaf[:,3:6]
                refatoms = bdna.Cscaf[:,0]
                restype = 'CYT'
            elif baseseq == 'G':
                refcrds = bdna.Gscaf[:,3:6]
                refatoms = bdna.Gscaf[:,0]
                restype = 'GUA'
            elif baseseq == 'T':
                refcrds = bdna.Tscaf[:,3:6]
                refatoms = bdna.Tscaf[:,0]
                restype = 'THY'
            else:
                print('...Error: No base sequence for scaffold strand...\n')
        elif type == 2 and abtype == 'B' and natype[type-1] == 'DNA': # Staple strand
            if baseseq == 'A':
                refcrds = bdna.Astap[:,3:6]
                refatoms = bdna.Astap[:,0]
                restype = 'ADE'
            elif baseseq == 'C':
                refcrds = bdna.Cstap[:,3:6]
                refatoms = bdna.Cstap[:,0]
                restype = 'CYT'
            elif baseseq == 'G':
                refcrds = bdna.Gstap[:,3:6]
                refatoms = bdna.Gstap[:,0]
                restype = 'GUA'
            elif baseseq == 'T':
                refcrds = bdna.Tstap[:,3:6]
                refatoms = bdna.Tstap[:,0]
                restype = 'THY'
            else:
                print('...Error: No base sequence for staple strand...\n')
        elif type == 1 and abtype == 'A' and natype[type-1] == 'DNA': # Scaffold strand
            if baseseq == 'A':
                refcrds = adna.Ascaf[:,3:6]
                refatoms = adna.Ascaf[:,0]
                restype = 'ADE'
            elif baseseq == 'C':
                refcrds = adna.Cscaf[:,3:6]
                refatoms = adna.Cscaf[:,0]
                restype = 'CYT'
            elif baseseq == 'G':
                refcrds = adna.Gscaf[:,3:6]
                refatoms = adna.Gscaf[:,0]
                restype = 'GUA'
            elif baseseq == 'T':
                refcrds = adna.Tscaf[:,3:6]
                refatoms = adna.Tscaf[:,0]
                restype = 'THY'
            else:
                print('...Error: No base sequence for scaffold strand...\n')
        elif type == 2 and abtype == 'A' and natype[type-1] == 'DNA': # Staple strand
            if baseseq == 'A':
                refcrds = adna.Astap[:,3:6]
                refatoms = adna.Astap[:,0]
                restype = 'ADE'
            elif baseseq == 'C':
                refcrds = adna.Cstap[:,3:6]
                refatoms = adna.Cstap[:,0]
                restype = 'CYT'
            elif baseseq == 'G':
                refcrds = adna.Gstap[:,3:6]
                refatoms = adna.Gstap[:,0]
                restype = 'GUA'
            elif baseseq == 'T':
                refcrds = adna.Tstap[:,3:6]
                refatoms = adna.Tstap[:,0]
                restype = 'THY'
            else:
                print('...Error: No base sequence for staple strand...\n')
        elif type == 1 and abtype == 'A' and natype[type-1] == 'RNA': # Scaffold strand
            if baseseq == 'A':
                refcrds = arna.Ascaf[:,3:6]
                refatoms = arna.Ascaf[:,0]
                restype = 'ADE'
            elif baseseq == 'C':
                refcrds = arna.Cscaf[:,3:6]
                refatoms = arna.Cscaf[:,0]
                restype = 'CYT'
            elif baseseq == 'G':
                refcrds = arna.Gscaf[:,3:6]
                refatoms = arna.Gscaf[:,0]
                restype = 'GUA'
            elif baseseq == 'U':
                refcrds = arna.Uscaf[:,3:6]
                refatoms = arna.Uscaf[:,0]
                restype = 'URA'
            elif baseseq == 'T':
                refcrds = arna.Uscaf[:,3:6]
                refatoms = arna.Uscaf[:,0]
                restype = 'URA'
            else:
                print('...No base sequence for scaffold strand...\n')
        elif type == 2 and abtype == 'A' and natype[type-1] == 'RNA': # Staple strand
            if baseseq == 'A':
                refcrds = arna.Astap[:,3:6]
                refatoms = arna.Astap[:,0]
                restype = 'ADE'
            elif baseseq == 'C':
                refcrds = arna.Cstap[:,3:6]
                refatoms = arna.Cstap[:,0]
                restype = 'CYT'
            elif baseseq == 'G':
                refcrds = arna.Gstap[:,3:6]
                refatoms = arna.Gstap[:,0]
                restype = 'GUA'
            elif baseseq == 'U':
                refcrds = arna.Ustap[:,3:6]
                refatoms = arna.Ustap[:,0]
                restype = 'URA'
            elif baseseq == 'T':
                refcrds = arna.Ustap[:,3:6]
                refatoms = arna.Ustap[:,0]
                restype = 'URA'
            else:
                print('...Error: No base sequence for staple strand...\n')
        else:
#            print('...Error: Base sequence not labelled as scaffold or staple strand...\n')
            continue

        # Additional step if calculating A-DNA structure
        if abtype == 'A': # Transformation for A-form DNA

            # Two local parameters change to go from the B- to A- coordinate frame:
            # x-displacement = -4.81 Angstroms
            # inclination = 19.8 degrees

            # Set intrinsic parameters for rotation
            alpha = [14.7] # rotation angle around x-axis (degrees)
            beta = [0.0] # rotation angle around y-axis (degrees)
            gamma = [0.0] # rotation angle around z-axis (degrees)

            xdisp = [-4.17] # Angstrom
            ydisp = [0.0] # Angstrom
            zdisp = [0.0] # Angstrom

            alpharad = radians(alpha)
            betarad = radians(beta)
            gammarad = radians(gamma)

            # Set intrinsic rotation matrix for B- to A- coordinate transformation
            R = zeros((4,4),dtype=float)
            R[0,0] = cos(betarad) * cos(gammarad)
            R[0,1] = -cos(betarad) * sin(gammarad)
            R[0,2] = sin(betarad)
            R[1,0] = cos(alpharad) * sin(gammarad) + cos(gammarad) * sin(alpharad) * sin(betarad)
            R[1,1] = cos(alpharad) * cos(gammarad) - sin(alpharad) * sin(betarad) * sin(gammarad)
            R[1,2] = -cos(betarad) * sin(alpharad)
            R[2,0] = sin(alpharad) * sin(gammarad) - cos(alpharad) * cos(gammarad) * sin(betarad)
            R[2,1] = cos(gammarad) * sin(alpharad) + cos(alpharad) * sin(betarad) * sin(gammarad)
            R[2,2] = cos(alpharad) * cos(betarad)
            R[0,3] = xdisp[0]
            R[1,3] = ydisp[0]
            R[2,3] = zdisp[0]
            R[3,3] = 1

            batransform = R

            # Apply B to A-form transform matrix
            abcrds = applyTransMat(batransform, refcrds)

            # Now transform reference coordinates back to base coordinate system
            basecrds = applyTransMat(transformMat, abcrds)

        else: # Standard B-form DNA

            # Now transform reference coordinates to base coordinate system
            basecrds = applyTransMat(transformMat, refcrds)

        # Write out PDB file sequentially
        # Pass {filename, chain, residue number, atom number, residue type,
        # atom types, base coords} to PDB writer
        atomnum, mmatomnum = writePDBresidue(filename, chlist, chainnum, resnum, atomnum, \
                                  mmatomnum, restype, refatoms, basecrds, pN, fpdb, fmm, fseg)

        # Iterate residue indexing
        resnum += 1
        if basedown == -1:

            # Standard PDB end chain
            fpdb.write('TER\n')
            
            # Multi-model PDB ends model here
            fmm.write('TER\nENDMDL\n')

            # Chain segment PDB end chain
            fseg.write('TER\n')


            # Iterate chainnum and return mmatomnum to 1
            chainnum += 1
            mmatomnum = 1
            resnum = 1

            # Chainlist definition
            if chainnum < 62:
                chlist = chainlist[chainnum]
            elif chainnum == int(62 * (cc+1)): 
                chlist = chainlist[chainnum - int(62*(cc+1))]
                cc += 1
            else:
                chlist = chainlist[chainnum - int(62*cc)]
                
    # close any open files
    fpdb.close()
    fmm.close()
    fseg.close()
    
    return 1
