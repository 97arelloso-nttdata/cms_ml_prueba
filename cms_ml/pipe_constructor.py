import numpy as np


def band_gen(low, high, step, frequency_values = None, name="band", primitive = 'cms_ml.aggregations.amplitude.band.band_rms'):
    """Returns a list of dictionaries with the sequential frequencies bands
    for making aggregations to match the expected format of the the SigPro band_mean.
    
    Note: as the the result in evaluated in the return the functionally effectively is creating a 
    input statement to be evaluated as a string.
    
    args:
        low (int or float): 
            the starting frequency for the sequence
        high (int or float):
            the end frequency for the sequence
        step (int or float):
            the step and width of the band, in abolute terms.
        name (string):
            the name (becomes the prefix) of the indicator
    Returns:
        list:
            List of dictionaries matching the format of the primitives.
    
"""
    result = []
    for i in np.arange(low,high,step):
        str_i = str(i)
        str_i_step = str(i+step)
        
        config = {
            'name': name,
            'str_i': str_i,
            'str_i_step': str_i_step,
            'primitive': primitive
            
        }
        
        if frequency_values:
            result_t = """
            {{
                'name': '{name}_{str_i}_{str_i_step}',
                'primitive': '{primitive}',
                'init_params':{{'min_frequency':{str_i},'max_frequency':{str_i_step}, 'frequency_values': frequency_values}} 
            }}""".format(**config)
        else:
            result_t = """
            {{
                'name': '{name}_{str_i}_{str_i_step}',
                'primitive': '{primitive}',
                'init_params':{{'min_frequency':{str_i},'max_frequency':{str_i_step}}} 
            }}""".format(**config)
        result.append(result_t)
    return(eval("[" + ",".join(result) + "]"))
    



def harm_gen(first, number, width, frequency_values = None, name="harm", primitive = 'cms_ml.aggregations.amplitude.band.band_rms'):
    """Returns a list of dictionaries with the key frequencies bands (around harmonics) 
    for making aggregations to match the expected format of the the SigPro band_mean.
    
    Note: as the the result in evaluated in the return the functionally effectively is creating a 
    input statement to be evaluated as a string.
    
    args:
        first (int or float): 
            the frequency of the first harmonic
        number (int):
            the number of harmonics which shall be generated (must be > 0)
        width (int or float):
            the width of the band, in abolute terms, around the harmonic.
        name (str):
            the name (becomes the prefix) of the indicator
    
    """
    result = []
    harmonic_index = 1
    for i in np.arange(first,first*(number + 1),first):
        band_low = '%.1f' % (i-width)
        band_high = '%.1f' % (i+width)
        config = {
            'name': name,
            'band_low': band_low,
            'band_high': band_high,
            'primitive': primitive,
            'harmonic_index':harmonic_index,
            'frequency':'%.0f' % i
            
        }

        if frequency_values:
            result_t = """
        {{
            'name': '{name}{harmonic_index}_{frequency}Hz',
            'primitive': '{primitive}',
            'init_params':{{'min_frequency':{band_low},'max_frequency':{band_high}, 'frequency_values': frequency_values}}
        }}""".format(**config)
        else:
            result_t = """
        {{
            'name': '{name}{harmonic_index}_{frequency}Hz',
            'primitive': '{primitive}',
            'init_params':{{'min_frequency':{band_low},'max_frequency':{band_high}}} 
        }}""".format(**config)
        
        result.append(result_t)
        harmonic_index = 1 + harmonic_index
    return(eval("[" + ",".join(result) + "]"))
    
    
def harm_w_sideband_gen(first, number, width, sideband, sideband_number, frequency_values = None, name="harm", primitive = 'cms_ml.aggregations.amplitude.band.band_sideband_rms'):
    """Returns a list of dictionaries with the key frequencies bands (around harmonics) 
    and associated sideband bands (around sidebands) for making aggregations to match 
    the expected format of the the SigPro band_side_rms.
    
    Note: as the the result in evaluated in the return the functionally effectively is creating a 
    input statement to be evaluated as a string.
    
    args:
        first (int or float): 
            the frequency of the first harmonic
        number (int):
            the number of harmonics which shall be generated (must be > 0)
        width (int or float):
            the width of the band, in abolute terms, around the harmonic.
        sideband (int or float):
            the sideband frequency offset (-/+) from the harmonic.
        sideband_number (int):
            the number of sidebands around the harmonic
        name (str):
            the name (becomes the prefix) of the indicator
    
    """
    result = []
    harmonic_index = 1
    
    sb_ar = np.arange(-sideband_number * sideband, (sideband_number * sideband) + sideband, sideband)
    sb_ar = sb_ar[sb_ar!=0]

    for i in np.arange(first,first*(number + 1),first):
        
        band_low = '%.2f' % (i-width)
        band_high = '%.2f' % (i+width)
        sideband_list = []
        for si in sb_ar:
            sideband_list.append('(%.2f, %.2f)' % (si+i-width, si+i+width))
        
        sideband_string = "[" + ",".join(sideband_list) + "]"
        
        config = {
            'name': name,
            'band_low': band_low,
            'band_high': band_high,
            'primitive': primitive,
            'harmonic_index':harmonic_index,
            'frequency':'%.0f' % i,
            'sidebands':sideband_string
            
        }
        
        if frequency_values:
            result_t = """
            {
                'name': '{name}{harmonic_index}_{frequency}Hz_sb',
                'primitive': '{primitive}',
                'init_params':{'min_frequency':{band_low},'max_frequency':{band_high}, 'frequency_values': frequency_values, 'side_bands':{sidebands}}}
            }""".format(**config)
        else:
            result_t = """
            {{
                'name': '{name}{harmonic_index}_{frequency}Hz_sb',
                'primitive': '{primitive}',
                'init_params':{{'min_frequency':{band_low},'max_frequency':{band_high}, 'side_bands':{sidebands}}}
            }}""".format(**config)
            
        result.append(result_t)
        harmonic_index = 1 + harmonic_index
    return(eval("[" + ",".join(result) + "]"))
    
    
def harm_sideband_power_ratio_gen(first, number, width, sideband, sideband_number, frequency_values = None, name="harm", primitive = 'cms_ml.aggregations.amplitude.band.band_sideband_pr'):
    """ Returns a list of dictionaries with the key frequencies bands (around harmonics) 
    and associated sideband bands (around sidebands) for making aggregations to match 
    the expected format of the the SigPro band_sideband_pr.
    
    Note: as the the result in evaluated in the return the functionally effectively is creating a 
    input statement to be evaluated as a string.
    
    args:
        first (int or float): 
            the frequency of the first harmonic
        number (int):
            the number of harmonics which shall be generated (must be > 0)
        width (int or float):
            the width of the band, in abolute terms, around the harmonic.
        sideband (int or float):
            the sideband frequency offset (-/+) from the harmonic.
        sideband_number (int):
            the number of sidebands around the harmonic
        name (str):
            the name (becomes the prefix) of the indicator
            
    """
    result = []
    harmonic_index = 1
    
    sb_ar = np.arange(-sideband_number * sideband, (sideband_number * sideband) + sideband, sideband)
    sb_ar = sb_ar[sb_ar!=0]

    for i in np.arange(first,first*(number + 1),first):
        
        band_low = '%.2f' % (i-width)
        band_high = '%.2f' % (i+width)
        sideband_list = []
        for si in sb_ar:
            sideband_list.append('(%.2f, %.2f)' % (si+i-width, si+i+width))
        
        sideband_string = "[" + ",".join(sideband_list) + "]"
        
        config = {
            'name': name,
            'band_low': band_low,
            'band_high': band_high,
            'primitive': primitive,
            'harmonic_index':harmonic_index,
            'frequency':'%.0f' % i,
            'sidebands':sideband_string
            
        }
        
        if frequency_values:
            result_t = """
            {
                'name': '{name}{harmonic_index}_{frequency}Hz_sb',
                'primitive': '{primitive}',
                'init_params':{'min_frequency':{band_low},'max_frequency':{band_high}, 'frequency_values': frequency_values, 'side_bands':{sidebands}}}
            }""".format(**config)
        else:
            result_t = """
            {{
                'name': '{name}{harmonic_index}_{frequency}Hz_sb',
                'primitive': '{primitive}',
                'init_params':{{'min_frequency':{band_low},'max_frequency':{band_high}, 'side_bands':{sidebands}}}
            }}""".format(**config)
            
        result.append(result_t)
        harmonic_index = 1 + harmonic_index
    return(eval("[" + ",".join(result) + "]"))