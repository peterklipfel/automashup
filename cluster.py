# Class for cluster info
import numpy as np
from scipy.cluster.vq import kmeans,vq
import echonest.remix.audio as audio
import scipy
import matplotlib.pyplot as plt

dbg = 0
ftrDim = 12+12+2

regionTypes = [ 'bars', 'beats', 'sections', 'tatums' ]

def getRegionsOfType( analysis, rtype ):
    if rtype == 'bars':
        return analysis.bars
    elif rtype == 'beats':
        return analysis.beats
    elif rtype == 'sections':
        return analysis.sections
    elif rtype == 'tatums':
        return analysis.tatums
    else:
        assert False


def computeFeatureVector( aregion ):
    f = np.zeros(ftrDim)
    f[0] = aregion.duration
    f[1] = aregion.mean_loudness()
    f[2:2+12] = np.log10( np.maximum( 1E-3, aregion.mean_pitches() ) )
    f[14:14+12] = aregion.mean_timbre()
    if dbg:
        print '\t\tComputed ftrs ', f
    return f

def createFeatureMatrixSongs( rtype, songFns ):
    D = None
    for fn in songFns:
        au = audio.LocalAudioFile(fn)
        regs = getRegionsOfType( au.analysis, rtype )
        if dbg:
            print '\tClustering %d %s regions for this song' % (len(regs),rtype)
        if D==None:
            D = createFeatureMatrix( regs )
        else:
            D = np.vstack( [D, createFeatureMatrix(regs)] )
        if dbg:
            print '\tFeature matrix has grown to size ', D.shape
    return D

def createFeatureMatrix( aregionList ):
    n = len(aregionList)
    D = ftrDim
    if dbg:
        print 'D=',D
    X = np.zeros( (n,D), dtype=float )
    for i,a in enumerate(aregionList):
        X[i,:] = computeFeatureVector( a )
    return X

def clusterData( X ):
    # computing K-Means with ? clusters
    ncl = np.round( np.sqrt( X.shape[0]/2 ) )
    print 'k-means clustering, k = %d...' % ncl
    centroids,_ = kmeans(X,ncl)
    # assign each sample to a cluster
    clids,_ = vq(X,centroids)
    print '   finished.'
    if dbg:
        # histogram of class labels
        plt.interactive(1)
        plt.figure()
        plt.hist( clids, ncl )
        plt.title('class label hist')
        plt.draw()
    return (clids, centroids)

def computeClusterTxProbs( clids, centroids ):
    assert np.min(clids) == 0
    nbcl = len( np.unique( clids ) )
    assert nbcl-1 == np.max(clids)
    D = scipy.spatial.distance.squareform(\
        scipy.spatial.distance.pdist( centroids, 'euclidean' ) )
    assert D.shape == (nbcl,nbcl)
    # Make a transition probability matrix.  prob is inversely proportional to
    # distance between clusters.  The bigger k, the less effect distance has.
    k = 15.0
    P = np.exp( -(D/k) )
    # no prob of transitioning to self
    for i in range(nbcl):
        P[i,i] = 0.0
    # Now multiply columns by tf-idf.  That is, increase weight for clusters
    # with fewer members.
    (tf,foo) = np.histogram( clids, range(nbcl+1) )
    assert len(tf) == nbcl
    assert np.sum(tf) == len(clids)
    wt = np.log( len(clids) / tf )
    for i in range(nbcl):
        P[:,i] *= wt[i]
    # normalise so that each row sums to one
    psums = np.sum(P,1)
    assert np.all( psums > 0 )
    for i in range(nbcl):
        P[:,i] /= psums
    # add in a uniform
    alpha = 0.05
    P = alpha*np.ones(P.shape)/nbcl + (1-alpha)*P
    if dbg:
        print 'Cluster tx probs = '
        print P
        plt.interactive(1)
        plt.figure()
        plt.imshow(P)
        plt.title('trans probs')
        plt.set_cmap('gray')
        plt.draw()
    assert np.all( np.abs(np.sum(P,1)-1) < 1E-5 )
    return P

class ClusterInfo:

    def __init__(self, rtype, songFileList):
        self.m_rtype = rtype
        # n x D matrix
        X = createFeatureMatrixSongs( rtype, songFileList )
        if dbg:
            print 'Size of full feature matrix = ', X.shape

        (self.m_clusterIds,self.m_clusterCentres) = clusterData( X )

        if dbg:
            print 'Found %d clusters' % self.m_clusterCentres.shape[0]
            
        self.m_clusterTransProbs = computeClusterTxProbs( \
            self.m_clusterIds, self.m_clusterCentres )

        if dbg:
            plt.waitforbuttonpress()
