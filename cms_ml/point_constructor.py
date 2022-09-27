import numpy as np

def harm_points(first, number, sb = 0, sb_n = 0, name="harm"):
    """
    Returns a list of dictionaries with the key frequencies, sidebands and meta data for including in plots.
    ---------------------------------------------
    
    first : the frequency of the first harmonic
    number : the number of harmonics which shall be generated (must be > 0)
    sb : the frequency of the sideband (modulating frequency). Sidebands are generate for both -/+.
    sb_n : the number of sideband frequencies
    
    Note: as the the result in evaluated in the return the functionally effectively is creating a 
    input statement to be evaluated as a string.
    """
    # Instantiate the result list to be appended to.
    result = []
    
    # Set the harmonic index to 1
    hi = 1
    # Loop round range of required harmonics
    for i in np.arange(first,first*(number + 1),first):

        # If no sidebands are required then write it the list as empty; else generate sideband list
        if sb == 0:
            sbs = '[]'
        else:
            sb_ar = np.arange(-sb_n * sb, (sb_n * sb) + sb, sb)
            sb_ar = sb_ar[sb_ar!=0] + i

            sbs = '['+ ','.join(['%.2f' % x for x in sb_ar]) + ']'
        
        # Create dictionary as a string and substitute in frequencies and meta-data.
        result_t = """
        {
            'name': '%s_%s',
            'frequency': %s,
            'sb': %s
        }""" % (name, hi,'%.1f' % i, sbs)
        # append result to list
        result.append(result_t)
        # increase harmonic index for next iteration
        hi = 1 + hi
    # return is the evaluation of a string to return a python list
    return eval("[" + ",".join(result) + "]")