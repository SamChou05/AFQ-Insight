from __future__ import absolute_import, division, print_function

import afqinsight as afqi
import numpy as np
import os.path as op
import pandas as pd

data_path = op.join(afqi.__path__[0], "data")
test_data_path = op.join(data_path, "test_data")


def test_AFQFeatureTransformer():
    nodes_path = op.join(data_path, "nodes.csv")
    nodes = pd.read_csv(nodes_path)
    transformer = afqi.AFQFeatureTransformer()
    x, groups, cols = transformer.transform(nodes)

    x_ref = np.load(op.join(test_data_path, "test_transform_x.npy"))
    groups_ref = np.load(op.join(test_data_path, "test_transform_groups.npy"))
    cols_ref = pd.read_pickle(op.join(test_data_path, "test_transform_cols.pkl"))

    assert np.all(x == x_ref)
    assert np.all(groups == groups_ref)
    assert np.all(cols == cols_ref)


def test_isiterable():
    assert afqi.transform.isiterable(range(10))
    assert not afqi.transform.isiterable(5)
    assert afqi.transform.isiterable(np.arange(10))


def test_remove_group():
    x_ref = np.load(op.join(test_data_path, "test_transform_x.npy"))
    label_sets_ref = np.load(
        op.join(test_data_path, "test_multicol2sets_label_sets.npy")
    )

    x_removed = afqi.remove_group(x_ref, ("Callosum Forceps Major",), label_sets_ref)

    x_removed_ref = np.load(op.join(test_data_path, "test_remove_group_x.npy"))

    assert np.all(x_removed == x_removed_ref)


def test_remove_groups():
    x_ref = np.load(op.join(test_data_path, "test_transform_x.npy"))
    label_sets_ref = np.load(
        op.join(test_data_path, "test_multicol2sets_label_sets.npy")
    )

    x_removed = afqi.remove_groups(
        x_ref, [("Callosum Forceps Major",), ("Uncinate",), ("fa",)], label_sets_ref
    )

    x_removed_ref = np.load(op.join(test_data_path, "test_remove_groups_x.npy"))

    assert np.all(x_removed == x_removed_ref)


def test_select_group():
    x_ref = np.load(op.join(test_data_path, "test_transform_x.npy"))
    label_sets_ref = np.load(
        op.join(test_data_path, "test_multicol2sets_label_sets.npy")
    )

    x_select = afqi.select_group(x_ref, ("Callosum Forceps Major",), label_sets_ref)

    x_select_ref = np.load(op.join(test_data_path, "test_select_group_x.npy"))

    assert np.all(x_select == x_select_ref)


def test_select_groups():
    x_ref = np.load(op.join(test_data_path, "test_transform_x.npy"))
    label_sets_ref = np.load(
        op.join(test_data_path, "test_multicol2sets_label_sets.npy")
    )

    x_select = afqi.select_groups(
        x_ref, [("Callosum Forceps Major",), ("Uncinate",), ("fa",)], label_sets_ref
    )

    x_select_ref = np.load(op.join(test_data_path, "test_select_groups_x.npy"))

    assert np.all(x_select == x_select_ref)


def test_shuffle_group():
    x_ref = np.load(op.join(test_data_path, "test_transform_x.npy"))
    label_sets_ref = np.load(
        op.join(test_data_path, "test_multicol2sets_label_sets.npy")
    )

    x_shuffle = afqi.shuffle_group(
        x_ref, ("Corticospinal",), label_sets_ref, random_seed=42
    )

    x_shuffle_ref = np.load(op.join(test_data_path, "test_shuffle_group_x.npy"))

    assert np.all(x_shuffle == x_shuffle_ref)


def test_multicol2sets():
    cols = pd.read_pickle(op.join(test_data_path, "test_transform_cols.pkl"))

    label_sets = afqi.multicol2sets(cols)
    label_sets_ref = np.load(
        op.join(test_data_path, "test_multicol2sets_label_sets.npy")
    )

    assert np.all(label_sets == label_sets_ref)
