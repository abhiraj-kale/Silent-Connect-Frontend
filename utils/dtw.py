import pandas as pd
from fastdtw import fastdtw
import numpy as np
from models.sign_model import SignModel


def dtw_distances(recorded_sign: SignModel, reference_signs: pd.DataFrame) -> pd.DataFrame:
    """
    Use DTW to compute similarity between the recorded sign and the reference signs.

    :param recorded_sign: A SignModel object containing the data gathered during recording.
    :param reference_signs: A pandas DataFrame containing the reference signs.
                            The DataFrame must have the following columns:
                            - name: str
                            - sign_model: SignModel
                            - distance: float64
    :return: A sign dictionary sorted by the distances from the recorded sign.
    """

    # Get the embeddings of the recorded sign
    rec_left_hand = recorded_sign.lh_embedding
    rec_right_hand = recorded_sign.rh_embedding

    # Loop through the reference signs and compute their distances
    for idx, row in reference_signs.iterrows():
        # Get the variables for the current row
        ref_sign_name, ref_sign_model, distance = row["name"], row["sign_model"], row["distance"]

        # If the reference sign has the same number of hands, compute the distance using fastdtw
        if (recorded_sign.has_left_hand == ref_sign_model.has_left_hand) and \
                (recorded_sign.has_right_hand == ref_sign_model.has_right_hand):
            ref_left_hand, ref_right_hand = ref_sign_model.lh_embedding, ref_sign_model.rh_embedding

            if recorded_sign.has_left_hand:
                distance += fastdtw(rec_left_hand, ref_left_hand)[0]

            if recorded_sign.has_right_hand:
                distance += fastdtw(rec_right_hand, ref_right_hand)[0]

        # If the reference sign has a different number of hands, set the distance to infinity
        else:
            distance = np.inf

        # Update the distance in the row
        reference_signs.at[idx, "distance"] = distance

    # Sort the reference signs by distance
    return reference_signs.sort_values(by=["distance"])

