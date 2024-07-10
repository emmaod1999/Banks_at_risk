import pandas as pd
import numpy as np
import re
import os

def convert_EXIO_to_NACE(score, converter, type, calc):
    """
    :param score: the score you are converting from EXIO to nace
    :param converter: the conversion table
    :param type: the type of score (whether it is a scope 1 (only Code) or whether it contains region as well
    :param calc: whether the score is mean, min or max
    :return: the NACE scores
    """
    if type != 'region_code' and type != 'code_only' and type != 'region_only':
        print('ERROR: Type must be "region_code" or "code_only" or "region_only"')
        return
    if calc != 'mean' and calc != 'min' and calc != 'max':
        print('ERROR: calc must be "mean" or "min" or "max"')
        return

    score_T_EXIO = score.transpose()
    score_T_EXIO.index.name = "sector"
    score_T = pd.merge(score_T_EXIO, converter, left_index=True,
                                        right_index=True)
    if calc== 'mean':
        if type == 'code_only':
            score_T = score_T.groupby('Code').mean()
        if type == 'region_only':
            score_T = score_T.groupby('region').mean()
        if type == 'region_code':
            score_T = score_T.groupby(['region', 'Code']).mean()
    if calc =='min':
        if type == 'code_only':
            score_T = score_T.groupby('Code').min()
        if type == 'region_only':
            score_T = score_T.groupby('region').min()
        if type == 'region_code':
            score_T = score_T.groupby(['region', 'Code']).min()
    if calc == 'max':
        if type == 'code_only':
            score_T = score_T.groupby('Code').max()
        if type == 'region_only':
            score_T = score_T.groupby('region').max()
        if type == 'region_code':
            score_T = score_T.groupby(['region', 'Code']).max()

    return score_T