import sys
from dataclasses import dataclass

import numpy as np 
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, StandardScaler
from sklearn.preprocessing import LabelEncoder
from category_encoders import TargetEncoder

from src.exception import CustomException
from src.logger import logging
import os

from src.utils import save_object

@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path=os.path.join('artifacts',"proprocessor.pkl")

class DataTransformation:
    def __init__(self):
        self.data_transformation_config=DataTransformationConfig()

    def get_data_transformer_object(self):
        '''
        This function si responsible for data trnasformation
        
        '''
        try:
            numerical_columns = ['monthly_charge', 'zip_code', 'longitude', 'age', 'latitude',
                                 'total_long_distance_charges', 'tenure_in_months', 'total_revenue', 'number_of_referrals',
                                 'total_charges', 'avg_monthly_long_distance_charges', 'avg_monthly_gb_download', 'number_of_dependents',
                                 'engagement_score', 'num_addon_services']
            categorical_columns = ['city', 'contract', 'payment_method', 'offer', 'paperless_billing', 'gender', 'married', 'internet_type']

            num_pipeline= Pipeline(
                steps=[
                ("imputer",SimpleImputer(strategy="median")),
                ("scaler",StandardScaler())

                ]
            )
            # diff = ColumnTransformer(
            #     [
            #         ("tenure_category",OrdinalEncoder(), 'tenure_category'),
            #         ("contract",OneHotEncoder(), 'contract'),
            #         ("paperless_billing", LabelEncoder(),'paperless_billing'),
            #         ("city", TargetEncoder(),'city')
            #     ]
            # )
            cat_pipeline=Pipeline(

                steps=[
                ("imputer",SimpleImputer(strategy="most_frequent")),
                ("one_hot_encoder",OneHotEncoder(handle_unknown='ignore',sparse_output=False,drop='first'))
                ]

            )

            logging.info(f"Categorical columns: {categorical_columns}")
            logging.info(f"Numerical columns: {numerical_columns}")

            preprocessor=ColumnTransformer(
                [
                ("num_pipeline",num_pipeline,numerical_columns),
                ("cat_pipelines",cat_pipeline,categorical_columns)

                ]


            )

            return preprocessor
        
        except Exception as e:
            raise CustomException(e,sys)
        
    def initiate_data_transformation(self,train_path,test_path):

        try:
            train_df=pd.read_csv(train_path)
            test_df=pd.read_csv(test_path)

            logging.info("Read train and test data completed")

            logging.info("Obtaining preprocessing object")

            preprocessing_obj=self.get_data_transformer_object()

            target_column_name="customer_status"
            numerical_columns = [
                    'age', 'number_of_dependents', 'zip_code', 'latitude', 'longitude',
                    'number_of_referrals', 'tenure_in_months', 'avg_monthly_long_distance_charges',
                    'avg_monthly_gb_download', 'monthly_charge', 'total_charges',
                    'total_refunds', 'total_extra_data_charges', 'total_long_distance_charges',
                    'total_revenue', 'has_offer', 'offer_popularity'
                ]

            input_feature_train_df=train_df.drop(columns=[target_column_name],axis=1)
            target_feature_train_df=train_df[target_column_name]

            input_feature_test_df=test_df.drop(columns=[target_column_name],axis=1)
            target_feature_test_df=test_df[target_column_name]

            logging.info(
                f"Applying preprocessing object on training dataframe and testing dataframe."
            )

            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr=preprocessing_obj.transform(input_feature_test_df)

            train_arr = np.c_[input_feature_train_arr, np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]

            logging.info(f"Saved preprocessing object.")

            save_object(

                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=preprocessing_obj

            )

            return (
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessor_obj_file_path,
            )
        except Exception as e:
            raise CustomException(e,sys)