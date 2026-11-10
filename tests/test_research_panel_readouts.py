import numpy as np
from sklearn.cluster import KMeans

from atomic_research.datasets import DiscoveryScaler
from atomic_research.replicated_panels import predict_linear_rule
from scripts.run_research_panel_readouts import exact_centroid_rule


def test_rule_matches_centroid_in_original_units_with_missing_and_unused_features():
    rng = np.random.default_rng(17)
    train = rng.normal(size=(60, 8)) * np.arange(1, 9) + np.arange(8) * 10
    train[0, 2] = np.nan
    panel = np.array([1, 2, 5, 7])
    scaler = DiscoveryScaler().fit(train)
    model = KMeans(n_clusters=2, n_init=5, random_state=17).fit(scaler.transform(train)[:, panel])
    rule = exact_centroid_rule(model.cluster_centers_, panel, scaler, 8)
    query = rng.normal(size=(40, 8)) * np.arange(1, 9) + np.arange(8) * 10
    query[1, 5] = np.inf
    predicted = model.predict(scaler.transform(query)[:, panel])
    np.testing.assert_array_equal(predict_linear_rule(rule, query), predicted)
    query[:, [0, 3, 4, 6]] = 1e200
    np.testing.assert_array_equal(predict_linear_rule(rule, query), predicted)
