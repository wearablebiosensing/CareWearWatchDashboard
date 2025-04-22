# features to analyse
#mean
def feature_mean(feature_name,accel_gyro_data):
    mean = accel_gyro_data.mean()
    mean_transposed_df = mean.to_frame().T
    mean_transposed_df.columns = ["Accel_X_"+feature_name ,"Accel_Y_" +feature_name ,"Accel_Z_" +feature_name,"Gyro_X_" +feature_name, "Gyro_Y_" + feature_name ,"Gyro_Z_" +feature_name]
    return mean_transposed_df

#std
def feature_std(feature_name,accel_gyro_data):
    std = accel_gyro_data.std()
    std_transposed_df = std.to_frame().T
    std_transposed_df.columns = ["Accel_X_"+feature_name ,"Accel_Y_" +feature_name ,"Accel_Z_" +feature_name,"Gyro_X_" +feature_name, "Gyro_Y_" + feature_name ,"Gyro_Z_" +feature_name]
    return std_transposed_df

#kurtosis
def feature_kurtosis(feature_name,accel_gyro_data):
    kurtosis = accel_gyro_data.kurtosis()
    kurtosis_transposed_df = kurtosis.to_frame().T
    kurtosis_transposed_df.columns = ["Accel_X_"+feature_name ,"Accel_Y_" +feature_name ,"Accel_Z_" +feature_name,"Gyro_X_" +feature_name, "Gyro_Y_" + feature_name ,"Gyro_Z_"+feature_name]
    return kurtosis_transposed_df

#median
def feature_median(feature_name,accel_gyro_data):
    median = accel_gyro_data.median()
    median_transposed_df = median.to_frame().T
    median_transposed_df.columns = ["Accel_X_"+feature_name ,"Accel_Y_" +feature_name ,"Accel_Z_" +feature_name,"Gyro_X_" +feature_name, "Gyro_Y_" + feature_name ,"Gyro_Z_" + feature_name]
    return median_transposed_df

#skewness
def feature_skewness(feature_name,accel_gyro_data):
    skewness = accel_gyro_data.skew()
    skewness_transposed_df = skewness.to_frame().T
    skewness_transposed_df.columns = ["Accel_X_"+feature_name ,"Accel_Y_" +feature_name ,"Accel_Z_" +feature_name,"Gyro_X_" +feature_name, "Gyro_Y_" + feature_name ,"Gyro_Z_" + feature_name]
    return skewness_transposed_df
# 'Accel_X_mean', 'Accel_Y_mean', 'Accel_Z_mean', 'Gyro_X_mean',
#        'Gyro_Y_mean', 'Gyro_Z_mean', 'Accel_X_std', 'Accel_Y_std',
#        'Accel_Z_std', 'Gyro_X_std', 'Gyro_Y_std', 'Gyro_Z_std',
#        'Accel_X_kurtosis', 'Accel_Y_kurtosis', 'Accel_Z_kurtosis',
#        'Gyro_X_kurtosis', 'Gyro_Y_kurtosis', 'Gyro_Z_kurtosis',
#        'Accel_X_skewness', 'Accel_Y_skewness', 'Accel_Z_skewness',
#        'Gyro_X_skewness', 'Gyro_Y_skewness', 'Gyro_Z_skewness', 'type'],
# create table 
def get_concated_features(accel_gyro_data):
    # Subset the DataFrame to include only the specified columns
    accel_gyro_data = accel_gyro_data[['Accel_X', 'Accel_Y', 'Accel_Z', 'Gyro_X', 'Gyro_Y', 'Gyro_Z']]
    df1 = feature_mean("mean",accel_gyro_data)
    df2 = feature_median("median",accel_gyro_data)
    df3 = feature_std("std",accel_gyro_data)
    df4 = feature_kurtosis("kurtosis",accel_gyro_data)
    df5 =feature_skewness("skewness",accel_gyro_data)
    df = [df1, df2, df3, df4, df5]
    result_df = pd.concat(df, axis=1)

    return result_df

X_test_windowed_df_features = get_concated_features(windowed_df)
