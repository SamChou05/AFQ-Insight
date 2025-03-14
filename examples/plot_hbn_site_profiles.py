"""
===============================
Harmonize HBN data using ComBat
===============================

This example loads AFQ data from the Healthy Brain Network (HBN) preprocessed
diffusion derivatives [1]_. The HBN is a landmark pediatric mental health study.
Over the course of the study, it will collect diffusion MRI data from
approximately 5,000 children and adolescents. We recently processed the
available data from over 2,000 of these subjects, and provide the tract profiles
from this dataset, which can be downloaded from AWS thanks to
[INDI](http://fcon_1000.projects.nitrc.org/).

We first load the data by using the :func:`AFQDataset.from_files` static method
and supplying AWS S3 URIs instead of local file names. We then impute missing
values and plot the mean bundle profiles by scanning site, noting that there are
substantial site differences. Lastly, we harmonize the site differences using
NeuroComBat [2]_ and plot the harmonized bundle profiles to verify that the site
differences have been removed.

.. [1]  Adam Richie-Halford, Matthew Cieslak, Lei Ai, Sendy Caffarra, Sydney
   Covitz, Alexandre R. Franco, Iliana I. Karipidis, John Kruper, Michael
   Milham, Bárbara Avelar-Pereira, Ethan Roy, Valerie J. Sydnor, Jason Yeatman,
   The Fibr Community Science Consortium, Theodore D. Satterthwaite, and Ariel
   Rokem,
   "An open, analysis-ready, and quality controlled resource for pediatric brain
   white-matter research"
   bioRxiv 2022.02.24.481303;
   doi: https://doi.org/10.1101/2022.02.24.481303

.. [2] Jean-Philippe Fortin, Drew Parker, Birkan Tunc, Takanori Watanabe, Mark A
   Elliott, Kosha Ruparel, David R Roalf, Theodore D Satterthwaite, Ruben C Gur,
   Raquel E Gur, Robert T Schultz, Ragini Verma, Russell T Shinohara.
   "Harmonization Of Multi-Site Diffusion Tensor Imaging Data"
   NeuroImage, 161, 149-170, 2017;
   doi: https://doi.org/10.1016/j.neuroimage.2017.08.047

"""

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split

from afqinsight import AFQDataset
from afqinsight.neurocombat_sklearn import CombatModel
from afqinsight.plot import plot_tract_profiles

#############################################################################
# Fetch the HBN data
# ------------------
# As a shortcut, we have incorporated a few studies  into the software. In these
# cases, a :class:`AFQDataset` class instance can be initialized using the
# :func:`AFQDataset.from_study` static method. This expects the name of one of
# the studies that are supported (see the method documentation for the list of
# these studies). By passing `"hbn"`, we request that the object download the
# HBN dataset from the AWS Open Data program where it has been stored and
# initialize the objects with the subjects and nodes information. Subjects' age
# is set as the target variable. After dropping subjects that don't have their
# age recorded, there are 1867 subjects in the dataset.


dataset = AFQDataset.from_study("hbn")
dataset.drop_target_na()
print(dataset)

#############################################################################
# Train / test split
# ------------------
#
# We can pass the :class:`AFQDataset` class instance to scikit-learn's
# :func:`train_test_split` function, just as we would with an array.

dataset_train, dataset_test = train_test_split(dataset, test_size=0.5)

##########################################################################
# Impute missing values
# ---------------------
#
# Next we impute missing values using median imputation. We fit the imputer
# using the training set and then use it to transform both the training and test
# sets.

imputer = dataset_train.model_fit(SimpleImputer(strategy="median"))
dataset_train = dataset_train.model_transform(imputer)
dataset_test = dataset_test.model_transform(imputer)

##########################################################################
# Plot average bundle profiles by scan site
# -----------------------------------------
#
# Next we plot the mean bundle profiles in the test set by scanning site. The
# :func:`plot_tract_profiles` function takes as input an :class:`AFQDataset` and
# returns matplotlib figures displaying the mean bundle profile for each bundle
# and metric, optionally grouped by a categorical or continuous variable.

site_figs = plot_tract_profiles(
    X=dataset_test,
    group_by=dataset_test.classes["scan_site_id"][dataset_test.y[:, 2].astype(int)],
    group_by_name="Site",
    figsize=(14, 14),
)

##########################################################################
# Harmonize the sites and replot
# ------------------------------
#
# We can see that there are substantial scan site differences in both the
# FA and MD profiles. Let's use neuroComBat to harmonize the site differences
# and then replot the mean bundle profiles.
#

# N.B. We use the excellent `neurocombat_sklearn
# <https://github.com/Warvito/neurocombat_sklearn>`_ package, which we have
# ported and updated to support recent versions of scikit learn,
# to apply ComBat to
# our data. We love this library, however, it is not fully compliant with the
# scikit-learn transformer API, so we cannot use the
# :func:`AFQDataset.model_fit_transform` method to apply this transformer to our
# dataset. No problem! We can simply copy the unharmonized dataset into a new
# variable and then overwrite the features of the new dataset with the ComBat
# output.
#
# Lastly, we replot the mean bundle profiles and confirm that ComBat did its
# job.

# Fit the ComBat transformer to the training set

combat = CombatModel()
combat.fit(
    dataset_train.X,
    dataset_train.y[:, 2][:, np.newaxis],
    dataset_train.y[:, 1][:, np.newaxis],
    dataset_train.y[:, 0][:, np.newaxis],
)

# And then transform a copy of the test set
harmonized_test = dataset_test.copy()
harmonized_test.X = combat.transform(
    dataset_test.X,
    dataset_test.y[:, 2][:, np.newaxis],
    dataset_test.y[:, 1][:, np.newaxis],
    dataset_test.y[:, 0][:, np.newaxis],
)

site_figs = plot_tract_profiles(
    X=harmonized_test,
    group_by=harmonized_test.classes["scan_site_id"][
        harmonized_test.y[:, 2].astype(int)
    ],
    group_by_name="Site",
    figsize=(14, 14),
)
