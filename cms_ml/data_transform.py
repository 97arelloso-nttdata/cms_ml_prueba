# Auxilliary functions to handle parser outputs
import pandas as pd

# Generate function to convert list of data frame with list entries to a dataframe

def df_list_to_df(df, x_col, y_col = 'y_value', label_col = 'timestamp', turbine_col = 'turbine_id', sensor_col = 'sensor'):
    """
    Returns a dataframe
    Generate function to convert list of data frame with list entries to a dataframe
    -------------------------
    df : Dataframe with the output format from 'parse_cms_directory'
    x_col : name of column with the delta to reconstruct the x-axis
    y_col : name of column with the list of amplitudes
    
    """    
    # Instantiate lists to be appened to.
    x = []
    y = []
    turbine = []
    sensor = []
    label = []
    
    # Iterate through each row and transpose list of amplitudes and generate x-axis
    for i, row in df.iterrows():
    
        if type(list(x_col))  == type([]):
            x = x + list(x_col)
        else:
            x = x + row[x_col]

        y = y + list(row[y_col])
        
        # Append meta-data
        label = label + [str(row[label_col])]*len(list(row[y_col]))
        turbine = turbine + [str(row[turbine_col])]*len(list(row[y_col]))
        sensor = sensor + [str(row[sensor_col])]*len(list(row[y_col]))
    # return data frame
    return pd.DataFrame({'x':x, 'y':y, 'label':label, 'turbine':turbine, 'sensor':sensor})
    
    
def head_for_unique(df, col):
    """
    Returns the head of each for each instance of a dataframe filtered on unique values
    
    df : a dataframe to be truncated to the head.
    col : the column name for which the unique values will be generated.
    
    """
    # Instantiate an empty dataset
    data = pd.DataFrame({})
    
    # Calculate the unique items in the set
    unique = sorted(list(set(df[col])))
    
    # for each unique value filter the dataset and return the head
    for i in unique:
        data = pd.concat([data,
                         df[df[col] == i].head()])
    return data