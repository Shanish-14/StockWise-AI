
# StockWise AI
# Supplier Delay Prediction – V2 Evaluation Report

## 1. Project Overview

The Supplier Delay Prediction module is Feature 3 of StockWise AI, an intelligent grocery inventory management system.

The purpose of this module is to predict whether a supplier order is likely to arrive later than its promised delivery date.

Early identification of potential supplier delays can help grocery stores:

- Prepare for possible stock shortages.
- Plan inventory replenishment.
- Identify suppliers with frequent delivery problems.
- Make better purchasing decisions.

The model performs binary classification:

- 0 = On Time
- 1 = Delayed

## 2. Dataset Description

Version 2 uses a simulated supplier-order dataset.

Dataset file:

`data/raw/supplier_delay/supplier_orders_v2.csv`

Dataset details:

- Total records: 20,000
- Suppliers: 30
- Product categories: 7
- Features: 16 columns
- Date range: 2023–2025
- Missing values: 0
- Duplicate records: 0

Target distribution:

| Class | Records | Percentage |
|---|---:|---:|
| Delayed | 10,690 | 53.45% |
| On Time | 9,310 | 46.55% |

**Important:** This dataset is synthetically generated. It does not contain actual supplier delivery records. Its patterns are based on simulation assumptions.

## 3. Model Features

The following features are used for prediction:

1. Supplier ID
2. Product category
3. Order quantity
4. Delivery distance
5. Supplier reliability
6. Capacity utilization
7. Promised delivery days
8. Historical supplier delay rate
9. Order day of week
10. Order month

Future delivery information, including actual delivery date and actual delivery days, is excluded from prediction to prevent data leakage.

Historical delay rate is calculated using previous supplier orders only.

## 4. Data Splitting Strategy

A chronological split is used to simulate predicting future orders using past information.

| Dataset | Records | Percentage |
|---|---:|---:|
| Training | 14,000 | 70% |
| Validation | 3,000 | 15% |
| Final Test | 3,000 | 15% |

The final test dataset was kept separate during model selection and threshold tuning.

## 5. Model Comparison

Three classification algorithms were evaluated:

- Logistic Regression
- Random Forest
- Extra Trees

Validation results at threshold 0.50:

| Model | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Logistic Regression | 0.6303 | 0.6692 | 0.6720 | 0.6706 |
| Random Forest | 0.6277 | 0.6632 | 0.6810 | 0.6720 |
| Extra Trees | 0.6247 | 0.6675 | 0.6571 | 0.6623 |

Logistic Regression was selected as the candidate model because it achieved the highest validation ROC AUC (0.6771).

## 6. Threshold Optimization

Different classification thresholds were evaluated using validation data.

The F1-maximizing threshold was 0.35.

However, this threshold produced a high number of false warnings.

A separate business-oriented threshold analysis was performed using a provisional minimum recall requirement of 80%.

The highest tested threshold satisfying this requirement was 0.43.

### Business threshold results

| Metric | Result |
|---|---:|
| Selected threshold | 0.43 |
| Accuracy | 62.93% |
| Precision | 63.10% |
| Recall | 81.43% |
| F1 Score | 71.10% |
| True Positives | 1,368 |
| False Positives | 800 |
| False Negatives | 312 |
| True Negatives | 520 |

This threshold represents a trade-off between detecting delayed orders and reducing unnecessary warnings.

The 80% recall requirement is a provisional design assumption, not a confirmed business requirement.

## 7. Final Test Evaluation

The final test dataset was evaluated once using the previously selected threshold of 0.35.

Final test results:

| Metric | Result |
|---|---:|
| Threshold | 0.35 |
| Accuracy | 55.97% |
| Precision | 54.66% |
| Recall | 94.86% |
| F1 Score | 69.36% |
| ROC AUC | 65.46% |
| PR AUC | 66.67% |

Confusion matrix:

| | Predicted On Time | Predicted Delayed |
|---|---:|---:|
| Actual On Time | 184 | 1,240 |
| Actual Delayed | 81 | 1,495 |

The model detected most delayed orders but generated many false warnings.

For comparison, a simple baseline that predicts every order as delayed achieves approximately 68.88% F1 on this test dataset.

The model's F1 improvement over that baseline is only approximately 0.48 percentage points.

Therefore, the model currently provides limited predictive improvement.

## 8. Error Analysis

Validation error analysis identified the following issues:

- A large number of on-time orders were incorrectly classified as delayed.
- At threshold 0.35, 1,083 of 1,320 actual on-time orders received false delay warnings.
- Supplier-level false alarms varied considerably.
- Historical supplier delay rate showed a useful increasing relationship with actual delay frequency in the simulated data.
- No single product category explained all classification errors.

These findings suggest that additional improvements are necessary.

## 9. Limitations

The current implementation has several limitations:

1. The dataset is synthetically generated.
2. The simulation assumptions may not represent real supplier behaviour.
3. The model produces too many false-positive warnings.
4. Predictive performance is only slightly better than the always-delayed baseline in F1 score.
5. The model has not been validated using real-world supplier data.
6. The provisional business threshold has not been tested against actual operational costs.

The current model should be considered an experimental prototype, not a production-ready supplier risk system.

## 10. Future Improvements

Potential improvements include:

- Testing with real supplier delivery records.
- Improving historical supplier performance features.
- Collecting more informative operational variables.
- Evaluating cost-sensitive classification.
- Exploring calibrated probabilities.
- Comparing additional classification algorithms.
- Predicting the expected number of delay days.
- Developing supplier performance dashboards.

## 11. Conclusion

Supplier Delay Prediction V2 establishes an initial machine-learning pipeline for identifying potentially delayed grocery supplier orders.

The project includes dataset generation, data validation, chronological splitting, model comparison, threshold experiments, final test evaluation, and error analysis.

Although the model demonstrates high recall at the selected test threshold, it also produces a high number of false warnings and has limited improvement over a simple baseline.

Further development and validation using real-world data are required before operational use.

---

**Project:** StockWise AI  
**Module:** Supplier Delay Prediction  
**Version:** V2  
**Status:** Experimental – Evaluation Completed
