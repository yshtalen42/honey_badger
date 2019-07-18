import numpy as np

# truncate or scale hessian to reduce correlations

def diag_lens(mat):
    return np.sqrt(np.diag(mat))

def set_diag_lens(mat, diaglens):
    return np.dot(diaglens, np.dot(mat, diaglens))

def eye_mat(mat):
    return np.eye(np.shape(mat)[0])

def unit_diag(mat): # scales out diagonal lengths from matrix
    diaginvlens = np.diag(1./diag_lens(mat))
    return np.dot(diaginvlens, np.dot(mat, diaginvlens))

def scale_offdiag(mat, factor): # scales off diagonal elements by a scalar
    diag = np.diag(np.diag(mat))
    return diag + factor * (mat-diag)

def truncate_offdiag(mat, absmax): # truncate off-diagonal elements to +/- absmax
    diag = np.diag(np.diag(mat))
    offdiag = mat-diag
    offdiag[offdiag > absmax] = absmax
    offdiag[offdiag < -absmax] = -absmax
    return diag + offdiag

# including correlations increases the net area covered by the kernel
# => possibly huge steps along major axis
# this attempts to limit this length by calculating eigenlengths
# and truncating to some maximum length
# treat eigenlength as a zscore if diag(mat) is identity
def limit_maxeigenlength(mat, eigenlengthmax, offdiag_function=scale_offdiag):
    for absmax in np.linspace(1,0,101):
        truncmat = offdiag_function(mat, absmax)
        if np.linalg.det(truncmat) < 0: continue # prevent diverging model
        evals = np.linalg.eig(truncmat)[0]
        if np.sum(evals < 0) > 0: continue # prevent diverging model
        elens = 1./np.sqrt(np.abs(evals))
        if max(elens) <= eigenlengthmax:
            print 'absmax = ', absmax, '\t max(eigen lengths) = ', max(elens)
            return truncmat

# reduced norm eigen length is norm of vector of eigen lengths divided by sqrt(n_eigen_vals)
def limit_reducednormeigenlength(mat, eigenlengthmax, offdiag_function=scale_offdiag):
    for absmax in np.linspace(1,0,101):
        truncmat = offdiag_function(mat, absmax)
        if np.linalg.det(truncmat) < 0: continue # prevent diverging model
        evals = np.linalg.eig(truncmat)[0]
        if np.sum(evals < 0) > 0: continue # prevent diverging model
        elenssqr = 1./np.abs(evals)
        normelen = np.sqrt(np.sum(elenssqr) / len(elenssqr))
        if normelen <= eigenlengthmax:
            print 'absmax = ', absmax, '\t norm(eigen lengths) = ', normelen
            return truncmat