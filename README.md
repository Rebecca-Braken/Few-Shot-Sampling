# Few-Shot-Sampling
This repository contains the implementation of the sampling-procedure used in ["An Evaluation of Link Prediction Approaches in Few-Shot Scenarios"](https://doi.org/10.3390/electronics12102296) published at MDPI 2023.
From a given relational data set, the code creates a subset with a predefined number of triples.
The subset is initialized with a random node and is iteratively increased by adding random triples involving at least one entity from the subset.
This procedure was used to generate few-shot datasets, on which the performance of different link-prediction approaches was evaluated.
