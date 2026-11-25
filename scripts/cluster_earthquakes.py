import numpy as np
import pandas as pd

from paths import TABLES_DIR


class KMeans:
    """Implement K-means clustering using NumPy."""

    def __init__(self, k=6, max_iters=100, tol=1e-4, random_state=42):
        self.k = k
        self.max_iters = max_iters
        self.tol = tol
        self.random_state = random_state
        self.centroids = None

    def fit(self, X):
        """Find cluster centers and assign training points to clusters."""
        X = np.asarray(X, dtype=float)

        if X.ndim != 2 or X.shape[1] == 0 or not np.isfinite(X).all():
            raise ValueError("X must be a two-dimensional array of finite numbers.")

        # Sample distinct coordinate vectors so the initial centroids do not repeat.
        unique_points = np.unique(X, axis=0)
        if not 1 <= self.k <= len(unique_points):
            raise ValueError("k must be between 1 and the number of unique points.")

        rng = np.random.default_rng(self.random_state)
        indices = rng.choice(len(unique_points), size=self.k, replace=False)
        self.centroids = unique_points[indices].copy()

        for _ in range(self.max_iters):
            labels = self.predict(X)
            old_centroids = self.centroids
            new_centroids = old_centroids.copy()

            # Empty clusters keep their previous centroid.
            for group in range(self.k):
                cluster = X[labels == group]
                if len(cluster) > 0:
                    new_centroids[group] = cluster.mean(axis=0)

            # Check centroid changes using only the absolute tolerance.
            self.centroids = new_centroids
            if np.allclose(old_centroids, self.centroids, atol=self.tol, rtol=0):
                break

        # Recompute labels after the final centroid update.
        self.labels = self.predict(X)
        self.clusters = [X[self.labels == group] for group in range(self.k)]
        return self

    def predict(self, X):
        """Return the closest cluster index for each input point."""
        if self.centroids is None:
            raise ValueError("Call fit() before predict().")

        X = np.asarray(X, dtype=float)
        distances = np.empty((len(X), self.k))

        # Squared distances preserve the nearest-centroid ordering without square roots.
        for group in range(self.k):
            difference = X - self.centroids[group]
            distances[:, group] = np.sum(difference ** 2, axis=1)

        return np.argmin(distances, axis=1)


def to_sphere(longitude, latitude):
    """Convert longitude and latitude in degrees to unit-sphere coordinates."""
    lon = np.radians(longitude)
    lat = np.radians(latitude)

    x = np.cos(lat) * np.cos(lon)
    y = np.cos(lat) * np.sin(lon)
    z = np.sin(lat)
    return np.column_stack([x, y, z])


def main():
    earthquakes = pd.read_csv(TABLES_DIR / "earthquake_only.csv")

    longitude = pd.to_numeric(earthquakes["Longitude"], errors="coerce")
    latitude = pd.to_numeric(earthquakes["Latitude"], errors="coerce")
    valid = longitude.between(-180, 180) & latitude.between(-90, 90)

    # Spherical coordinates keep points on either side of the date line close together.
    X = to_sphere(longitude.loc[valid], latitude.loc[valid])
    model = KMeans(k=6, max_iters=100, tol=1e-4, random_state=42)
    model.fit(X)

    # Keep rows with invalid coordinates and leave their cluster labels empty.
    earthquakes["Cluster"] = pd.Series(
        pd.NA, index=earthquakes.index, dtype="Int64"
    )
    earthquakes.loc[valid, "Cluster"] = model.labels

    print("Earthquake counts by cluster:")
    print(earthquakes["Cluster"].value_counts(dropna=False).sort_index())

    annual_counts = (
        earthquakes.groupby(["year", "Cluster"])
        .size()
        .unstack(fill_value=0)
    )
    print("\nAnnual counts by cluster, 2010 to 2012:")
    print(annual_counts.loc[2010:2012])

    output_file = TABLES_DIR / "earthquake_kmeans.csv"
    earthquakes.to_csv(output_file, index=False)
    print(f"\nSaved: {output_file}")


if __name__ == "__main__":
    main()
